from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str]
    role: Optional[str]

class UserCreate(BaseModel):
    username: str
    password: str
    role: Optional[str] = "trader"

class UserOut(BaseModel):
    id: int
    username: str
    role: str
    class Config:
        orm_mode = True

class PnLSummary(BaseModel):
    total_realized_pnl: float
    per_simulator: Dict[int, float]
