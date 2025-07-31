from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from .models import User, Simulator, PnLMetrics
from passlib.context import CryptContext

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Users
async def get_user_by_username(db: AsyncSession, username: str):
    res = await db.execute(select(User).where(User.username==username))
    return res.scalars().first()

async def list_users(db: AsyncSession):
    res = await db.execute(select(User))
    return res.scalars().all()

async def create_user(db: AsyncSession, username: str, password: str, role: str):
    hashed = pwd_ctx.hash(password)
    user = User(username=username, hashed_password=hashed, role=role)
    db.add(user); await db.commit(); await db.refresh(user)
    return user

async def update_user_role(db: AsyncSession, user_id: int, new_role: str):
    await db.execute(
        update(User).where(User.id==user_id).values(role=new_role)
    )
    await db.commit()
    res = await db.execute(select(User).where(User.id==user_id))
    return res.scalars().first()

# Simulators
async def create_simulator(db: AsyncSession, name: str, sk: str, pub: str):
    sim = Simulator(name=name, secret_key=sk, pubkey=pub)
    db.add(sim); await db.commit(); await db.refresh(sim)
    return sim

async def list_simulators(db: AsyncSession):
    res = await db.execute(select(Simulator))
    return res.scalars().all()

async def update_simulator(db: AsyncSession, sim_id: int, **fields):
    await db.execute(update(Simulator).where(Simulator.id==sim_id).values(**fields))
    await db.commit()

async def delete_simulator(db: AsyncSession, sim_id: int):
    await db.execute(delete(Simulator).where(Simulator.id==sim_id))
    await db.commit()

# PnL
async def record_pnl(db: AsyncSession, sim_id: int, pnl: float):
    rec = PnLMetrics(simulator_id=sim_id, realized_pnl=pnl)
    db.add(rec); await db.commit()

async def get_pnl_summary(db: AsyncSession):
    total = (await db.execute(select(func.sum(PnLMetrics.realized_pnl)))).scalar() or 0.0
    per   = await db.execute(
        select(PnLMetrics.simulator_id, func.sum(PnLMetrics.realized_pnl))
        .group_by(PnLMetrics.simulator_id)
    )
    return total, dict(per.all())

