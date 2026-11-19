"""Persisted historical datasets, immutable backtests, and forward-only paper accounts."""
from __future__ import annotations

import hashlib
import json
import math
import os
import time
import uuid
from pathlib import Path

from .strategy import Simulation, backtest, indicator_series

SAMPLE_PATH=Path(__file__).resolve().parents[3]/'docs/assignment4-part2-evidence/yahoo-hourly-sample.json'


def validate_bars(bars):
    previous=-1
    for bar in bars:
        if type(bar['time']) is not int or bar['time']<=previous:
            raise ValueError('Historical timestamps must be unique and increasing')
        previous=bar['time']
        prices=[float(bar[key]) for key in ('open','high','low','close')]
        if not all(math.isfinite(p) and p>0 for p in prices):
            raise ValueError('Invalid historical OHLC')
        if bar['low']>min(bar['open'],bar['close']) or bar['high']<max(bar['open'],bar['close']) or bar['low']>bar['high']:
            raise ValueError('Inconsistent historical OHLC')
        if bar.get('volume') is not None and (not math.isfinite(bar['volume']) or bar['volume']<0):
            raise ValueError('Invalid historical volume')
        if type(bar.get('complete')) is not bool:
            raise ValueError('Historical completion flag required')
    if not bars:
        raise ValueError('No historical bars returned')


