from fastapi import FastAPI, Depends, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
import aioredis, os, asyncio, random
from sqlalchemy.ext.asyncio import AsyncSession
from solana.keypair import Keypair

from .db import Base, engine, get_db
from .models import User, Simulator
from .crud import (
    list_users, create_user, update_user_role,
    create_simulator, list_simulators, update_simulator, delete_simulator,
    record_pnl, get_pnl_summary
)
from .auth import create_access_token, get_current_user, require_roles
from .schemas import Token, UserCreate, UserOut, PnLSummary
from .simulator import seed_and_start

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    redis = await aioredis.from_url(os.getenv("REDIS_URL"), encoding="utf8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="cache")
    async for db in get_db():
        if not await list_users(db):
            await create_user(db, os.getenv("ADMIN_USER"), os.getenv("ADMIN_PASSWORD"), "admin")
        await seed_and_start(db)

# --- Auth ---
@app.post("/token", response_model=Token)
async def login(form_data=Depends(...), db: AsyncSession=Depends(get_db)):
    # здесь проверка пароля опущена для краткости
    user = await get_user_by_username(db, form_data.username)
    if not user:
        raise HTTPException(400, "Invalid credentials")
    token = create_access_token({"sub": user.username, "role": user.role})
    return {"access_token": token, "token_type": "bearer"}

@app.post("/users", response_model=UserOut, dependencies=[Depends(require_roles("admin"))])
async def create_new_user(u: UserCreate, db: AsyncSession = Depends(get_db)):
    return await create_user(db, u.username, u.password, u.role)

@app.get("/users", response_model=list[UserOut], dependencies=[Depends(require_roles("admin"))])
async def get_all_users(db: AsyncSession = Depends(get_db)):
    return await list_users(db)

@app.patch("/users/{uid}/role", response_model=UserOut, dependencies=[Depends(require_roles("admin"))])
async def change_role(uid: int, new_role: str = Body(...), db: AsyncSession = Depends(get_db)):
    return await update_user_role(db, uid, new_role)

# Main wallet balance
@app.get("/main-wallet/balance", dependencies=[Depends(get_current_user)])
async def main_balance():
    sk = os.getenv("MM_SECRET_KEY", "")
    if not sk:
        raise HTTPException(500, "Main key not set")
    from .solana_utils import load_keypair, get_client
    kp = load_keypair(sk)
    cli = await get_client()
    bal = await cli.get_balance(kp.public_key)
    await cli.close()
    return {"balance_sol": bal['result']['value'] / 1e9}

# --- Simulators CRUD & fund ---
@app.get("/simulators", dependencies=[Depends(require_roles("admin","trader"))])
async def read_sims(db: AsyncSession = Depends(get_db)):
    return await list_simulators(db)

@app.post("/simulators", dependencies=[Depends(require_roles("admin","trader"))])
async def add_sim(db: AsyncSession = Depends(get_db)):
    kp = Keypair()
    sk = kp.secret_key.hex()
    pub= kp.public_key.to_base58()
    sim = await create_simulator(db, f"Trader{random.randint(1000,9999)}", sk, pub)
    asyncio.create_task(seed_and_start(db))
    return sim

@app.patch("/simulators/{sid}", dependencies=[Depends(require_roles("admin","trader"))])
async def edit_sim(sid: int, fields: dict = Body(...), db: AsyncSession = Depends(get_db)):
    await update_simulator(db, sid, **fields)
    return {"id": sid, **fields}

@app.delete("/simulators/{sid}", dependencies=[Depends(require_roles("admin","trader"))])
async def del_sim(sid: int, db: AsyncSession = Depends(get_db)):
    await delete_simulator(db, sid)
    return {"deleted": sid}

# --- PnL summary ---
@app.get("/pnl-summary", response_model=PnLSummary, dependencies=[Depends(require_roles("admin","trader"))])
@FastAPICache.decorator(expire=30)
async def pnl_summary(db: AsyncSession = Depends(get_db)):
    total, per = await get_pnl_summary(db)
    return PnLSummary(total_realized_pnl=total, per_simulator=per)

# Include websocket router
from .websocket import router as ws_router
app.include_router(ws_router)

