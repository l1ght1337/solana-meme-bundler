from dotenv import load_dotenv
load_dotenv()

import os, base58
from solana.rpc.async_api import AsyncClient
from solana.keypair import Keypair
from solana.transaction import Transaction
from solana.system_program import transfer, TransferParams
from solana.publickey import PublicKey

RPC_URL = os.getenv("SOLANA_RPC_URL")

async def get_client():
    return AsyncClient(RPC_URL)

def load_keypair(secret_b58: str) -> Keypair:
    return Keypair.from_secret_key(base58.b58decode(secret_b58))
