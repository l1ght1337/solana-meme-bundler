import os
import random
import asyncio
from datetime import datetime, timedelta

from fastapi import FastAPI, Depends, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext
import jwt

from solana.keypair import Keypair
from solana_utils import load_keypair, get_client

from models import Base
from crud import (
    get_user_by_username,
    list_users,
    create_user,
    update_user_role,
    list_simulators,
    create_simulator,
    update_simulator,
    delete_simulator,
    get_pnl_summary,
)
from schemas import Token, UserCreate, UserOut, PnLSummary
from simulator import run_simulator_loop

# --- Настройки и инициализация ---

# База на SQLite (Gitpod-friendly)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///workspace/db.sqlite")
engine = create_async_engine(DATABASE_URL, future=True, echo=False)
AsyncSessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

# Auth / JWT
JWT_SECRET = os.getenv("JWT_SECRET", "UltraSecureJWTSecretKey123!")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = 60
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

app = FastAPI(title="Solana Meme-Bundler API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Зависимость для сессии
async def get_db():
    async with AsyncSessionLocal() as db:
        yield db

# Функция для создания JWT
def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=JWT_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)

# Получить текущего пользователя из токена
async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        if not username or not role:
            raise HTTPException(status_code=401, detail="Invalid token")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = await get_user_by_username(db, username)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    user.role = role
    return user

# Ограничитель ролей
def require_roles(*roles: str):
    async def checker(user = Depends(get_current_user)):
        if user.role not in roles:
            raise HTTPException(status_code=403, detail="Forbidden")
        return user
    return Depends(checker)

# При старте создаём таблицы и админа, запускаем симуляторы
@app.on_event("startup")
async def on_startup():
    # Создание таблиц
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Создание админа, если нет пользователей
    async with AsyncSessionLocal() as db:
        users = await list_users(db)
        if not users:
            await create_user(
                db,
                os.getenv("ADMIN_USER", "admin"),
                os.getenv("ADMIN_PASSWORD", "SuperSecretAdmin123"),
                role="admin",
            )
    # Запуск фонового цикла симуляторов
    asyncio.create_task(run_simulator_loop())

# --- Эндпоинты ---

@app.post("/token", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    user = await get_user_by_username(db, form_data.username)
    if not user or not pwd_ctx.verify(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    token = create_access_token({"sub": user.username, "role": user.role})
    return {"access_token": token, "token_type": "bearer"}

@app.post(
    "/users",
    response_model=UserOut,
    dependencies=[Depends(require_roles("admin"))],
)
async def create_new_user(
    u: UserCreate, db: AsyncSession = Depends(get_db)
):
    return await create_user(db, u.username, u.password, u.role)

@app.get(
    "/users",
    response_model=list[UserOut],
    dependencies=[Depends(require_roles("admin"))],
)
async def read_users(db: AsyncSession = Depends(get_db)):
    return await list_users(db)

@app.patch(
    "/users/{user_id}/role",
    response_model=UserOut,
    dependencies=[Depends(require_roles("admin"))],
)
async def change_role(
    user_id: int, new_role: str = Body(...), db: AsyncSession = Depends(get_db)
):
    return await update_user_role(db, user_id, new_role)

@app.get(
    "/main-wallet/balance",
    dependencies=[Depends(get_current_user)],
)
async def main_wallet_balance():
    seed = os.getenv("MM_SECRET_KEY")
    if not seed:
        raise HTTPException(status_code=500, detail="Main wallet key not set")
    kp = load_keypair(seed)
    client = await get_client()
    resp = await client.get_balance(kp.public_key)
    await client.close()
    return {"balance_sol": resp["result"]["value"] / 1e9}

@app.get(
    "/simulators",
    dependencies=[Depends(require_roles("admin", "trader"))],
)
async def get_sims(db: AsyncSession = Depends(get_db)):
    return await list_simulators(db)

@app.post(
    "/simulators",
    dependencies=[Depends(require_roles("admin", "trader"))],
)
async def add_simulator(db: AsyncSession = Depends(get_db)):
    kp = Keypair()
    sim = await create_simulator(
        db,
        name=f"Trader{random.randint(1000,9999)}",
        secret_key=kp.secret_key.hex(),
        public_key=kp.public_key.to_base58().decode(),
    )
    return sim

@app.patch(
    "/simulators/{sim_id}",
    dependencies=[Depends(require_roles("admin", "trader"))],
)
async def patch_sim(
    sim_id: int, data: dict = Body(...), db: AsyncSession = Depends(get_db)
):
    await update_simulator(db, sim_id, **data)
    return {"status": "ok"}

@app.delete(
    "/simulators/{sim_id}",
    dependencies=[Depends(require_roles("admin"))],
)
async def remove_sim(sim_id: int, db: AsyncSession = Depends(get_db)):
    await delete_simulator(db, sim_id)
    return {"status": "deleted"}

@app.get(
    "/pnl",
    response_model=PnLSummary,
    dependencies=[Depends(require_roles("admin", "trader"))],
)
async def pnl(db: AsyncSession = Depends(get_db)):
    total, per = await get_pnl_summary(db)
    return PnLSummary(total_realized_pnl=total, per_simulator=per)
