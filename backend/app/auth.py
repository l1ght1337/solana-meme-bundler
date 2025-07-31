import os, jwt
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from .schemas import TokenData

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
SECRET_KEY    = os.getenv("JWT_SECRET", "changeme")
ALGO          = "HS256"
ACCESS_EXPIRE = int(os.getenv("JWT_EXPIRE_MINUTES","60"))

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_EXPIRE)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGO)

async def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenData:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGO])
        return TokenData(username=payload["sub"], role=payload["role"])
    except:
        raise HTTPException(401, "Invalid token")

def require_roles(*allowed):
    async def verifier(user: TokenData = Depends(get_current_user)):
        if user.role not in allowed:
            raise HTTPException(403, "Forbidden")
        return user
    return verifier
