from __future__ import annotations

import asyncio
import os
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from ..config import DATA_DIR
from .feed import YahooFeed
from .store import MarketStore, SYMBOLS

store = MarketStore(Path(os.getenv("MARKET_DB_PATH", DATA_DIR / "market.db")))
feed = YahooFeed(store, os.getenv("MARKET_FEED_ENABLED", "1") != "0")
router = APIRouter(prefix="/api/market")


def check_symbol(symbol):
    if symbol not in SYMBOLS:
        raise HTTPException(422,"Choose AAPL, MSFT, or BTC-USD")


@router.get("/candles")
def candles(symbol: str = "AAPL"):
    check_symbol(symbol)
    return {"symbol":symbol,"events":store.snapshot(symbol),"feed":feed.status(symbol)}


@router.get("/observations")
def observations(symbol: str = "AAPL", after: int = Query(0,ge=0), limit: int = Query(100,ge=1,le=500)):
    check_symbol(symbol)
    with store.connect() as db:
        rows = db.execute("SELECT * FROM observations WHERE symbol=? AND id>? ORDER BY id LIMIT ?",(symbol,after,limit)).fetchall()
        return {"observations":[dict(row) for row in rows],"stats":store.stats(symbol)}


@router.get("/events")
def events(symbol: str = "AAPL", after: int = Query(0,ge=0), through: int | None = Query(None,ge=0), limit: int = Query(500,ge=1,le=1000)):
    check_symbol(symbol)
    end = store.highwater() if through is None else min(through, store.highwater())
    rows = store.events(symbol,after,end,limit)
    return {"events":rows,"through":end,"next":rows[-1]["id"] if rows else after}


class FeedControl(BaseModel):
    enabled: bool


@router.post("/feed")
def control_feed(control: FeedControl):
    feed.enabled = control.enabled
    return {"enabled":feed.enabled}


@router.websocket("/ws")
async def market_socket(ws: WebSocket, symbol: str = "AAPL", mode: str = "live", speed: int = 10):
    await ws.accept()
    if symbol not in SYMBOLS or mode not in ("live","replay") or not 1 <= speed <= 50:
        await ws.close(code=1008)
        return
    try:
        if mode == "replay":
            # Capture the boundary once. New live events cannot leak into this replay.
            through, cursor = store.highwater(), 0
            await ws.send_json({"type":"replay_start","through":through})
            while True:
                batch = store.events(symbol,cursor,through,100)
                if not batch:
                    break
                for event in batch:
                    await ws.send_json({"type":"replay_event","event":event})
                    cursor = event["id"]
                    await asyncio.sleep(1/speed)
            await ws.send_json({"type":"replay_done","through":through})
            await ws.close()
        else:
            while True:
                await ws.send_json({"type":"snapshot","symbol":symbol,"events":store.snapshot(symbol),"feed":feed.status(symbol)})
                await asyncio.sleep(1)
    except (WebSocketDisconnect, RuntimeError):
        return


async def finalize_candles():
    while True:
        await asyncio.sleep(1)
        store.finalize()
