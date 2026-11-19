import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import { createChart, LineSeries, ColorType } from 'lightweight-charts'

const base=import.meta.env.VITE_API_BASE_URL || ''
async function api(path,body) {
  const response=await fetch(base+'/api/strategy'+path,body===undefined?{}:{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)})
  const result=await response.json()
  if(!response.ok) throw new Error(typeof result.detail==='string'?result.detail:'Check strategy settings and try again')
  return result
}

export default {
  props:['symbol','mode'],emits:['historical','settings'],
  setup(props,{emit}) {
    const short=ref(5),long=ref(20),initial=ref(10000),fee=ref(1),slippage=ref(5)
    const datasets=ref([]),datasetId=ref(''),dataset=ref(null),runs=ref([]),run=ref(null),paper=ref(null)
    const busy=ref(false),problem=ref(''),equityEl=ref(null),message=ref('')
    let chart,line,poller,revision=0
    const historical=computed(()=>props.mode==='backtest')
    const result=computed(()=>historical.value?run.value?.result:props.mode==='live'?paper.value?.result:null)
    const account=computed(()=>result.value?.account)
    const money=value=>value==null?'—':new Intl.NumberFormat('en-US',{style:'currency',currency:'USD',maximumFractionDigits:2}).format(value)
    const when=value=>value?new Date(value*1000).toISOString().replace('T',' ').slice(0,19)+' UTC':'—'
    const parameters=()=>({short:Number(short.value),long:Number(long.value),initial_cash:Number(initial.value),fee:Number(fee.value),slippage_bps:Number(slippage.value)})
    const settings=()=>{
      if(Number.isInteger(short.value)&&Number.isInteger(long.value)&&short.value>=2&&short.value<long.value&&long.value<=100) emit('settings',{short:Number(short.value),long:Number(long.value)})
      run.value=null;message.value='Settings changed; run the backtest to apply valid windows.'
    }
    const plot=()=>{
      if(!line) return
      line.setData(result.value?.equity_curve.map(point=>({time:point.time,value:point.equity})) || [])
      chart.timeScale().fitContent()
    }
    watch(result,plot,{deep:true})
    const task=async action=>{
      if(busy.value) return
      busy.value=true;problem.value='';message.value=''
      const current=revision
      try { await action(current) } catch(error) { if(current===revision) problem.value=error.message } finally {busy.value=false}
    }
    const showDataset=value=>{dataset.value=value;datasetId.value=value.id;emit('historical',value)}
    const loadDataset=()=>task(async current=>{
      const value=await api('/datasets/'+datasetId.value)
      if(current!==revision) return
      run.value=null;showDataset(value)
    })
    const refresh=async()=>{
      const current=++revision
      problem.value='';run.value=null;paper.value=null;dataset.value=null;datasetId.value='';datasets.value=[];runs.value=[]
      try {
        if(historical.value) {
          const [saved,sessions]=await Promise.all([api('/datasets?symbol='+props.symbol),api('/backtests?symbol='+props.symbol)])
          if(current!==revision) return
          datasets.value=saved.datasets;runs.value=sessions.runs
          if(saved.datasets.length) {
            const value=await api('/datasets/'+saved.datasets[0].id)
            if(current===revision) showDataset(value)
          }
        } else if(props.mode==='live') {
          const value=await api('/paper?symbol='+props.symbol)
          if(current===revision) {paper.value=value.paper; if(value.paper?.active) {short.value=value.paper.short;long.value=value.paper.long;emit('settings',{short:short.value,long:long.value})}}
        }
      } catch(error) {if(current===revision)problem.value=error.message}
    }
    const history=sample=>task(async current=>{
      const value=await api(sample?'/history/sample':'/history/fetch',sample?{}:{symbol:props.symbol})
      if(current!==revision) return
      showDataset(value);run.value=null
      datasets.value=(await api('/datasets?symbol='+props.symbol)).datasets
      message.value=sample?'Included recorded Yahoo snapshot loaded.':'Yahoo history fetched and saved as an immutable snapshot.'
    })
    const execute=()=>task(async current=>{
      const value=await api('/backtests',{dataset_id:datasetId.value,...parameters()})
      if(current!==revision) return
      run.value=value;runs.value=(await api('/backtests?symbol='+props.symbol)).runs
      message.value='Backtest saved. Signals use closed bars; simulated fills use later opens.'
    })
    const openRun=event=>task(async current=>{
      if(!event.target.value) return
      const value=await api('/backtests/'+event.target.value)
      const data=await api('/datasets/'+value.dataset_id)
      if(current!==revision) return
      for(const [key,target] of [['short',short],['long',long],['initial_cash',initial],['fee',fee],['slippage_bps',slippage]]) target.value=value.parameters[key]
      emit('settings',{short:short.value,long:long.value});showDataset(data);run.value=value
    })
    const startPaper=()=>task(async current=>{
      const value=await api('/paper',{symbol:props.symbol,...parameters()})
      if(current===revision) {paper.value=value;message.value='Forward paper account started. Historical candles warm up the SMAs without historical trades.'}
    })
    const stopPaper=()=>task(async current=>{
      const value=await api('/paper/'+paper.value.id+'/stop',{})
      if(current===revision)paper.value=value
    })
    watch(()=>[props.symbol,props.mode],refresh)
    onMounted(()=>{
      chart=createChart(equityEl.value,{autoSize:true,layout:{background:{type:ColorType.Solid,color:'#101c28'},textColor:'#8099ae'},grid:{vertLines:{visible:false},horzLines:{color:'#20313e'}},timeScale:{timeVisible:true},rightPriceScale:{borderVisible:false}})
      line=chart.addSeries(LineSeries,{color:'#8ad8c3',lineWidth:2,priceFormat:{type:'price',precision:2,minMove:.01}})
      refresh()
      poller=setInterval(async()=>{
        if(props.mode!=='live'||busy.value) return
        const current=revision
        try { const value=await api('/paper?symbol='+props.symbol);if(current===revision)paper.value=value.paper } catch { /* Live feed/offline status is shown in the main dashboard. */ }
      },3000)
    })
    onBeforeUnmount(()=>{revision++;clearInterval(poller);chart?.remove()})
    return {short,long,initial,fee,slippage,historical,datasets,datasetId,dataset,runs,run,paper,busy,problem,message,result,account,equityEl,money,when,settings,loadDataset,history,execute,openRun,startPaper,stopPaper}
  },
  template:`<section class="strategy-panel records" aria-label="Simulated strategy">
    <div class="panel-heading"><div><div class="eyebrow">SMA CROSSOVER · SIMULATION ONLY</div><h2>{{historical?'Historical backtesting':'Forward paper account'}}</h2></div><span class="bar-state">{{historical?'RECORDED HISTORY':mode==='replay'?'REPLAY · NO TRADING':paper?.active?'PAPER STRATEGY ACTIVE':'PAPER STRATEGY STOPPED'}}</span></div>
    <div class="strategy-body">
      <p class="strategy-intro">{{historical?'Evaluate past bars sequentially. Decisions use closed candles; fills use the next available bar open.':'Paper trading is optional and simulated. Only new closed-bar crossovers can place orders; a later received quote can fill them.'}}</p>
      <div class="strategy-settings"><label>Short SMA<input data-testid="short-window" type="number" min="2" max="99" v-model.number="short" @change="settings" :disabled="paper?.active && !historical" /></label><label>Long SMA<input data-testid="long-window" type="number" min="3" max="100" v-model.number="long" @change="settings" :disabled="paper?.active && !historical" /></label><label>Starting cash ($)<input type="number" min="1" max="1000000" v-model.number="initial" @change="settings" :disabled="paper?.active && !historical" /></label><label>Fee per fill ($)<input type="number" min="0" max="100" step="0.1" v-model.number="fee" @change="settings" :disabled="paper?.active && !historical" /></label><label>Slippage (bps)<input type="number" min="0" max="100" step="1" v-model.number="slippage" @change="settings" :disabled="paper?.active && !historical" /></label></div>
      <div v-if="historical" class="strategy-actions"><button @click="history(false)" :disabled="busy">Fetch Yahoo history</button><button data-testid="load-sample" v-if="symbol==='AAPL'" @click="history(true)" :disabled="busy">Load included AAPL snapshot</button><button class="primary-action" data-testid="run-backtest" @click="execute" :disabled="busy || !datasetId">{{busy?'Working…':'Run backtest'}}</button></div>
      <div v-else-if="mode==='live'" class="strategy-actions"><button class="primary-action" data-testid="start-paper" @click="startPaper" :disabled="busy || paper?.active">Start paper strategy</button><button data-testid="stop-paper" @click="stopPaper" :disabled="busy || !paper?.active">Stop paper strategy</button><span class="fine-print">A new account begins with the selected cash. One active account per instrument.</span></div>
      <div v-if="historical && datasets.length" class="dataset-choices"><label>Saved dataset<select aria-label="Saved dataset" v-model="datasetId" @change="loadDataset" :disabled="busy"><option v-for="value in datasets" :value="value.id">{{when(value.fetched_at)}} · {{value.bars_count}} hourly bars · {{value.id.slice(0,8)}}</option></select></label><label v-if="runs.length">Saved run<select aria-label="Saved run" @change="openRun" :disabled="busy"><option value="">Open a saved run…</option><option v-for="value in runs" :value="value.id">{{when(value.created_at)}} · {{value.id.slice(0,8)}}</option></select></label></div>
      <p v-if="dataset && historical" class="dataset-note" data-testid="dataset-provenance">{{dataset.source}} · {{dataset.bars.length}} hourly bars · fetched {{when(dataset.fetched_at)}} · snapshot {{dataset.id.slice(0,12)}}. Unadjusted; no dividends or splits credited.</p>
      <p v-if="problem" role="alert" class="notice">{{problem}}</p><p v-if="message" role="status" class="strategy-message">{{message}}</p>
      <div v-if="account" class="account-grid" data-testid="account-summary"><div><span>ACCOUNT EQUITY</span><strong>{{money(account.equity)}}</strong></div><div><span>CASH</span><strong>{{money(account.cash)}}</strong></div><div><span>POSITION · {{symbol}}</span><strong>{{account.quantity.toFixed(6)}}</strong></div><div><span>REALIZED P/L</span><strong :class="account.realized_pnl>=0?'positive':'negative'">{{money(account.realized_pnl)}}</strong></div><div><span>UNREALIZED P/L</span><strong :class="account.unrealized_pnl>=0?'positive':'negative'">{{money(account.unrealized_pnl)}}</strong></div><div><span>RETURN / MAX DRAWDOWN</span><strong>{{account.return_pct.toFixed(2)}}% / {{result.max_drawdown_pct.toFixed(2)}}%</strong></div></div>
      <div class="equity-heading"><span>SIMULATED EQUITY · USD</span><span v-if="account">{{result.fills.length}} fills · {{result.closed_trades}} closed trades · {{money(account.fees_paid)}} fees</span></div><div ref="equityEl" class="equity-chart" role="img" aria-label="Simulated account equity over completed bars; summary and fill values are also shown as text."></div>
      <p v-if="account" class="dataset-note">{{historical?'Run '+run.id.slice(0,12):'Paper account '+paper.id.slice(0,12)}} · long only · fractional units to 6 decimals · no leverage · fees included in entry cost · open positions marked to last processed price; no forced final sale.</p>
      <p v-else class="dataset-note">{{historical?'Load recorded Yahoo history, then run the strategy to see simulated outcomes.':'Start a paper account to process new market events. Warming up requires '+long+' closed observations. Replay never places orders.'}}</p>
    </div>
    <div class="panel-heading"><h2>Orders & simulated fills</h2><span class="dataset-note">{{result?.orders.length || 0}} orders · latest 12 shown</span></div>
    <div class="table-scroll"><table data-testid="orders-table"><thead><tr><th>SIGNAL BAR (UTC)</th><th>SIDE</th><th>STATUS</th><th>FILL (UTC)</th><th>QUANTITY</th><th>PRICE / FEE</th><th>REALIZED P/L</th></tr></thead><tbody><tr v-for="order in [...(result?.orders || [])].reverse().slice(0,12)" :key="order.id"><td>{{when(order.signal_time)}}</td><td :class="order.side==='buy'?'positive':'negative'">{{order.side.toUpperCase()}}</td><td :title="order.reason">{{order.status}}</td><td>{{when(order.fill_time)}}</td><td>{{result.fills.find(f=>f.order_id===order.id)?.quantity.toFixed(6) ?? '—'}}</td><td>{{money(result.fills.find(f=>f.order_id===order.id)?.price)}} / {{money(result.fills.find(f=>f.order_id===order.id)?.fee)}}</td><td>{{money(result.fills.find(f=>f.order_id===order.id)?.realized_pnl)}}</td></tr><tr v-if="!result?.orders.length"><td colspan="7">No orders yet. A full warm-up and a new confirmed crossover are required.</td></tr></tbody></table></div>
    <p class="strategy-footnote">Historical results describe this dataset and these assumptions. They do not establish future performance. Later data corrections, missing bars, corporate actions and execution costs can change the result.</p>
  </section>`
}
