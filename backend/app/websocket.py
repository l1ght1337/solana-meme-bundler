import asyncio
from fastapi import APIRouter, WebSocket, Depends
from .db import get_db
from .crud import list_simulators
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

@router.websocket("/ws/portfolio")
async def ws_portfolio(ws: WebSocket, db: AsyncSession = Depends(get_db)):
    await ws.accept()
    while True:
        sims = await list_simulators(db)
        data = [{"id": s.id, "last_trade": s.last_trade.isoformat() if s.last_trade else None} for s in sims]
        await ws.send_json(data)
        await asyncio.sleep(5)
