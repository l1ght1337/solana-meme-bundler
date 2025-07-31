import os, asyncio, random, base58
from solana.keypair import Keypair
from solana.publickey import PublicKey
from .db import get_db
from .crud import record_pnl, list_simulators, create_simulator
from .models import Simulator
from sqlalchemy.ext.asyncio import AsyncSession

SIM_COUNT = int(os.getenv("SIMULATOR_COUNT","10"))

async def sim_trader_loop(sim: Simulator, db: AsyncSession):
    while True:
        db_sim = await db.get(Simulator, sim.id)
        if not db_sim.is_active:
            await asyncio.sleep(1)
            continue
        # экспоненциальный интервал
        interval = random.expovariate(1.0/db_sim.avg_interval)
        await asyncio.sleep(interval)
        side = "buy" if random.random()<db_sim.buy_bias else "sell"
        qty  = max(0.01, random.gauss(db_sim.vol_mean, db_sim.vol_std))
        qty  = min(qty, db_sim.vol_mean*5)
        # тут вы подставляете свой mint из фронта
        mint = os.getenv("EXTERNAL_MINT")  # передайте его в env
        in_m, out_m = ("So11111111111111111111111111111111111111112", mint) if side=="buy" else (mint, "So11111111111111111111111111111111111111112")
        # эмуляция PnL
        price = random.uniform(0.5, 1.5)
        pnl   = price * qty if side=="sell" else -price * qty
        await record_pnl(db, sim.id, pnl)

async def seed_and_start(db: AsyncSession):
    sims = await list_simulators(db)
    if not sims:
        for i in range(1, SIM_COUNT+1):
            kp = Keypair()
            sk = base58.b58encode(kp.secret_key).decode()
            pub= kp.public_key.to_base58()
            sim = await create_simulator(db, f"Trader{i}", sk, pub)
            asyncio.create_task(sim_trader_loop(sim, db))
    else:
        for sim in sims:
            asyncio.create_task(sim_trader_loop(sim, db))

