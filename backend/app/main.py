from fastapi import FastAPI, Depends, HTTPException, Body, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
import aioredis, os, asyncio, base58, random
from sqlalchemy.ext.asyncio import AsyncSession
from solana.transaction import Transaction
from solana.system_program import TransferParams, transfer
from solana.publickey import PublicKey
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
from .solana_utils import get_client, load_keypair, create_mint_account
from .simulator import seed_and_start
from .telegram import notify
from .letsbonkfun_api import register_token_on_letsbonkfun
from .image_upload import pin_file_to_ipfs

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    # Redis cache
    redis = await aioredis.from_url(os.getenv("REDIS_URL"), encoding="utf8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="cache")
    # Bootstrap admin
    async for db in get_db():
        if not await list_users(db):
            await create_user(db, os.getenv("ADMIN_USER"), os.getenv("ADMIN_PASSWORD"), "admin")
        await seed_and_start(db)

# Auth
@app.post("/token", response_model=Token)
async def login(form_data=Depends(...), db: AsyncSession=Depends(get_db)):
    # omitted: verify password, create token
    ...

@app.post("/users", response_model=UserOut, dependencies=[Depends(require_roles("admin"))])
async def create_new_user(u: UserCreate, db: AsyncSession=Depends(get_db)):
    return await create_user(db, u.username, u.password, u.role)

@app.get("/users", response_model=list[UserOut], dependencies=[Depends(require_roles("admin"))])
async def get_all_users(db: AsyncSession=Depends(get_db)):
    return await list_users(db)

@app.patch("/users/{uid}/role", response_model=UserOut, dependencies=[Depends(require_roles("admin"))])
async def change_role(uid: int, new_role: str = Body(...), db: AsyncSession=Depends(get_db)):
    return await update_user_role(db, uid, new_role)

# Main wallet balance
@app.get("/main-wallet/balance", dependencies=[Depends(get_current_user)])
async def main_balance():
    sk = os.getenv("MM_SECRET_KEY","")
    kp = load_keypair(sk)
    cli = await get_client()
    bal = await cli.get_balance(kp.public_key)
    await cli.close()
    return {"balance_sol": bal['result']['value']/1e9}

# Simulators CRUD & fund
@app.get("/simulators", dependencies=[Depends(require_roles("admin","trader"))])
async def read_sims(db: AsyncSession=Depends(get_db)):
    return await list_simulators(db)

@app.post("/simulators", dependencies=[Depends(require_roles("admin","trader"))])
async def add_sim(db: AsyncSession=Depends(get_db)):
    kp = Keypair()
    sk = base58.b58encode(kp.secret_key).decode()
    pub= kp.public_key.to_base58()
    sim= await create_simulator(db, f"Trader{random.randint(1000,9999)}", sk, pub)
    asyncio.create_task(seed_and_start(db))
    return sim

@app.patch("/simulators/{sid}", dependencies=[Depends(require_roles("admin","trader"))])
async def edit_sim(sid: int, fields: dict=Body(...), db: AsyncSession=Depends(get_db)):
    await update_simulator(db, sid, **fields)
    return {"id": sid, **fields}

@app.delete("/simulators/{sid}", dependencies=[Depends(require_roles("admin","trader"))])
async def del_sim(sid:int, db:AsyncSession=Depends(get_db)):
    await delete_simulator(db, sid)
    return {"deleted": sid}

@app.post("/simulators/{sid}/fund", dependencies=[Depends(require_roles("admin","trader"))])
async def fund_sim(sid:int, amount_sol:float=Body(...), db:AsyncSession=Depends(get_db)):
    sim = await db.get(Simulator, sid)
    if not sim: raise HTTPException(404)
    main= load_keypair(os.getenv("MM_SECRET_KEY",""))
    to  = PublicKey(sim.pubkey)
    lam = int(amount_sol*1e9)
    cli = await get_client()
    tx  = Transaction().add(transfer(TransferParams(from_pubkey=main.public_key,to_pubkey=to,lamports=lam)))
    await cli.send_transaction(tx, main)
    await cli.close()
    return {"funded": sid, "amount": amount_sol}

# Settings endpoints omitted for brevity

@app.get("/pnl-summary", response_model=PnLSummary, dependencies=[Depends(require_roles("admin","trader"))])
@FastAPICache.decorator(expire=30)
async def pnl_summary(db:AsyncSession=Depends(get_db)):
    total, per = await get_pnl_summary(db)
    return PnLSummary(total_realized_pnl=total, per_simulator=per)

# Create token
@app.post("/create-token", dependencies=[Depends(require_roles("admin","trader"))])
async def create_token(
    secret_key: str = Body(...),
    name:       str = Body(...),
    symbol:     str = Body(...),
    supply:     int = Body(...),
    decimals:   int = Body(...),
    logo:       UploadFile = File(...)
):
    c = await logo.read()
    img = await pin_file_to_ipfs(c, logo.filename)
    payer = load_keypair(secret_key)
    mint  = Keypair()
    sol_tx= await create_mint_account(payer, mint, decimals)
    bf    = await register_token_on_letsbonkfun(mint.public_key.to_base58(),name,symbol,supply,img)
    await notify(f"Created {symbol}@{mint.public_key}")
    return {"sol_tx":sol_tx,"bf":bf,"mint":mint.public_key.to_base58(),"logo":img}
