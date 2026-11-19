"""Causal SMA crossover strategy and a Decimal, long-only simulated ledger."""
from __future__ import annotations

import copy
import math
from collections import deque
from decimal import Decimal, ROUND_DOWN


def windows(short, long):
    if not 2 <= short < long <= 100:
        raise ValueError('Use 2 ≤ short SMA < long SMA ≤ 100')


def crossover(previous, fast, slow):
    if previous is None or fast is None or slow is None:
        return None
    delta = fast-slow
    delta = 0 if math.isclose(fast,slow,rel_tol=1e-12,abs_tol=1e-10) else delta
    if previous <= 0 and delta > 0:
        return 'buy'
    if previous >= 0 and delta < 0:
        return 'sell'
    return None


class IncrementalSMA:
    def __init__(self, short=5, long=20):
        windows(short,long)
        self.short, self.long = short,long
        self.values = deque()
        self.fast_total = Decimal(0)
        self.slow_total = Decimal(0)
        self.previous = None

    def push(self, close):
        value=Decimal(str(close))
        if not value.is_finite() or value <= 0:
            raise ValueError('Close must be positive and finite')
        self.values.append(value)
        self.fast_total += value
        self.slow_total += value
        if len(self.values)>self.short:
            self.fast_total -= self.values[-self.short-1]
        if len(self.values)>self.long:
            self.slow_total -= self.values.popleft()
        fast=float(self.fast_total/self.short) if len(self.values)>=self.short else None
        slow=float(self.slow_total/self.long) if len(self.values)>=self.long else None
        signal=crossover(self.previous,fast,slow)
        if slow is not None:
            self.previous=0 if math.isclose(fast,slow,rel_tol=1e-12,abs_tol=1e-10) else fast-slow
        return {'fast':fast,'slow':slow,'signal':signal}

    def preview(self, close):
        return copy.deepcopy(self).push(close)


def batch_indicators(closes, short=5, long=20):
    """Independent batch implementation for reference/verification."""
    windows(short,long)
    points=[]
    previous=None
    for i in range(len(closes)):
        fast=math.fsum(closes[i-short+1:i+1])/short if i+1>=short else None
        slow=math.fsum(closes[i-long+1:i+1])/long if i+1>=long else None
        points.append({'fast':fast,'slow':slow,'signal':crossover(previous,fast,slow)})
        if slow is not None:
            previous=0 if math.isclose(fast,slow,rel_tol=1e-12,abs_tol=1e-10) else fast-slow
    return points


def indicator_series(bars, short=5, long=20):
    engine=IncrementalSMA(short,long)
    result=[]
    for bar in bars:
        point=engine.push(bar['close']) if bar['complete'] else engine.preview(bar['close'])
        result.append({'time':bar['time'],**point,'provisional':not bar['complete']})
    return result


def decimal(value):
    return Decimal(str(value))


class Ledger:
    """Fractional units, no leverage/shorts. Fees included in entry cost basis."""
    def __init__(self, initial_cash=10000, fee=1, slippage_bps=5):
        self.initial_cash=decimal(initial_cash)
        self.fee=decimal(fee)
        self.slippage=decimal(slippage_bps)/10000
        if not all(x.is_finite() for x in (self.initial_cash,self.fee,self.slippage)) or self.initial_cash<=0 or self.fee<0 or not 0<=self.slippage<=Decimal('.01'):
            raise ValueError('Invalid account assumptions')
        self.cash=self.initial_cash
        self.quantity=Decimal(0)
        self.cost_basis=Decimal(0)
        self.realized=Decimal(0)
        self.fees=Decimal(0)
        self.fills=[]

    def fill(self, side, raw_price, timestamp, order_id):
        raw_price=decimal(raw_price)
        if not raw_price.is_finite() or raw_price<=0:
            raise ValueError('Fill price must be positive and finite')
        if side not in ('buy','sell'):
            raise ValueError('Invalid side')
        price=(raw_price*(1+self.slippage if side=='buy' else 1-self.slippage)).quantize(Decimal('.00000001'))
        if side=='buy':
            if self.quantity or self.cash<=self.fee:
                return None
            quantity=((self.cash-self.fee)/price).quantize(Decimal('.000001'),rounding=ROUND_DOWN)
            if quantity<=0:
                return None
            total=quantity*price+self.fee
            self.cash-=total
            self.quantity=quantity
            self.cost_basis=total
            realized=Decimal(0)
        else:
            if not self.quantity or self.quantity*price<self.fee:
                return None
            quantity=self.quantity
            proceeds=quantity*price-self.fee
            realized=proceeds-self.cost_basis
            self.realized+=realized
            self.cash+=proceeds
            self.quantity=Decimal(0)
            self.cost_basis=Decimal(0)
        self.fees+=self.fee
        fill={'order_id':order_id,'time':timestamp,'side':side,'quantity':float(quantity),'price':float(price),
              'fee':float(self.fee),'realized_pnl':float(realized),'cash_after':float(self.cash)}
        self.fills.append(fill)
        return fill

    def mark(self, price):
        market_value=self.quantity*decimal(price)
        equity=self.cash+market_value
        return {'initial_cash':float(self.initial_cash),'cash':float(self.cash),'quantity':float(self.quantity),
                'cost_basis':float(self.cost_basis),'market_value':float(market_value),
                'realized_pnl':float(self.realized),'unrealized_pnl':float(market_value-self.cost_basis),
                'equity':float(equity),'total_pnl':float(equity-self.initial_cash),'fees_paid':float(self.fees),
                'return_pct':float((equity/self.initial_cash-1)*100)}

    def dump(self):
        return {key:str(value) for key,value in vars(self).items() if isinstance(value,Decimal)} | {'fills':self.fills}

    @classmethod
    def restore(cls, state):
        ledger=cls()
        for key,value in state.items():
            setattr(ledger,key,decimal(value) if key!='fills' else value)
        return ledger


