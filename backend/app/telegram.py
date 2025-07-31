from dotenv import load_dotenv
load_dotenv()

import os, httpx

BOT = os.getenv("TELEGRAM_BOT_TOKEN")
CID = os.getenv("TELEGRAM_CHAT_ID")

async def notify(text: str):
    if not BOT or not CID:
        return
    url = f"https://api.telegram.org/bot{BOT}/sendMessage"
    await httpx.post(url, json={"chat_id": CID, "text": text})
