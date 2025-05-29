from fastapi import APIRouter
from strategies.force_trade.force_vol import ForceTradeVolParams, force_trade_vol
from strategies.force_trade.force_mc import ForceTradeMCParams, force_trade_mc
import asyncio


router = APIRouter(
    prefix="/force-trade",
    tags=["force-trade"],
    responses={404: {"description": "Not found"}},
)


# @router.post("/by_vol", response_model=bool)
async def execute_force_trade_by_vol(params: ForceTradeVolParams):
    """
    Execute the force trade by vol
    """
    asyncio.create_task(force_trade_vol(params))
    return True


# @router.post("/by_mc", response_model=bool)
async def execute_force_trade_by_mc(params: ForceTradeMCParams):
    """
    Execute the force trade by mc
    """
    asyncio.create_task(force_trade_mc(params))
    return True
