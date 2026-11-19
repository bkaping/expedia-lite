// Confirmed windows consume only closed candles; previews never enter confirmed history.
export function indicators(bars, short=5, long=20) {
  const closes=[]
  let previous=null
  return bars.map(bar=>{
    const values=[...closes,bar.close]
    const average=n=>values.length>=n ? values.slice(-n).reduce((a,b)=>a+b,0)/n : null
    const fast=average(short),slow=average(long)
    let delta=slow==null?null:fast-slow
    if(delta!=null && Math.abs(delta)<=Math.max(1e-10,1e-12*Math.max(Math.abs(fast),Math.abs(slow)))) delta=0
    const signal=previous==null||delta==null?null:previous<=0&&delta>0?'buy':previous>=0&&delta<0?'sell':null
    if(bar.complete) { closes.push(bar.close); if(closes.length>long) closes.shift(); if(delta!=null) previous=delta }
    return {time:bar.time,fast,slow,signal,provisional:!bar.complete}
  })
}
