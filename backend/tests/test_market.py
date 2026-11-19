from __future__ import annotations
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.market.store import MarketStore
from app.market.feed import YahooFeed


class MarketTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.store = MarketStore(Path(self.tmp.name)/'market.db')
        self.store.initialize()
        self.t = 1800000000  # exact UTC minute

    def tearDown(self):
        self.tmp.cleanup()

    def tick(self, offset=0, price=100, volume=1000, received=None):
        msg={'id':'AAPL','time':(self.t+offset)*1000,'price':price}
        if volume is not None: msg['day_volume']=volume
        return self.store.ingest(msg,self.t+offset+1 if received is None else received)

    def bars(self):
        return [e['candle'] for e in self.store.snapshot('AAPL')]

    def test_duplicate_receipts_do_not_change_volume_or_candles(self):
        self.tick()
        result=self.tick(received=self.t+2)
        self.assertEqual(result['disposition'],'duplicate')
        self.assertEqual(result['events'],[])
        self.assertEqual(self.store.stats('AAPL')['revisions'],1)
        self.assertEqual(self.store.stats('AAPL')['receipts'],{'new':1,'duplicate':1})

    def test_revisions_preserve_original_and_replace_aggregate(self):
        self.tick()
        self.tick(10,105,1010)
        changed=self.tick(10,102,1008,received=self.t+12)
        self.assertEqual(changed['disposition'],'revision')
        self.assertEqual(self.bars()[0]['high'],102)
        self.assertEqual(self.bars()[0]['volume'],8)
        with self.store.connect() as db:
            self.assertEqual(db.execute('SELECT COUNT(*) FROM observations').fetchone()[0],3)

    def test_out_of_order_uses_source_order_for_open_close(self):
        self.tick(30,110,1030)
        self.tick(50,108,1050)
        late=self.tick(10,99,1010,received=self.t+55)
        self.assertEqual(late['disposition'],'out_of_order')
        bar=self.bars()[0]
        self.assertEqual((bar['open'],bar['high'],bar['low'],bar['close'],bar['volume']),(99,110,99,108,40))

    def test_late_previous_candle_updates_next_volume_baseline(self):
        self.tick(10,100,1000)
        self.tick(70,102,1040)
        self.tick(50,101,1030,received=self.t+80)
        self.assertEqual([b['volume'] for b in self.bars()],[30,10])
        self.assertTrue(self.bars()[0]['complete'])
        self.assertFalse(self.bars()[1]['complete'])

    def test_completion_is_persisted_without_another_tick(self):
        self.tick()
        self.assertFalse(self.bars()[0]['complete'])
        self.assertEqual(self.store.finalize(self.t+60)[0]['reason'],'interval_closed')
        self.assertTrue(self.bars()[0]['complete'])
        self.assertEqual(self.store.finalize(self.t+61),[])

    def test_late_revision_keeps_interval_closed(self):
        self.tick()
        self.store.finalize(self.t+60)
        self.tick(5,102,1005,received=self.t+120)
        self.assertTrue(self.bars()[0]['complete'])
        self.assertEqual(self.bars()[0]['close'],102)

    def test_missing_volume_and_counter_reset_are_not_invented(self):
        self.tick(volume=None)
        self.assertFalse(self.bars()[0]['volume_known'])
        self.tick(5,100,1000)
        self.assertFalse(self.bars()[0]['volume_known'])
        self.tick(10,100,5)
        self.assertEqual(self.bars()[0]['volume'],0)
        self.tick(15,100,8)
        self.assertEqual(self.bars()[0]['volume'],3)
        next_day = (self.t//86400+1)*86400
        self.tick(next_day-self.t,100,5000)
        self.assertFalse(self.bars()[-1]['volume_known'])

    def test_replay_prefix_has_no_future_revision_and_boundary_is_fixed(self):
        self.tick()
        through=self.store.highwater()
        self.tick(5,120,1010)
        self.store.finalize(self.t+60)
        initial=self.store.events('AAPL',through=through)
        self.assertEqual(initial[0]['candle']['close'],100)
        self.assertFalse(initial[0]['candle']['complete'])
        self.tick(70,110,1020)
        self.tick(30,95,1011,received=self.t+80)
        state={}
        cursor=0
        while batch:=self.store.events('AAPL',after=cursor,limit=1):
            for event in batch: state[event['time']]=event; cursor=event['id']
        self.assertEqual(list(state.values()),self.store.snapshot('AAPL'))

    def test_restart_preserves_identity_and_event_history(self):
        self.tick()
        restarted=MarketStore(self.store.path)
        restarted.initialize()
        self.assertEqual(restarted.snapshot('AAPL'),self.store.snapshot('AAPL'))
        self.assertEqual(restarted.ingest({'id':'AAPL','time':self.t*1000,'price':100,'day_volume':1000},self.t+2)['disposition'],'duplicate')

    def test_invalid_observation_does_not_write(self):
        for msg in ({'id':'BAD','time':self.t*1000,'price':100}, {'id':'AAPL','time':self.t*1000,'price':float('nan')}, {'id':'AAPL','time':self.t*1000,'price':-1}, {'id':'AAPL','time':(self.t+1000)*1000,'price':100}):
            with self.assertRaises(ValueError): self.store.ingest(msg,self.t)
        self.assertEqual(self.store.stats('AAPL')['revisions'],0)

    def test_unavailable_and_stale_are_distinct_from_connected(self):
        self.tick()
        feed=YahooFeed(self.store,enabled=False)
        self.assertEqual(feed.status('AAPL')['state'],'unavailable')
        feed.enabled=True
        feed.transport='connected'
        self.assertEqual(feed.status('AAPL')['state'],'stale')
        self.assertIsNone(feed.status('AAPL')['last_live_receipt'])

if __name__=='__main__': unittest.main()