class Simulation:
    def __init__(self, short=5, long=20, initial_cash=10000, fee=1, slippage_bps=5):
        self.indicator=IncrementalSMA(short,long)
        self.ledger=Ledger(initial_cash,fee,slippage_bps)
        self.orders=[]
        self.points=[]
        self.timeline=[]
        self.pending=None
        self.last_closed=-1
        self.last_mark=0
        self.peak=float(initial_cash)
        self.max_drawdown=0

    def next_open(self, bar, known_at=None):
        if self.pending is None or bar['time']<=self.pending['signal_time']:
            return
        # Live paper fills use only a quote observed after the signal was known.
        if known_at is not None and known_at<self.pending['known_at']:
            return
        order=self.pending
        price=bar['open'] if known_at is None else bar['close']
        executed_at=bar['time'] if known_at is None else bar['source_time']
        fill=self.ledger.fill(order['side'],price,executed_at,order['id'])
        order.update(status='filled' if fill else 'skipped',fill_time=executed_at if fill else None,
                     reason=('Next available bar open' if known_at is None else 'First eligible next-interval quote received after signal') if fill else 'Position/cash constraints')
        self.pending=None
        self.last_mark=price

    def close_bar(self, bar, known_at=None, trade=True):
        if not bar['complete'] or bar['time']<=self.last_closed:
            return None
        point={'time':bar['time'],**self.indicator.push(bar['close']),'provisional':False}
        self.points.append(point)
        self.last_closed=bar['time']
        self.last_mark=bar['close']
        if trade and point['signal']:
            order={'id':len(self.orders)+1,'signal_time':bar['time'],'known_at':known_at if known_at is not None else bar['time']+3600,
                   'side':point['signal'],'status':'pending','fill_time':None,'reason':'Waiting for next available bar open'}
            self.orders.append(order)
            self.pending=order
        account=self.ledger.mark(bar['close'])
        self.peak=max(self.peak,account['equity'])
        drawdown=(self.peak-account['equity'])/self.peak*100
        self.max_drawdown=max(self.max_drawdown,drawdown)
        self.timeline.append({'time':bar['time'],'equity':account['equity'],'drawdown_pct':drawdown})
        return point

    def result(self):
        return {'account':self.ledger.mark(self.last_mark),'orders':self.orders,'fills':self.ledger.fills,
                'indicators':self.points,'equity_curve':self.timeline,'max_drawdown_pct':self.max_drawdown,
                'closed_trades':sum(fill['side']=='sell' for fill in self.ledger.fills)}

    def dump(self):
        return {'short':self.indicator.short,'long':self.indicator.long,'values':[str(v) for v in self.indicator.values],
                'ledger':self.ledger.dump(),'orders':self.orders,'points':self.points,'timeline':self.timeline,
                'pending_id':self.pending['id'] if self.pending else None,'last_closed':self.last_closed,
                'last_mark':self.last_mark,'peak':self.peak,'max_drawdown':self.max_drawdown}

    @classmethod
    def restore(cls,state):
        sim=cls(state['short'],state['long'])
        for value in state['values']:
            sim.indicator.push(value)
        sim.ledger=Ledger.restore(state['ledger'])
        for key in ('orders','last_closed','last_mark','peak','max_drawdown'):
            setattr(sim,key,state[key])
        sim.points=state['points']; sim.timeline=state['timeline']
        sim.pending=next((o for o in sim.orders if o['id']==state['pending_id']),None)
        # Rebuilding a long-window deque establishes the last SMA relation; no historical trade is replayed.
        return sim


def backtest(bars, short=5, long=20, initial_cash=10000, fee=1, slippage_bps=5):
    sim=Simulation(short,long,initial_cash,fee,slippage_bps)
    previous=-1
    for bar in bars:
        if bar['time']<=previous:
            raise ValueError('Backtest bars must have unique, increasing timestamps')
        previous=bar['time']
        if not bar['complete']:
            continue
        # A decision from an earlier close can execute before this bar's close is examined.
        sim.next_open(bar)
        sim.close_bar(bar)
    return sim.result()
