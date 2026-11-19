from __future__ import annotations

import hashlib
import json
import math
import sqlite3
import time
from contextlib import contextmanager
from pathlib import Path

SOURCE = "Yahoo Finance WebSocket"
SYMBOLS = ("AAPL", "MSFT", "BTC-USD")


class MarketStore:
    def __init__(self, path: Path):
        self.path = path

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.path, timeout=10)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys=ON")
        try:
            with db:
                yield db
        finally:
            db.close()

    def initialize(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.executescript("""
            PRAGMA journal_mode=WAL;
            CREATE TABLE IF NOT EXISTS observations (
                id INTEGER PRIMARY KEY, identity TEXT NOT NULL, revision INTEGER NOT NULL,
                symbol TEXT NOT NULL, source TEXT NOT NULL, source_time REAL NOT NULL,
                received_at REAL NOT NULL, price REAL NOT NULL, day_volume INTEGER,
                fingerprint TEXT NOT NULL, payload TEXT NOT NULL,
                UNIQUE(identity, revision));
            CREATE INDEX IF NOT EXISTS observation_time ON observations(symbol, source_time);
            CREATE TABLE IF NOT EXISTS receipts (
                id INTEGER PRIMARY KEY, observation_id INTEGER NOT NULL REFERENCES observations(id),
                received_at REAL NOT NULL, disposition TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS candle_events (
                id INTEGER PRIMARY KEY, symbol TEXT NOT NULL, time INTEGER NOT NULL,
                revision INTEGER NOT NULL, received_at REAL NOT NULL,
                reason TEXT NOT NULL, candle TEXT NOT NULL, UNIQUE(symbol,time,revision));
            CREATE INDEX IF NOT EXISTS candle_time ON candle_events(symbol,time,id);
            """)
            if db.execute("PRAGMA user_version").fetchone()[0] < 1:
                db.execute("PRAGMA user_version=1")

    @staticmethod
    def normalize(message, received_at):
        symbol = message.get("id")
        if symbol not in SYMBOLS:
            raise ValueError("Unsupported symbol")
        source_time = float(message["time"]) / 1000
        price = float(message["price"])
        if not all(math.isfinite(x) and x > 0 for x in (source_time, price)):
            raise ValueError("Invalid price or timestamp")
        if source_time > received_at + 300:
            raise ValueError("Source timestamp too far in the future")
        volume = message.get("day_volume")
        volume = int(volume) if volume is not None else None
        if volume is not None and volume < 0:
            raise ValueError("Negative volume")
        return symbol, source_time, price, volume

    def ingest(self, message, received_at=None):
        received_at = time.time() if received_at is None else received_at
        symbol, source_time, price, volume = self.normalize(message, received_at)
        identity = f"yahoo:{symbol}:{int(message['time'])}"
        payload = json.dumps(message, sort_keys=True, separators=(",", ":"))
        fingerprint = hashlib.sha256(payload.encode()).hexdigest()
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            previous = db.execute("SELECT * FROM observations WHERE identity=? ORDER BY revision DESC LIMIT 1", (identity,)).fetchone()
            if previous and previous["fingerprint"] == fingerprint:
                db.execute("INSERT INTO receipts(observation_id,received_at,disposition) VALUES(?,?,?)", (previous["id"], received_at, "duplicate"))
                return {"disposition": "duplicate", "observation_id": previous["id"], "events": []}
            latest_time = db.execute("SELECT MAX(source_time) FROM observations WHERE symbol=?", (symbol,)).fetchone()[0]
            disposition = "revision" if previous else ("out_of_order" if latest_time is not None and source_time < latest_time else "new")
            revision = previous["revision"] + 1 if previous else 1
            cursor = db.execute("""INSERT INTO observations(identity,revision,symbol,source,source_time,received_at,price,day_volume,fingerprint,payload)
                VALUES(?,?,?,?,?,?,?,?,?,?)""", (identity,revision,symbol,SOURCE,source_time,received_at,price,volume,fingerprint,payload))
            db.execute("INSERT INTO receipts(observation_id,received_at,disposition) VALUES(?,?,?)", (cursor.lastrowid,received_at,disposition))
            # Late observations and volume-baseline changes can affect a later candle too.
            events = self._rebuild(db, symbol, received_at, disposition)
            return {"disposition": disposition, "observation_id": cursor.lastrowid, "events": events}

    def _rebuild(self, db, symbol, now, reason):
        rows = db.execute("""SELECT o.* FROM observations o JOIN
            (SELECT identity,MAX(revision) revision FROM observations WHERE symbol=? GROUP BY identity) latest
            ON o.identity=latest.identity AND o.revision=latest.revision ORDER BY source_time,id""", (symbol,)).fetchall()
        bars = {}
        previous = None
        previous_time = None
        for row in rows:
            bucket = int(row["source_time"] // 60) * 60
            price = row["price"]
            bar = bars.setdefault(bucket, {"time":bucket,"open":price,"high":price,"low":price,"close":price,
                "volume":0,"volume_known":False,"source_time":row["source_time"],"source":SOURCE,
                "complete":bucket + 60 <= now,"observations":0})
            bar.update(high=max(bar["high"],price),low=min(bar["low"],price),close=price,
                source_time=row["source_time"],observations=bar["observations"]+1)
            # day_volume is cumulative, not a per-tick size. First value is only a baseline.
            # UTC day change / decreasing counter starts another baseline; do not invent volume.
            volume = row["day_volume"]
            if volume is not None and previous is not None and int(row["source_time"]//86400)==int(previous_time//86400) and volume >= previous:
                bar["volume"] += volume - previous
                bar["volume_known"] = True
            if volume is not None:
                previous, previous_time = volume, row["source_time"]
        events = []
        for bucket, bar in bars.items():
            old = db.execute("SELECT * FROM candle_events WHERE symbol=? AND time=? ORDER BY id DESC LIMIT 1", (symbol,bucket)).fetchone()
            encoded = json.dumps(bar,sort_keys=True)
            if old and old["candle"] == encoded:
                continue
            revision = old["revision"]+1 if old else 1
            cursor = db.execute("INSERT INTO candle_events(symbol,time,revision,received_at,reason,candle) VALUES(?,?,?,?,?,?)", (symbol,bucket,revision,now,reason,encoded))
            events.append({"id":cursor.lastrowid,"symbol":symbol,"revision":revision,"received_at":now,"reason":reason,"candle":bar})
        return events

    def finalize(self, now=None):
        now = time.time() if now is None else now
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            # Only rebuild symbols with unfinished bars whose intervals have now ended.
            symbols = db.execute("""SELECT DISTINCT e.symbol FROM candle_events e WHERE e.id IN
                (SELECT MAX(id) FROM candle_events GROUP BY symbol,time) AND e.time+60<=?
                AND json_extract(e.candle,'$.complete')=0""", (now,)).fetchall()
            return [event for row in symbols for event in self._rebuild(db,row[0],now,"interval_closed")]

    def snapshot(self, symbol, limit=300):
        with self.connect() as db:
            rows = db.execute("""SELECT * FROM candle_events WHERE id IN
                (SELECT MAX(id) FROM candle_events WHERE symbol=? GROUP BY time) ORDER BY time DESC LIMIT ?""", (symbol,limit)).fetchall()
            return [self.event(row) for row in reversed(rows)]

    @staticmethod
    def event(row):
        event = dict(row)
        event["candle"] = json.loads(event["candle"])
        return event

    def events(self, symbol, after=0, through=None, limit=500):
        through = self.highwater() if through is None else through
        with self.connect() as db:
            return [self.event(row) for row in db.execute("SELECT * FROM candle_events WHERE symbol=? AND id>? AND id<=? ORDER BY id LIMIT ?", (symbol,after,through,limit))]

    def highwater(self):
        with self.connect() as db:
            return db.execute("SELECT COALESCE(MAX(id),0) FROM candle_events").fetchone()[0]

    def stats(self, symbol):
        with self.connect() as db:
            row = db.execute("SELECT COUNT(*) revisions,COUNT(DISTINCT identity) identities,MAX(source_time) source_time,MAX(received_at) received_at FROM observations WHERE symbol=?", (symbol,)).fetchone()
            receipts = db.execute("SELECT disposition,COUNT(*) n FROM receipts r JOIN observations o ON o.id=r.observation_id WHERE symbol=? GROUP BY disposition", (symbol,)).fetchall()
            return {**dict(row),"receipts":{r[0]:r[1] for r in receipts},"highwater":self.highwater()}
