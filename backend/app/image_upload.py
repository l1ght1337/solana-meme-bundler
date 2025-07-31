from dotenv import load_dotenv
load_dotenv()

import os, httpx

PINATA_BASE = "https://api.pinata.cloud"
API_KEY     = os.getenv("PINATA_API_KEY")
API_SECRET  = os.getenv("PINATA_SECRET_API_KEY")

async def pin_file_to_ipfs(file_bytes: bytes, filename: str) -> str:
    url = f"{PINATA_BASE}/pinning/pinFileToIPFS"
    headers = {"pinata_api_key":API_KEY,"pinata_secret_api_key":API_SECRET}
    files = {"file":(filename, file_bytes)}
    async with httpx.AsyncClient() as c:
        r = await c.post(url, files=files, headers=headers)
        r.raise_for_status()
        return f"https://gateway.pinata.cloud/ipfs/{r.json()['IpfsHash']}"
