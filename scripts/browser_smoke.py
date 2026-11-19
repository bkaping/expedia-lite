"""CI browser regression using runner-provided ChromeDriver, Python stdlib only.

Runs in GitHub Actions, not against the user's desktop. Start FastAPI, Vite and
ChromeDriver (port 9515) first. Source network is disabled; the included real
Yahoo historical snapshot is explicitly loaded via the UI.
"""
import base64
import json
import time
import urllib.request
import urllib.error
from pathlib import Path

DRIVER='http://127.0.0.1:9515'
ROOT=Path(__file__).resolve().parents[1]


def request(method,path,body=None):
    raw=json.dumps(body).encode() if body is not None else None
    req=urllib.request.Request(DRIVER+path,data=raw,method=method,headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(req,timeout=20) as response:
        return json.load(response)['value']


def wait(action,seconds=30):
    end=time.time()+seconds
    while time.time()<end:
        try:
            value=action()
            if value: return value
        except (urllib.error.URLError,KeyError,AssertionError): pass
        time.sleep(.25)
    raise AssertionError('Browser condition timed out')


wait(lambda:request('GET','/status'))
created=request('POST','/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'args':['--headless=new','--window-size=1440,1100','--disable-dev-shm-usage']}}}})
session=created['sessionId']
base='/session/'+session


def find(selector):
    value=request('POST',base+'/element',{'using':'css selector','value':selector})
    return next(iter(value.values()))


def click(selector):
    element=wait(lambda:find(selector))
    request('POST',base+'/element/'+element+'/click',{})


def text(selector):
    return request('GET',base+'/element/'+find(selector)+'/text')


try:
    request('POST',base+'/url',{'url':'http://127.0.0.1:5173/'})
    wait(lambda:'Market overview' in text('h1'))
    click('[data-testid="historical-mode"]')
    click('[data-testid="load-sample"]')
    wait(lambda:'161 hourly bars' in text('[data-testid="dataset-provenance"]'))
    click('[data-testid="run-backtest"]')
    wait(lambda:'9 fills' in text('.equity-heading'))
    assert '-3.84%' in text('[data-testid="account-summary"]')
    assert 'BUY' in text('[data-testid="orders-table"]')
    assert 'SELL' in text('[data-testid="orders-table"]')
    assert 'SMA 5' in text('[data-testid="indicator-summary"]')
    assert 'SMA 20' in text('[data-testid="indicator-summary"]')
    for selector,value in (('[data-testid="short-window"]','20'),('[data-testid="long-window"]','5')):
        element=find(selector)
        request('POST',base+'/element/'+element+'/clear',{})
        request('POST',base+'/element/'+element+'/value',{'text':value+'\ue004'})
    click('[data-testid="run-backtest"]')
    wait(lambda:'Check strategy settings' in text('[role="alert"]'))
    request('POST',base+'/refresh',{})
    wait(lambda:'Market overview' in text('h1'))
    click('[data-testid="start-paper"]')
    wait(lambda:'PAPER STRATEGY ACTIVE' in text('.strategy-panel .bar-state'))
    click('[data-testid="stop-paper"]')
    wait(lambda:'PAPER STRATEGY STOPPED' in text('.strategy-panel .bar-state'))
    png=request('GET',base+'/screenshot')
    Path('/tmp/strategy-browser.png').write_bytes(base64.b64decode(png))
    print('Browser PASS: real recorded dataset, SMA overlays/readout, backtest/account/fills, invalid windows, paper start/stop.')
finally:
    request('DELETE',base)
