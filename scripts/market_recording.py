"""Export public Yahoo observations or import them into an empty local replay database.

Usage:
  .venv/bin/python scripts/market_recording.py export backend/data/market.db docs/assignment4-evidence/yahoo-observations.jsonl
  MARKET_DB_PATH=backend/data/replay.db MARKET_FEED_ENABLED=0 .venv/bin/uvicorn app.main:app --app-dir backend
  (Import BEFORE starting the backend; it will finalize old incomplete intervals at startup.)
"""
import argparse
import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'backend'))
from app.market.store import MarketStore

parser=argparse.ArgumentParser()
parser.add_argument('action',choices=['export','import'])
parser.add_argument('database',type=Path)
parser.add_argument('recording',type=Path)
args=parser.parse_args()
store=MarketStore(args.database)
store.initialize()
if args.action=='export':
    with store.connect() as db:
        rows=db.execute('''SELECT o.payload,r.received_at FROM receipts r JOIN observations o ON o.id=r.observation_id ORDER BY r.id''').fetchall()
    args.recording.write_text(''.join(json.dumps(dict(row))+'\n' for row in rows))
    print(f'Exported {len(rows)} original receipts; public Yahoo data, no generated prices.')
else:
    if store.highwater():
        parser.error('Import requires an empty market database')
    count=0
    for line in args.recording.read_text().splitlines():
        row=json.loads(line)
        # Close earlier intervals at this receipt time, not at the present wall clock.
        store.finalize(row['received_at'])
        store.ingest(json.loads(row['payload']),row['received_at'])
        count+=1
    print(f'Imported {count} recorded receipts. Replay labels remain recorded, never live.')
