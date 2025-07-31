from dotenv import load_dotenv
load_dotenv()

import os, httpx

BASE = os.getenv("LETSBONKFUN_API_BASE")
KEY  = os.getenv("LETSBONKFUN_API_KEY")

async def register_token_on_letsbonkfun(mint,name,symbol,supply,image_url=None):
    url = f"{BASE}/v1/tokens"
    headers = {"Authorization":f"Bearer {KEY}", "Content-Type":"application/json"}
    payload = {"mint":mint,"name":name,"symbol":symbol,"supply":supply}
    if image_url: payload["image"] = image_url
    async with httpx.AsyncClient() as c:
        r = await c.post(url,json=payload,headers=headers)
        r.raise_for_status()
        return r.json()
