import { createApp, ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { createChart, CandlestickSeries, HistogramSeries, LineSeries, createSeriesMarkers, ColorType } from 'lightweight-charts'
import './market.css'
import { indicators } from './indicators.js'
import StrategyPanel from './strategy-panel.js'

createApp({
  components: { StrategyPanel },
  setup() {
    const symbol = ref('AAPL'), mode = ref('live'), connection = ref('connecting')
    const feed = ref(null), bars = ref([]), replayState = ref(''), replayCount = ref(0)
    const strategyWindows=ref({short:5,long:20}), historicalMeta=ref(null)
    const indicatorPoints=computed(()=>indicators(bars.value.map(e=>e.candle),strategyWindows.value.short,strategyWindows.value.long))
    const latestIndicator=computed(()=>indicatorPoints.value.at(-1))
    const lastSignal=computed(()=>[...indicatorPoints.value].reverse().find(point=>point.signal))
    const clock = ref(Date.now()/1000), error = ref(''), events = ref([]), chartEl = ref(null)
    let socket, retry, ticker, chart, candles, volume, fastLine, slowLine, markers, generation = 0, fitted = false
    const latest = computed(() => bars.value.at(-1))
    const age = computed(() => {
      const source = mode.value !== 'live' ? latest.value?.candle.source_time : feed.value?.stats.source_time
      return source ? Math.max(0, Math.floor(clock.value-source)) : null
    })
    const ageText = computed(() => age.value == null ? 'No observations' : age.value < 60 ? `${age.value}s old` : `${Math.floor(age.value/60)}m ${age.value%60}s old`)
    const status = computed(() => mode.value === 'backtest' ? 'historical' : mode.value === 'replay' ? 'replay' : connection.value !== 'connected' ? 'backend offline' : feed.value?.state || 'connecting')
    const price = value => value == null ? '—' : new Intl.NumberFormat('en-US',{minimumFractionDigits:2,maximumFractionDigits:2}).format(value)
    const date = value => value ? new Date(value*1000).toLocaleTimeString('en-US',{hour12:false,timeZone:'UTC'})+' UTC' : '—'
    const paint = () => {
      const sorted = [...bars.value].sort((a,b)=>a.candle.time-b.candle.time).slice(-300)
      bars.value = sorted
      candles.setData(sorted.map(e=>({time:e.candle.time,open:e.candle.open,high:e.candle.high,low:e.candle.low,close:e.candle.close})))
      volume.setData(sorted.map(e=>({time:e.candle.time,value:e.candle.volume_known ? e.candle.volume : 0,color:e.candle.close>=e.candle.open?'#2c9b9977':'#df7f7977'})))
      const points=indicators(sorted.map(e=>e.candle),strategyWindows.value.short,strategyWindows.value.long)
      fastLine.setData(points.filter(p=>p.fast!=null).map(p=>({time:p.time,value:p.fast})))
      slowLine.setData(points.filter(p=>p.slow!=null).map(p=>({time:p.time,value:p.slow})))
      markers.setMarkers(points.filter(p=>p.signal).map(p=>({time:p.time,position:p.signal==='buy'?'belowBar':'aboveBar',shape:p.signal==='buy'?'arrowUp':'arrowDown',color:p.provisional?'#8b9baa':p.signal==='buy'?'#91dfbf':'#f2aa98',text:(p.provisional?'Preview ':'')+p.signal.toUpperCase()})))
      if (!fitted && sorted.length) { chart.timeScale().fitContent(); fitted = true }
    }
    const connect = (preserve = false) => {
      generation += 1
      const current = generation
      clearTimeout(retry)
      socket?.close()
      if(mode.value==='backtest') {connection.value='recorded history';bars.value=[];historicalMeta.value=null;feed.value=null;fitted=false;paint();return}
      if (preserve !== true) {
        bars.value=[]; events.value=[]; feed.value=null; fitted=false; paint()
      }
      error.value=''; replayCount.value=0; replayState.value='Starting recorded event playback'
      connection.value='connecting'
      const api = import.meta.env.VITE_API_BASE_URL || location.origin
      const url = new URL('/api/market/ws',api)
      url.protocol = url.protocol === 'https:' ? 'wss:' : 'ws:'
      url.search = new URLSearchParams({symbol:symbol.value,mode:mode.value,speed:'10'})
      socket = new WebSocket(url)
      socket.onopen = () => { if(current===generation) { connection.value='connected'; error.value='' } }
      socket.onmessage = message => {
        if(current!==generation) return
        const data = JSON.parse(message.data)
        if(data.type==='snapshot') {
          feed.value=data.feed; bars.value=data.events; events.value=data.events.slice(-5).reverse(); paint()
        } else if(data.type==='replay_event') {
          const event=data.event
          bars.value=[...bars.value.filter(e=>e.candle.time!==event.candle.time),event]
          events.value=[event,...events.value].slice(0,5); replayCount.value++; paint()
          replayState.value=`Playing saved revisions · event #${event.id}`
        } else if(data.type==='replay_done') {
          replayState.value=replayCount.value ? 'Replay complete · captured boundary #'+data.through : 'No recorded observations for this instrument. Return to live to record data.'
        }
      }
      socket.onclose=()=>{
        if(current!==generation) return
        connection.value='disconnected'
        if(mode.value==='live') { error.value='Backend connection lost. Retrying in 3 seconds.'; retry=setTimeout(()=>connect(true),3000) }
      }
      socket.onerror=()=> { if(current===generation) error.value='WebSocket connection unavailable' }
    }
    const switchMode = value => { mode.value=value; connect() }
    const showHistorical = dataset => {historicalMeta.value=dataset;bars.value=dataset.bars.map((candle,i)=>({id:i+1,candle,revision:1,received_at:dataset.fetched_at}));fitted=false;paint()}
    const applySettings = settings => {strategyWindows.value=settings;paint()}
    const toggleFeed = async () => {
      try {
        const response=await fetch(`${import.meta.env.VITE_API_BASE_URL || ''}/api/market/feed`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({enabled:feed.value?.state==='unavailable'})})
        if(!response.ok) throw new Error('Feed control failed')
        error.value=''
      } catch(e) { error.value=e.message }
    }
    onMounted(()=>{
      chart=createChart(chartEl.value,{autoSize:true,height:440,layout:{background:{type:ColorType.Solid,color:'#101c28'},textColor:'#8495a8',attributionLogo:true},grid:{vertLines:{color:'#1a2937'},horzLines:{color:'#1a2937'}},rightPriceScale:{borderColor:'#283746'},timeScale:{timeVisible:true,secondsVisible:false,borderColor:'#283746'},localization:{locale:'en-US'}})
      candles=chart.addSeries(CandlestickSeries,{upColor:'#51c0b0',downColor:'#ed9188',wickUpColor:'#51c0b0',wickDownColor:'#ed9188',borderVisible:false})
      fastLine=chart.addSeries(LineSeries,{color:'#f4c777',lineWidth:2,lastValueVisible:false,priceLineVisible:false})
      slowLine=chart.addSeries(LineSeries,{color:'#91a8f2',lineWidth:2,lastValueVisible:false,priceLineVisible:false})
      markers=createSeriesMarkers(candles,[])
      candles.priceScale().applyOptions({scaleMargins:{top:0.12,bottom:0.30}})
      volume=chart.addSeries(HistogramSeries,{priceFormat:{type:'volume'},priceScaleId:''})
      volume.priceScale().applyOptions({scaleMargins:{top:0.78,bottom:0}})
      ticker=setInterval(()=>clock.value=Date.now()/1000,1000); connect()
    })
    onBeforeUnmount(()=>{generation++;clearTimeout(retry);clearInterval(ticker);socket?.close();chart?.remove()})
    return {symbol,mode,connection,feed,bars,latest,ageText,status,price,date,chartEl,connect,switchMode,toggleFeed,replayState,replayCount,error,events,strategyWindows,latestIndicator,lastSignal,historicalMeta,showHistorical,applySettings}
  },
  template: `
  <div class="workstation">
    <aside class="rail"><a class="brand" href="/" aria-label="Market workstation">m<span>•</span></a><span class="rail-line"></span><span class="rail-active" aria-label="Dashboard">▥</span><span class="rail-bottom">4.2</span></aside>
    <main>
      <header><div><div class="eyebrow">LOCAL MARKET WORKSTATION</div><h1>Market overview<span class="title-dot">.</span></h1></div><div class="course-label">COURSEWORK PROTOTYPE <span>All trading is simulated</span></div></header>
      <nav class="toolbar" aria-label="Chart controls"><div class="instrument"><label for="symbol">INSTRUMENT</label><select id="symbol" v-model="symbol" @change="connect"><option>AAPL</option><option>MSFT</option><option>BTC-USD</option></select><span class="interval">{{mode==='backtest'?'1 hour · historical':'1 minute'}}</span></div><div class="segmented"><button :class="{selected:mode==='live'}" @click="switchMode('live')" :aria-pressed="mode==='live'">Live feed</button><button :class="{selected:mode==='replay'}" @click="switchMode('replay')" :aria-pressed="mode==='replay'">Recorded replay</button><button data-testid="historical-mode" :class="{selected:mode==='backtest'}" @click="switchMode('backtest')" :aria-pressed="mode==='backtest'">Historical backtest</button></div></nav>
      <section class="metrics" aria-label="Market summary"><div><span>LAST OBSERVED PRICE</span><strong>{{price(latest?.candle.close)}} <small>USD</small></strong></div><div><span>SOURCE DATA AGE</span><strong class="smaller">{{ageText}}</strong></div><div><span>FEED STATUS</span><strong class="smaller status" :class="status"><i></i>{{status}}</strong></div><div><span>{{mode==='backtest'?'HISTORICAL BARS':mode==='replay'?'REPLAYED REVISIONS':'PERSISTED IDENTITIES'}}</span><strong>{{mode==='backtest'?bars.length:mode==='replay'?replayCount:(feed?.stats.identities ?? '—')}}<small> / SQLite</small></strong></div></section>
      <div v-if="error && mode==='live'" role="alert" class="notice">{{error}}</div>
      <div v-if="mode==='replay'" role="status" class="notice replay">RECORDED DATA · {{replayState}} · 10 revisions/sec</div>
      <div v-else-if="status==='unavailable' || status==='stale'" role="status" class="notice">{{feed?.detail}}. Saved candles remain visible; source data may be delayed or the market closed.</div>
      <div v-if="mode==='backtest'" class="notice replay" role="status">HISTORICAL SNAPSHOT · 1-hour bars · {{historicalMeta?historicalMeta.source:'Load a saved dataset or fetch Yahoo history below.'}} · Never treated as a live feed.</div>
      <div class="content-grid"><section class="chart-panel"><div class="panel-heading"><div><h2>{{symbol}} <span> / USD</span></h2><p>{{mode==='backtest'?'Historical OHLCV · 1h candles':'Observed price · 1m candles & observed volume'}} · UTC</p></div><span class="bar-state">{{latest ? (latest.candle.complete?'INTERVAL CLOSED':'FORMING CANDLE') : 'AWAITING DATA'}}</span></div>
        <div class="ohlc" v-if="latest"><span>O <b>{{price(latest.candle.open)}}</b></span><span>H <b>{{price(latest.candle.high)}}</b></span><span>L <b>{{price(latest.candle.low)}}</b></span><span>C <b>{{price(latest.candle.close)}}</b></span><span>VOL <b>{{latest.candle.volume_known ? latest.candle.volume.toLocaleString() : 'unknown'}}</b></span></div>
        <div class="indicator-readout" data-testid="indicator-summary"><span class="fast-sma">SMA {{strategyWindows.short}} <b>{{price(latestIndicator?.fast)}}</b></span><span class="slow-sma">SMA {{strategyWindows.long}} <b>{{price(latestIndicator?.slow)}}</b></span><span>{{latestIndicator?.provisional?'PROVISIONAL · unfinished candle, no orders':'CONFIRMED · closed candles'}}</span><span v-if="lastSignal">{{lastSignal.provisional?'Preview':'Latest crossover'}}: {{lastSignal.signal.toUpperCase()}} · {{date(lastSignal.time)}}</span></div>
        <div class="chart-wrap"><div ref="chartEl" class="chart" role="img" :aria-label="symbol+' observed one-minute candlesticks and volume. Equivalent values are in the table below.'"></div><div v-if="!bars.length" class="empty-chart"><span>Waiting for observations</span><p>{{mode==='live'?'The chart fills only with received Yahoo data.':'No events have played yet.'}}</p></div></div>
        <div class="chart-footer"><span><i class="legend-price"></i>Price · SMA {{strategyWindows.short}} / {{strategyWindows.long}} <i class="legend-volume"></i>{{mode==='backtest'?'Yahoo volume':'Observed volume delta'}}</span><a href="https://www.tradingview.com/" target="_blank" rel="noopener">Charts by TradingView</a></div>
      </section><aside class="pipeline"><div class="eyebrow">DATA PROVENANCE</div><h2>From source to screen</h2><ol><li><span class="step">01</span><div><b>Yahoo Finance</b><p>{{mode==='backtest'?'Recorded hourly historical OHLCV.':'Streaming WebSocket observations.'}} Availability and delay vary.</p></div></li><li><span class="step">02</span><div><b>FastAPI → SQLite</b><p>Raw observations, receipt log, and versioned candles commit before display.</p></div></li><li><span class="step">03</span><div><b>Browser WebSocket</b><p>{{mode==='live'?'Saved snapshot pushed every second.':mode==='backtest'?'Saved dataset and causal strategy run.':'Saved revisions played in receipt order.'}}</p></div></li></ol><dl><dt>Source timestamp</dt><dd>{{date(latest?.candle.source_time)}}</dd><dt>Candle event saved</dt><dd>{{date(latest?.received_at)}}</dd><dt>Browser connection</dt><dd>{{connection}}</dd><dt>Candle revision</dt><dd>{{latest?.revision ?? '—'}}</dd><dt>Duplicate receipts</dt><dd>{{feed?.stats.receipts.duplicate ?? '—'}}</dd></dl><button class="failure-button" @click="toggleFeed" :disabled="mode!=='live' || connection!=='connected'">{{feed?.state==='unavailable'?'Reconnect Yahoo feed':'Disconnect feed · failure demo'}}</button><p class="fine-print">The failure control affects the local source connection. It preserves stored records.</p></aside></div>
      <StrategyPanel :symbol="symbol" :mode="mode" @historical="showHistorical" @settings="applySettings" />
      <section class="records"><div class="panel-heading"><div><div class="eyebrow">PERSISTENCE & AUDIT</div><h2>Recent candle records</h2></div><a :href="'/api/market/observations?symbol='+encodeURIComponent(symbol)" target="_blank">Inspect raw observations ↗</a></div><div class="table-scroll"><table><thead><tr><th>INTERVAL (UTC)</th><th>OPEN</th><th>HIGH</th><th>LOW</th><th>CLOSE</th><th>VOLUME Δ</th><th>REVISION</th><th>STATE</th></tr></thead><tbody><tr v-for="event in [...bars].reverse().slice(0,5)" :key="event.candle.time"><td>{{date(event.candle.time)}}</td><td>{{price(event.candle.open)}}</td><td>{{price(event.candle.high)}}</td><td>{{price(event.candle.low)}}</td><td>{{price(event.candle.close)}}</td><td>{{event.candle.volume_known?event.candle.volume.toLocaleString():'unknown'}}</td><td>r{{event.revision}} · #{{event.id}}</td><td><span :class="['state-tag',{closed:event.candle.complete}]">{{event.candle.complete?'Closed':'Forming'}}</span></td></tr><tr v-if="!bars.length"><td colspan="8">No stored candles for this view. No synthetic prices are substituted.</td></tr></tbody></table></div></section>
      <footer><span>Yahoo Finance WebSocket · Observed prices, not an exchange trade tape. Closed intervals may have gaps and receive later revisions.</span><a href="/stillpoint">Assignment 3 archive ↗</a></footer>
    </main>
  </div>`
}).mount('#app')
