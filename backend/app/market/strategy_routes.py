from __future__ import annotations

import asyncio
import json

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field, model_validator

from .routes import store, check_symbol
from .simulation import SimulationStore, SAMPLE_PATH
from .strategy import indicator_series

simulations=SimulationStore(store)
router=APIRouter(prefix='/api/strategy')


class Parameters(BaseModel):
    short: int=Field(5,ge=2,le=99)
    long: int=Field(20,ge=3,le=100)
    initial_cash: float=Field(10000,gt=0,le=1000000,allow_inf_nan=False)
    fee: float=Field(1,ge=0,le=100,allow_inf_nan=False)
    slippage_bps: float=Field(5,ge=0,le=100,allow_inf_nan=False)

    @model_validator(mode='after')
    def ordered_windows(self):
        if self.short>=self.long:
            raise ValueError('Short SMA must be smaller than long SMA')
        return self


class BacktestRequest(Parameters):
    dataset_id: str=Field(min_length=64,max_length=64)


class PaperRequest(Parameters):
    symbol: str='AAPL'


class HistoryRequest(BaseModel):
    symbol: str='AAPL'


@router.get('/indicators')
def indicators(symbol: str='AAPL',short: int=Query(5,ge=2,le=99),long: int=Query(20,ge=3,le=100)):
    check_symbol(symbol)
    if short>=long:
        raise HTTPException(422,'Short SMA must be smaller than long SMA')
    return {'points':indicator_series([e['candle'] for e in store.snapshot(symbol)],short,long)}


@router.get('/datasets')
def datasets(symbol: str='AAPL'):
    check_symbol(symbol)
    return {'datasets':simulations.datasets(symbol)}


@router.get('/datasets/{identifier}')
def dataset(identifier: str):
    try:
        return simulations.dataset(identifier)
    except KeyError as error:
        raise HTTPException(404,str(error)) from error


@router.post('/history/fetch')
def fetch_history(request: HistoryRequest):
    check_symbol(request.symbol)
    try:
        return simulations.fetch_history(request.symbol)
    except Exception as error:
        raise HTTPException(503,f'Yahoo historical feed unavailable ({type(error).__name__}); use an explicitly saved dataset instead') from error


@router.post('/history/sample')
def sample_history():
    if not SAMPLE_PATH.exists():
        raise HTTPException(404,'No included recorded Yahoo sample')
    return simulations.save_dataset(json.loads(SAMPLE_PATH.read_text()))


@router.get('/backtests')
def runs(symbol: str='AAPL'):
    check_symbol(symbol)
    return {'runs':simulations.runs(symbol)}


@router.post('/backtests')
def run_backtest(request: BacktestRequest):
    try:
        return simulations.run_backtest(request.dataset_id,request.model_dump(exclude={'dataset_id'}))
    except KeyError as error:
        raise HTTPException(404,str(error)) from error
    except ValueError as error:
        raise HTTPException(422,str(error)) from error


@router.get('/backtests/{identifier}')
def get_run(identifier: str):
    try:
        return simulations.run(identifier)
    except KeyError as error:
        raise HTTPException(404,str(error)) from error


@router.get('/paper')
def paper(symbol: str='AAPL'):
    check_symbol(symbol)
    return {'paper':simulations.latest_paper(symbol)}


@router.post('/paper')
def start_paper(request: PaperRequest):
    check_symbol(request.symbol)
    try:
        return simulations.start_paper(request.symbol,request.model_dump(exclude={'symbol'}))
    except ValueError as error:
        raise HTTPException(409,str(error)) from error


@router.post('/paper/{identifier}/stop')
def stop_paper(identifier: str):
    try:
        return simulations.stop_paper(identifier)
    except KeyError as error:
        raise HTTPException(404,str(error)) from error


async def process_paper_accounts():
    while True:
        simulations.advance_paper()
        await asyncio.sleep(1)
