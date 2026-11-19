from __future__ import annotations

import asyncio
import contextlib
import os
import time
import certifi

from .store import SYMBOLS


class YahooFeed:
    def __init__(self, store, enabled=True):
        self.store = store
        self.enabled = enabled
        self.transport = "starting"
        self.detail = "Waiting for Yahoo Finance"
        self.last_message = 0
        self.last_by_symbol = {}
        self.task = None

    async def run(self):
        while True:
            if not self.enabled:
                self.transport, self.detail = "unavailable", "Live feed deliberately disconnected for failure demonstration"
                await asyncio.sleep(1)
                continue
            try:
                # Python.org macOS installs may lack a default CA bundle. Keep TLS verification on.
                os.environ.setdefault("SSL_CERT_FILE", certifi.where())
                from yfinance import AsyncWebSocket
                self.transport, self.detail = "connecting", "Opening Yahoo WebSocket"
                async with AsyncWebSocket(verbose=False) as stream:
                    await stream.subscribe(list(SYMBOLS))
                    self.transport, self.detail = "connected", "Subscribed; waiting for valid observations"
                    started = time.time()

                    async def receive(message):
                        if not self.enabled:
                            return
                        try:
                            result = self.store.ingest(message)
                        except (ValueError, KeyError, TypeError, OverflowError):
                            self.detail = "Ignored an invalid source message"
                            return
                        # A receipt establishes transport activity, not source freshness.
                        self.last_message = time.time()
                        self.last_by_symbol[message["id"]] = self.last_message
                        self.detail = "Yahoo observations received and committed to SQLite"
                        self.transport = "connected"

                    listener = asyncio.create_task(stream.listen(receive))
                    try:
                        while self.enabled and not listener.done():
                            await asyncio.sleep(1)
                            if time.time() - max(started, self.last_message) > 45:
                                raise TimeoutError("No Yahoo observations for 45 seconds")
                        if listener.done():
                            listener.result()
                            raise ConnectionError("Yahoo listener stopped")
                    finally:
                        listener.cancel()
                        with contextlib.suppress(asyncio.CancelledError):
                            await listener
            except asyncio.CancelledError:
                raise
            except Exception as error:
                self.transport = "unavailable"
                # Only error class; exceptions may contain private machine/network information.
                self.detail = f"Yahoo feed unavailable ({type(error).__name__}); retrying in 5 seconds"
                await asyncio.sleep(5)

    def status(self, symbol):
        stats = self.store.stats(symbol)
        now = time.time()
        age = max(0,now-stats["source_time"]) if stats["source_time"] else None
        receipt = self.last_by_symbol.get(symbol)
        status = self.transport
        if not self.enabled:
            status = "unavailable"
        elif status == "connected":
            status = "live" if receipt and now-receipt <= 30 and age is not None and age <= 30 else "stale"
        return {"state":status,"transport":self.transport,"detail":self.detail,"source":"Yahoo Finance WebSocket",
                "source_age_seconds":age,"last_live_receipt":receipt,"server_time":now,"stats":stats}
