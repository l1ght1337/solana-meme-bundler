import datetime
from sqlalchemy import (
    Column, Integer, String, DateTime, Boolean, Float, ForeignKey
)
from sqlalchemy.orm import relationship
from .db import Base

class User(Base):
    __tablename__ = "users"
    id             = Column(Integer, primary_key=True, index=True)
    username       = Column(String, unique=True, index=True, nullable=False)
    hashed_password= Column(String, nullable=False)
    role           = Column(String, default="trader", nullable=False)

class Simulator(Base):
    __tablename__ = "simulators"
    id           = Column(Integer, primary_key=True, index=True)
    name         = Column(String, unique=True, index=True)
    secret_key   = Column(String, nullable=False)
    pubkey       = Column(String, nullable=False)
    is_active    = Column(Boolean, default=True, nullable=False)
    last_trade   = Column(DateTime, nullable=True)
    avg_interval = Column(Float, default=15.0)
    vol_mean     = Column(Float, default=1.0)
    vol_std      = Column(Float, default=0.5)
    buy_bias     = Column(Float, default=0.5)

class PnLMetrics(Base):
    __tablename__ = "pnl_metrics"
    id            = Column(Integer, primary_key=True, index=True)
    simulator_id  = Column(Integer, ForeignKey("simulators.id"), nullable=True)
    realized_pnl  = Column(Float)
    timestamp     = Column(DateTime, default=datetime.datetime.utcnow)
    simulator     = relationship("Simulator")

