from __future__ import annotations

import copy
import json
import random
import sys
import tempfile
import unittest
from pathlib import Path

import pandas as pd

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from app.market.store import MarketStore
from app.market.strategy import IncrementalSMA, Ledger, Simulation, backtest, batch_indicators, indicator_series
from app.market.simulation import SimulationStore, validate_bars
from app.market.strategy_routes import Parameters


def bars(closes):
    return [{'time':1800000000+i*3600,'open':p+0.25,'high':p+1,'low':p-0.5,'close':p,'volume':100,
             'complete':True,'source_time':1800003600+i*3600} for i,p in enumerate(closes)]


class IndicatorTests(unittest.TestCase):
    def test_tradingview_published_three_period_example(self):
        engine=IncrementalSMA(2,3)
        actual=[engine.push(p)['slow'] for p in (5,6,7,8,9)]
        self.assertEqual(actual,[None,None,6,7,8])

    def test_batch_incremental_and_pandas_values_and_crossovers(self):
        rng=random.Random(42)
        closes=[100+rng.uniform(-5,5) for _ in range(1200)]
        for short,long in ((2,3),(5,20),(20,100)):
            series=pd.Series(closes)
            fast,slow=series.rolling(short,min_periods=short).mean(),series.rolling(long,min_periods=long).mean()
            up=(fast>slow)&(fast.shift(1)<=slow.shift(1))
            down=(fast<slow)&(fast.shift(1)>=slow.shift(1))
            engine=IncrementalSMA(short,long)
            for i,(value,batch) in enumerate(zip(closes,batch_indicators(closes,short,long))):
                actual=engine.push(value)
                for name,reference in (('fast',fast),('slow',slow)):
                    if pd.isna(reference[i]): self.assertIsNone(actual[name])
                    else:
                        self.assertAlmostEqual(actual[name],reference[i],places=9)
                        self.assertAlmostEqual(batch[name],reference[i],places=9)
                expected='buy' if up[i] else 'sell' if down[i] else None
                self.assertEqual(actual['signal'],expected)
                self.assertEqual(batch['signal'],expected)

    def test_known_crossovers_warmup_and_equality(self):
        points=batch_indicators([3,2,1,2,3,4,3,2,1,2,3],2,3)
        self.assertEqual([(i,p['signal']) for i,p in enumerate(points) if p['signal']],[(4,'buy'),(7,'sell'),(10,'buy')])
        self.assertFalse(any(p['signal'] for p in batch_indicators([10.0]*30)))
        with self.assertRaises(ValueError): IncrementalSMA(20,5)

    def test_unfinished_preview_does_not_advance_confirmed_state(self):
        data=bars([3,2,1,100,2,3])
        data[3]['complete']=False
        points=indicator_series(data,2,3)
        expected=indicator_series([b for b in data if b['complete']],2,3)
        self.assertTrue(points[3]['provisional'])
        self.assertEqual([p for p in points if not p['provisional']],expected)
        self.assertEqual(expected[-1]['signal'],'buy')


class AccountingTests(unittest.TestCase):
    def test_known_roundtrip_with_entry_and_exit_fees(self):
        ledger=Ledger(1000,1,0)
        fill=ledger.fill('buy',100,1,1)
        self.assertEqual(fill['quantity'],9.99)
        self.assertEqual(ledger.mark(110)['unrealized_pnl'],98.9)
        self.assertEqual(ledger.mark(110)['equity'],1098.9)
        ledger.fill('sell',120,2,2)
        account=ledger.mark(120)
        self.assertEqual(account['cash'],1197.8)
        self.assertEqual(account['realized_pnl'],197.8)
        self.assertEqual(account['fees_paid'],2)
        self.assertEqual(account['unrealized_pnl'],0)
        self.assertEqual(account['quantity'],0)

    def test_slippage_constraints_and_accounting_identity(self):
        ledger=Ledger(1000,1,5)
        self.assertIsNone(ledger.fill('sell',100,0,0))
        self.assertEqual(ledger.fill('buy',100,1,1)['price'],100.05)
        self.assertIsNone(ledger.fill('buy',100,2,2))
        account=ledger.mark(97)
        self.assertGreaterEqual(account['cash'],0)
        self.assertAlmostEqual(account['equity'],account['cash']+account['market_value'])
        self.assertAlmostEqual(account['total_pnl'],account['realized_pnl']+account['unrealized_pnl'])
        ledger.fill('sell',100,3,3)
        self.assertEqual(ledger.fills[-1]['price'],99.95)
        self.assertLess(ledger.mark(100)['total_pnl'],0)
        self.assertEqual(Ledger.restore(ledger.dump()).mark(100),ledger.mark(100))

    def test_invalid_and_insufficient_cash(self):
        with self.assertRaises(ValueError): Ledger(float('nan'))
        with self.assertRaises(ValueError): Ledger(slippage_bps=-1)
        ledger=Ledger(1,1,0)
        self.assertIsNone(ledger.fill('buy',100,1,1))
        with self.assertRaises(ValueError): ledger.fill('buy',float('inf'),2,2)


