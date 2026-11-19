"""Read real local-server data; verify WebSocket, persistence, replay, and failure path.
Run while FastAPI is running: .venv/bin/python scripts/verify_market_live.py
No generated source data and no credentials are used.
"""
import asyncio
import json
import sqlite3
import time
import urllib.request
from pathlib import Path
from websockets.asyncio.client import connect

ROOT=Path(__file__).resolve().parents[1]
BASE='http://127.0.0.1:8000/api/market'


def control(enabled):
    request=urllib.request.Request(BASE+'/feed',data=json.dumps({'enabled':enabled}).encode(),headers={'Content-Type':'application/json'},method='POST')
    with urllib.request.urlopen(request,timeout=5) as response:
        return json.load(response)


async def verify():
    evidence={'checked_at_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'source':'real Yahoo Finance WebSocket, not mocked'}
    async with connect('ws://127.0.0.1:8000/api/market/ws?symbol=BTC-USD') as ws:
        frame=json.loads(await asyncio.wait_for(ws.recv(),10))
        assert frame['events'], 'No live observations recorded; retry after Yahoo supplies data'
        assert frame['feed']['state']=='live', frame['feed']
        event=frame['events'][-1]
        with sqlite3.connect(ROOT/'backend/data/market.db') as db:
            stored=json.loads(db.execute('SELECT candle FROM candle_events WHERE id=?',(event['id'],)).fetchone()[0])
            assert stored==event['candle'], 'Browser WebSocket candle differs from committed SQLite record'
        evidence['live']={'event_id':event['id'],'candle':event['candle'],'feed':frame['feed'],'sqlite_equals_socket':True}
        try:
            control(False)
            for _ in range(6):
                unavailable=json.loads(await asyncio.wait_for(ws.recv(),5))
                if unavailable['feed']['state']=='unavailable': break
            assert unavailable['feed']['state']=='unavailable'
            assert unavailable['events'], 'Failure erased saved candles'
            evidence['unavailable']={'state':unavailable['feed']['state'],'saved_candles_retained':len(unavailable['events'])}
            replay={}
            async with connect('ws://127.0.0.1:8000/api/market/ws?symbol=BTC-USD&mode=replay&speed=50') as playback:
                start=json.loads(await playback.recv())
                assert start['type']=='replay_start'
                count=0
                while True:
                    message=json.loads(await asyncio.wait_for(playback.recv(),10))
                    if message['type']=='replay_done': break
                    e=message['event']; assert e['id']<=start['through']
                    replay[e['time']]=e; count+=1
            with sqlite3.connect(ROOT/'backend/data/market.db') as db:
                rows=db.execute('''SELECT candle FROM candle_events WHERE id IN
                    (SELECT MAX(id) FROM candle_events WHERE symbol='BTC-USD' AND id<=? GROUP BY time) ORDER BY time''',(start['through'],)).fetchall()
            assert [json.loads(row[0]) for row in rows]==[replay[t]['candle'] for t in sorted(replay)]
            evidence['replay']={'events_played':count,'through':start['through'],'final_state_equals_sqlite_at_boundary':True}
        finally:
            control(True)
    path=ROOT/'docs/assignment4-evidence/live-verification.json'
    path.write_text(json.dumps(evidence,indent=2)+'\n')
    print(json.dumps(evidence,indent=2))

asyncio.run(verify())
