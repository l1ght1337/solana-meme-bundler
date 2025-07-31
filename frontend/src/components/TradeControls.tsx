import { useWallet } from '@solana/wallet-adapter-react';
import { Connection, Transaction } from '@solana/web3.js';
import axios from 'axios';
import { useState } from 'react';

export function TradeControls() {
  const { publicKey, sendTransaction } = useWallet();
  const [mint,setMint]=useState(''),[qty,setQty]=useState(0);

  async function onSwap(side:'buy'|'sell'|'sell-all') {
    if(!publicKey) return alert('Connect wallet');
    const conn=new Connection(process.env.NEXT_PUBLIC_RPC);
    const { data } = await axios.post(`/trade/${side}`, { mint_address: mint, quantity: qty });
    const tx=Transaction.from(Buffer.from(data.swapTransaction,'base64'));
    const sig=await sendTransaction(tx,conn);
    await conn.confirmTransaction(sig);
    alert(`${side} done: ${sig}`);
  }

  return (
    <div className="mb-4 p-4 border rounded">
      <h2>Trade</h2>
      <input placeholder="Mint address" onChange={e=>setMint(e.target.value)} className="block mb-2"/>
      <input type="number" placeholder="Quantity" onChange={e=>setQty(+e.target.value)} className="block mb-4"/>
      <button onClick={()=>onSwap('buy')} className="mr-2">Buy</button>
      <button onClick={()=>onSwap('sell')} className="mr-2">Sell</button>
      <button onClick={()=>onSwap('sell-all')}>Sell All</button>
    </div>
  );
}
