import os, asyncio, random, base58, httpx
from solana.keypair import Keypair
from solana.publickey import PublicKey
from solana.rpc.async_api import AsyncClient
from solana.transaction import Transaction
from solana.system_program import transfer, TransferParams
from .db import get_db
from .crud import record_pnl, list_simulators, create_simulator
from .models import Simulator
from sqlalchemy.ext.asyncio import AsyncSession

PAPER_MODE = False  # switched via UI, ignore .env here
RPC        = os.getenv("SOLANA_RPC_URL")
SIM_COUNT  = int(os.getenv("SIMULATOR_COUNT","10"))

async def get_client():
    return AsyncClient(RPC)

async def get_route(secret_key,in_mint,out_mint,amount):
    if PAPER_MODE:
        return {"inAmount":"0","inAmountDecimals":9,"outAmount":"0","outAmountDecimals":9}
    async with httpx.AsyncClient() as c:
        r = await c.get(
          "https://quote-api.jup.ag/v4/quote",
          params={"inputMint":in_mint,"outputMint":out_mint,"amount":str(amount),"slippageBps":50}
        )
        r.raise_for_status()
        d = r.json().get("data") or []
        return d[0] if d else None

async def sim_trader_loop(sim: Simulator, db: AsyncSession):
    rpc = await get_client()
    while True:
        db_sim = await db.get(Simulator, sim.id)
        if not db_sim.is_active:
            await asyncio.sleep(1); continue
        # экспоненциальный интервал
        interval = random.expovariate(1.0/db_sim.avg_interval)
        await asyncio.sleep(interval)
        side = "buy" if random.random()<db_sim.buy_bias else "sell"
        qty  = max(0.01, random.gauss(db_sim.vol_mean, db_sim.vol_std))
        qty  = min(qty, db_sim.vol_mean*5)
        in_m, out_m = ("So11111111111111111111111111111111111111112", sim.pubkey) if side=="buy" else (sim.pubkey, "So11111111111111111111111111111111111111112")
        amount = int(qty*(1e9))
        route = await get_route(db_sim.secret_key, in_m, out_m, amount)
        if not route: continue
        price = (float(route["inAmount"])/10**route["inAmountDecimals"])/(float(route["outAmount"])/10**route["outAmountDecimals"])
        pnl   = price*qty if side=="sell" else -price*qty
        await record_pnl(db, sim.id, pnl)
    await rpc.close()

async def seed_and_start(db: AsyncSession):
    from .solana_utils import load_keypair
    main_sk = os.getenv("MM_SECRET_KEY","")
    main    = load_keypair(main_sk) if main_sk else None
    sims = await list_simulators(db)
    if not sims:
        for i in range(1, SIM_COUNT+1):
            kp = Keypair()
            sk = base58.b58encode(kp.secret_key).decode()
            pub= kp.public_key.to_base58()
            sim = await create_simulator(db, f"Trader{i}", sk, pub)
            # без автоматического фандинга
            asyncio.create_task(sim_trader_loop(sim, db))
    else:
        for sim in sims:
            asyncio.create_task(sim_trader_loop(sim, db))
