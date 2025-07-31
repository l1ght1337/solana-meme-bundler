from dotenv import load_dotenv
load_dotenv()

import os, base58
from solana.rpc.async_api import AsyncClient
from solana.keypair import Keypair
from solana.transaction import Transaction
from solana.system_program import CreateAccountParams, create_account, TransferParams, transfer
from solana.publickey import PublicKey
from spl.token.instructions import initialize_mint, InitializeMintParams

RPC_URL = os.getenv("SOLANA_RPC_URL")

async def get_client():
    return AsyncClient(RPC_URL)

def load_keypair(secret_b58: str) -> Keypair:
    return Keypair.from_secret_key(base58.b58decode(secret_b58))

async def create_mint_account(payer: Keypair, mint: Keypair, decimals: int):
    client = await get_client()
    rent = await client.get_minimum_balance_for_rent_exemption(82)
    tx = Transaction().add(
      create_account(CreateAccountParams(
        from_pubkey=payer.public_key,
        new_account_pubkey=mint.public_key,
        lamports=rent,
        space=82,
        program_id=PublicKey("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
      ))
    ).add(
      initialize_mint(InitializeMintParams(
        decimals=decimals,
        mint=mint.public_key,
        mint_authority=payer.public_key,
        freeze_authority=payer.public_key
      ))
    )
    resp = await client.send_transaction(tx, payer, mint)
    await client.close()
    return resp

async def fund_one(payer: Keypair, recipient: PublicKey, lamports: int):
    client = await get_client()
    tx = Transaction().add(
      transfer(TransferParams(
        from_pubkey=payer.public_key,
        to_pubkey=recipient,
        lamports=lamports
      ))
    )
    await client.send_transaction(tx, payer)
    await client.close()
