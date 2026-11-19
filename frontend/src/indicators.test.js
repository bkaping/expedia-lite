import test from 'node:test'
import assert from 'node:assert/strict'
import { indicators } from './indicators.js'
const bars=values=>values.map((close,time)=>({close,time,complete:true}))
test('published three-period SMA example and crossover fixture',()=>{
  assert.deepEqual(indicators(bars([5,6,7,8,9]),2,3).map(p=>p.slow),[null,null,6,7,8])
  assert.deepEqual(indicators(bars([3,2,1,2,3,4,3,2,1,2,3]),2,3).flatMap((p,i)=>p.signal?[[i,p.signal]]:[]),[[4,'buy'],[7,'sell'],[10,'buy']])
})
test('unfinished preview never contaminates confirmed windows',()=>{
  const input=bars([3,2,1,100,2,3]);input[3].complete=false
  assert.deepEqual(indicators(input,2,3).filter(p=>!p.provisional),indicators(input.filter(b=>b.complete),2,3))
  assert.equal(indicators(input,2,3)[3].provisional,true)
})
