"""Verify the running Part 4.2 API against a real recorded Yahoo snapshot and pandas."""
import json
import time
import urllib.request
import urllib.error
from pathlib import Path
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
BASE='http://127.0.0.1:8000/api/strategy'


def api(path,body=None):
    request=urllib.request.Request(BASE+path,data=json.dumps(body).encode() if body is not None else None,
                                  headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(request,timeout=30) as response:
        return json.load(response)


dataset=api('/history/sample',{})
parameters={'short':5,'long':20,'initial_cash':10000,'fee':1,'slippage_bps':5}
run=api('/backtests',{'dataset_id':dataset['id'],**parameters})
reopened=api('/backtests/'+run['id'])
assert run==reopened
result=run['result']
closes=pd.Series([b['close'] for b in dataset['bars']])
fast,slow=closes.rolling(5).mean(),closes.rolling(20).mean()
errors=[]
for i,point in enumerate(result['indicators']):
    for key,reference in (('fast',fast),('slow',slow)):
        if pd.notna(reference[i]): errors.append(abs(reference[i]-point[key]))
    expected='buy' if fast[i]>slow[i] and fast.shift()[i]<=slow.shift()[i] else 'sell' if fast[i]<slow[i] and fast.shift()[i]>=slow.shift()[i] else None
    assert point['signal']==expected
for fill in result['fills']:
    order=next(o for o in result['orders'] if o['id']==fill['order_id'])
    assert fill['time']>order['signal_time']
a=result['account']
assert abs(a['equity']-a['cash']-a['market_value'])<1e-8
assert abs(a['total_pnl']-a['realized_pnl']-a['unrealized_pnl'])<1e-8
try:
    api('/backtests',{'dataset_id':dataset['id'],**parameters,'short':20,'long':5})
    raise AssertionError('Invalid windows accepted')
except urllib.error.HTTPError as error:
    assert error.code==422
report={'verified_at':time.time(),'dataset_id':dataset['id'],'source':dataset['source'],'fetched_at':dataset['fetched_at'],
        'bars':len(dataset['bars']),'run_id':run['id'],'pandas_version':pd.__version__,'max_sma_absolute_error':max(errors),
        'all_crossovers_match_pandas':True,'persisted_run_reopened_identically':True,'every_fill_after_signal_bar':True,
        'accounting_identities_pass':True,'invalid_windows_http_status':422,'parameters':parameters,'account':a,
        'fills':result['fills'],'orders':result['orders'],'max_drawdown_pct':result['max_drawdown_pct']}
path=ROOT/'docs/assignment4-part2-evidence/api-verification.json'
path.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:report[k] for k in ('dataset_id','bars','max_sma_absolute_error','account','max_drawdown_pct')},indent=2))