class CausalityTests(unittest.TestCase):
    def setUp(self):
        self.data=bars([3,2,1,2,3,4,3,2,1,2,3,4,3,2,1,2,3])

    def test_execution_uses_next_open_and_leaves_last_signal_pending(self):
        result=backtest(self.data[:11],2,3,1000,0,0)
        self.assertEqual(result['fills'][0]['time'],self.data[5]['time'])
        self.assertEqual(result['fills'][0]['price'],self.data[5]['open'])
        self.assertEqual(result['orders'][-1]['status'],'pending')
        for fill in result['fills']:
            order=next(o for o in result['orders'] if o['id']==fill['order_id'])
            self.assertGreater(fill['time'],order['signal_time'])
        self.assertEqual(result['closed_trades'],1)

    def test_future_changes_cannot_change_earlier_equity_or_signals(self):
        full=backtest(self.data,2,3)
        prefix=backtest(self.data[:9],2,3)
        self.assertEqual(prefix['equity_curve'],full['equity_curve'][:9])
        self.assertEqual(prefix['indicators'],full['indicators'][:9])
        changed=copy.deepcopy(self.data)
        for b in changed[9:]:
            for key in ('open','high','low','close'): b[key]*=10
        changed_result=backtest(changed,2,3)
        self.assertEqual(full['equity_curve'][:9],changed_result['equity_curve'][:9])
        self.assertEqual(full['indicators'][:9],changed_result['indicators'][:9])

    def test_unfinished_outlier_never_trades_or_changes_final_mark(self):
        data=copy.deepcopy(self.data)
        data[-1]['complete']=False
        data[-1]['close']=1e9
        self.assertEqual(backtest(data,2,3),backtest(data[:-1],2,3))

    def test_restart_matches_uninterrupted_incremental_run(self):
        sim=Simulation(2,3)
        for b in self.data[:8]: sim.next_open(b);sim.close_bar(b)
        restarted=Simulation.restore(json.loads(json.dumps(sim.dump())))
        for b in self.data[8:]:
            for engine in (sim,restarted): engine.next_open(b);engine.close_bar(b)
        self.assertEqual(sim.result(),restarted.result())

    def test_live_fill_uses_received_quote_and_not_historical_open(self):
        sim=Simulation(2,3,1000,0,0)
        for b in self.data[:5]: sim.close_bar(b,b['time']+3601)
        next_bar={**self.data[5],'close':9,'source_time':self.data[5]['time']+3}
        sim.next_open(next_bar,known_at=sim.pending['known_at']-1)
        self.assertEqual(sim.ledger.fills,[])
        sim.next_open(next_bar,known_at=sim.pending['known_at']+3)
        self.assertEqual(sim.ledger.fills[0]['price'],9)
        self.assertEqual(sim.ledger.fills[0]['time'],next_bar['source_time'])

    def test_duplicate_unsorted_and_malformed_history_rejected(self):
        with self.assertRaises(ValueError): backtest([self.data[1],self.data[0]])
        bad=copy.deepcopy(self.data);bad[0]['high']=0
        with self.assertRaises(ValueError): validate_bars(bad)
        with self.assertRaises(ValueError): Parameters(short=20,long=5)
        with self.assertRaises(ValueError): Parameters(initial_cash=float('nan'))


class PersistenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.market=MarketStore(Path(self.tmp.name)/'market.db');self.market.initialize()
        self.service=SimulationStore(self.market);self.service.initialize()
        self.dataset=self.service.save_dataset({'symbol':'AAPL','interval':'1h','source':'explicit test fixture',
            'fetched_at':1800100000,'bars':bars([3,2,1,2,3,4,3,2,1,2,3])})
        self.parameters={'short':2,'long':3,'initial_cash':1000,'fee':1,'slippage_bps':5}

    def tearDown(self): self.tmp.cleanup()

    def test_immutable_dataset_and_run_survive_restart(self):
        duplicate=self.service.save_dataset(self.dataset)
        self.assertEqual(duplicate,self.dataset)
        run=self.service.run_backtest(self.dataset['id'],self.parameters)
        reopened=SimulationStore(self.market);reopened.initialize()
        self.market.initialize()
        with self.market.connect() as db:
            self.assertEqual(db.execute('PRAGMA user_version').fetchone()[0],2)
        self.assertEqual(reopened.run(run['id'])['result'],run['result'])
        self.assertEqual(len(reopened.runs('AAPL')),1)
        with self.assertRaises(KeyError): reopened.dataset('missing')

    def test_unfinished_history_rejected_and_empty_backtest_rejected(self):
        bad=copy.deepcopy(self.dataset);bad['bars'][-1]['complete']=False
        with self.assertRaises(ValueError): self.service.save_dataset(bad)
        overlap=copy.deepcopy(self.dataset);overlap['bars'][1]['time']=overlap['bars'][0]['time']+1
        with self.assertRaises(ValueError): self.service.save_dataset(overlap)
        with self.assertRaises(ValueError): self.service.run_backtest(self.dataset['id'],{**self.parameters,'long':20})

    def tick(self,index,price):
        t=1800000000+index*60
        self.market.ingest({'id':'AAPL','time':t*1000,'price':price},t+1)
        self.market.finalize(t+60)

    def test_forward_paper_does_not_trade_seed_history_or_rewrite_corrections(self):
        for i,p in enumerate([3,2,1,2]): self.tick(i,p)
        account=self.service.start_paper('AAPL',self.parameters)
        self.assertEqual(account['result']['fills'],[])
        self.assertEqual(account['parameters'],self.parameters)
        self.assertEqual(account['result']['equity_curve'],[])
        with self.assertRaises(ValueError): self.service.start_paper('AAPL',self.parameters)
        self.tick(4,3);self.service.advance_paper()
        paper=self.service.paper(account['id'])
        self.assertEqual(paper['result']['orders'][0]['side'],'buy')
        self.tick(5,4);self.service.advance_paper()
        paper=self.service.paper(account['id'])
        self.assertEqual(len(paper['result']['fills']),1)
        old_equity=paper['result']['account']['equity']
        quote_time=1800000000+6*60
        self.market.ingest({'id':'AAPL','time':quote_time*1000,'price':5},quote_time+1)
        self.service.advance_paper()
        paper=self.service.paper(account['id'])
        self.assertGreater(paper['result']['account']['equity'],old_equity)
        saved=copy.deepcopy(paper['result'])
        self.market.ingest({'id':'AAPL','time':1800000000*1000,'price':300},quote_time+2)
        self.service.advance_paper()
        self.assertEqual(self.service.paper(account['id'])['result'],saved)
        self.service.advance_paper()
        self.assertEqual(len(self.service.paper(account['id'])['result']['fills']),1)
        stopped=self.service.stop_paper(account['id'])
        self.assertEqual(stopped['active'],0)
        self.assertEqual(self.service.latest_paper('AAPL')['id'],account['id'])

    def test_paper_pending_order_cancelled_when_stopped(self):
        for i,p in enumerate([3,2,1,2]): self.tick(i,p)
        account=self.service.start_paper('AAPL',self.parameters)
        self.tick(4,3);self.service.advance_paper()
        stopped=self.service.stop_paper(account['id'])
        self.assertEqual(stopped['result']['orders'][-1]['status'],'cancelled')

if __name__=='__main__': unittest.main()