class SimulationStore:
    def __init__(self, market):
        self.market=market

    def initialize(self):
        with self.market.connect() as db:
            db.executescript('''
            CREATE TABLE IF NOT EXISTS historical_datasets (
                id TEXT PRIMARY KEY, symbol TEXT NOT NULL, interval TEXT NOT NULL,
                source TEXT NOT NULL, fetched_at REAL NOT NULL, payload TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS backtest_runs (
                id TEXT PRIMARY KEY, dataset_id TEXT NOT NULL REFERENCES historical_datasets(id),
                created_at REAL NOT NULL, parameters TEXT NOT NULL, result TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS paper_accounts (
                id TEXT PRIMARY KEY, symbol TEXT NOT NULL, created_at REAL NOT NULL,
                active INTEGER NOT NULL, cursor INTEGER NOT NULL, state TEXT NOT NULL);
            PRAGMA user_version=2;
            ''')

    def save_dataset(self, dataset):
        validate_bars(dataset['bars'])
        if dataset['interval']!='1h':
            raise ValueError('Only 1-hour historical datasets are supported')
        if any(b['time']-a['time']<3600 for a,b in zip(dataset['bars'],dataset['bars'][1:])):
            raise ValueError('Historical hourly intervals must not overlap')
        if any(not bar['complete'] or bar['time']+3600>dataset['fetched_at'] for bar in dataset['bars']):
            raise ValueError('Dataset includes an unfinished interval')
        content=json.dumps({k:dataset[k] for k in ('symbol','interval','source','bars')},sort_keys=True,separators=(',',':'))
        identifier=hashlib.sha256(content.encode()).hexdigest()
        dataset={**dataset,'id':identifier}
        with self.market.connect() as db:
            db.execute('INSERT OR IGNORE INTO historical_datasets VALUES(?,?,?,?,?,?)',
                       (identifier,dataset['symbol'],dataset['interval'],dataset['source'],dataset['fetched_at'],json.dumps(dataset)))
        return self.dataset(identifier)

    def dataset(self, identifier):
        with self.market.connect() as db:
            row=db.execute('SELECT payload FROM historical_datasets WHERE id=?',(identifier,)).fetchone()
        if not row:
            raise KeyError('Historical dataset not found')
        return json.loads(row[0])

    def datasets(self, symbol):
        with self.market.connect() as db:
            rows=db.execute('SELECT id,symbol,interval,source,fetched_at,payload FROM historical_datasets WHERE symbol=? ORDER BY fetched_at DESC LIMIT 20',(symbol,)).fetchall()
        return [{k:row[k] for k in ('id','symbol','interval','source','fetched_at')} | {'bars_count':len(json.loads(row['payload'])['bars'])} for row in rows]

    def fetch_history(self,symbol):
        import yfinance as yf
        # Cache is local app data, never a credential or tracked artifact.
        yf.set_tz_cache_location(str(self.market.path.parent/'yfinance-cache'))
        frame=yf.Ticker(symbol).history(period='1mo',interval='1h',auto_adjust=False,actions=False,prepost=False,raise_errors=True,timeout=20)
        fetched=time.time()
        bars=[]
        for timestamp,row in frame.iterrows():
            start=int(timestamp.timestamp())
            if start+3600>fetched:
                continue
            values={key:float(row[key.title()]) for key in ('open','high','low','close')}
            bars.append({'time':start,**values,'volume':int(row['Volume']),'volume_known':True,'complete':True,
                         'source':'Yahoo Finance historical OHLCV','source_time':start+3600})
        return self.save_dataset({'symbol':symbol,'interval':'1h','source':'Yahoo Finance via yfinance.history; unadjusted regular-session OHLCV',
                                  'fetched_at':fetched,'bars':bars})

    def run_backtest(self,dataset_id,parameters):
        dataset=self.dataset(dataset_id)
        if len(dataset['bars'])<=parameters['long']:
            raise ValueError('Dataset needs more bars than the long SMA window')
        result=backtest(dataset['bars'],**parameters)
        run={'id':uuid.uuid4().hex,'dataset_id':dataset_id,'symbol':dataset['symbol'],'created_at':time.time(),
             'parameters':parameters,'result':result}
        with self.market.connect() as db:
            db.execute('INSERT INTO backtest_runs VALUES(?,?,?,?,?)',(run['id'],dataset_id,run['created_at'],json.dumps(parameters),json.dumps(result)))
        return run

    def run(self,identifier):
        with self.market.connect() as db:
            row=db.execute('SELECT r.*,d.symbol FROM backtest_runs r JOIN historical_datasets d ON d.id=r.dataset_id WHERE r.id=?',(identifier,)).fetchone()
        if not row:
            raise KeyError('Backtest not found')
        return {k:row[k] for k in ('id','dataset_id','symbol','created_at')} | {'parameters':json.loads(row['parameters']),'result':json.loads(row['result'])}

    def runs(self,symbol):
        with self.market.connect() as db:
            return [dict(row) for row in db.execute('''SELECT r.id,r.dataset_id,r.created_at,r.parameters FROM backtest_runs r JOIN historical_datasets d ON d.id=r.dataset_id WHERE d.symbol=? ORDER BY r.created_at DESC LIMIT 20''',(symbol,))]

    def start_paper(self,symbol,parameters):
        sim=Simulation(**parameters)
        identifier=uuid.uuid4().hex
        with self.market.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            if db.execute('SELECT 1 FROM paper_accounts WHERE symbol=? AND active=1',(symbol,)).fetchone():
                raise ValueError('Stop the active paper strategy before starting a new account')
            # Seed closed history and capture cursor within one transaction; no historical orders.
            rows=db.execute('''SELECT candle FROM candle_events WHERE id IN
                (SELECT MAX(id) FROM candle_events WHERE symbol=? GROUP BY time) ORDER BY time DESC LIMIT 300''',(symbol,)).fetchall()
            for row in reversed(rows):
                bar=json.loads(row['candle'])
                sim.close_bar(bar,trade=False)
            sim.timeline=[]
            sim.points=[]
            cursor=db.execute('SELECT COALESCE(MAX(id),0) FROM candle_events').fetchone()[0]
            db.execute('INSERT INTO paper_accounts VALUES(?,?,?,?,?,?)',(identifier,symbol,time.time(),1,cursor,json.dumps(sim.dump())))
        return self.paper(identifier)

    def paper(self,identifier):
        with self.market.connect() as db:
            row=db.execute('SELECT * FROM paper_accounts WHERE id=?',(identifier,)).fetchone()
        if not row:
            raise KeyError('Paper account not found')
        sim=Simulation.restore(json.loads(row['state']))
        parameters={'short':sim.indicator.short,'long':sim.indicator.long,'initial_cash':float(sim.ledger.initial_cash),
                    'fee':float(sim.ledger.fee),'slippage_bps':float(sim.ledger.slippage*10000)}
        return {k:row[k] for k in ('id','symbol','created_at','active','cursor')} | {'result':sim.result(),'parameters':parameters,'short':sim.indicator.short,'long':sim.indicator.long}

    def latest_paper(self,symbol):
        with self.market.connect() as db:
            row=db.execute('SELECT id FROM paper_accounts WHERE symbol=? ORDER BY created_at DESC LIMIT 1',(symbol,)).fetchone()
        return self.paper(row[0]) if row else None

    def stop_paper(self,identifier):
        with self.market.connect() as db:
            row=db.execute('SELECT state FROM paper_accounts WHERE id=?',(identifier,)).fetchone()
            if not row:
                raise KeyError('Paper account not found')
            sim=Simulation.restore(json.loads(row['state']))
            if sim.pending:
                sim.pending.update(status='cancelled',reason='Paper strategy stopped; no simulated fill')
                sim.pending=None
            db.execute('UPDATE paper_accounts SET active=0,state=? WHERE id=?',(json.dumps(sim.dump()),identifier))
        return self.paper(identifier)

    def advance_paper(self):
        with self.market.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            accounts=db.execute('SELECT * FROM paper_accounts WHERE active=1').fetchall()
            for account in accounts:
                sim=Simulation.restore(json.loads(account['state']))
                events=db.execute('SELECT * FROM candle_events WHERE symbol=? AND id>? ORDER BY id LIMIT 1000',(account['symbol'],account['cursor'])).fetchall()
                for event in events:
                    bar=json.loads(event['candle'])
                    # Older closed-bar corrections never rewrite executed decisions or account history.
                    if bar['time']<=sim.last_closed:
                        continue
                    if event['reason']!='interval_closed':
                        sim.next_open(bar,event['received_at'])
                        sim.last_mark=bar['close']
                    sim.close_bar(bar,event['received_at'])
                if events:
                    db.execute('UPDATE paper_accounts SET cursor=?,state=? WHERE id=?',(events[-1]['id'],json.dumps(sim.dump()),account['id']))
