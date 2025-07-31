import { useWallet } from '@solana/wallet-adapter-react';
import { Connection, Transaction } from '@solana/web3.js';
import axios from 'axios';
import { useState } from 'react';

export function TradeControls({ mint }: { mint: string }) {
  const { publicKey, sendTransaction } = useWallet();
  const [qty,setQty] = useState(0);

  async function onSwap(side:'buy'|'sell'|'sell-all') {
    if (!publicKey) return alert('Connect wallet');
    const conn = new Connection(process.env.NEXT_PUBLIC_RPC!);
    const { data } = await axios.post(`/trade/${side}`, { mint_address: mint, quantity: qty });
    const tx = Transaction.from(Buffer.from(data.swapTransaction, 'base64'));
    const sig = await sendTransaction(tx, conn);
    await conn.confirmTransaction(sig);
    alert(`${side} done: ${sig}`);
  }

  return (
    <div className="mb-4 p-4 border rounded">
      <h2>Trade</h2>
      <input
        placeholder="Quantity"
        type="number"
        value={qty}
        onChange={e=>setQty(+e.target.value)}
        className="block mb-2 p-1 border"
      />
      <button onClick={()=>onSwap('buy')} className="mr-2 px-3 py-1 bg-green-500 text-white rounded">Buy</button>
      <button onClick={()=>onSwap('sell')} className="mr-2 px-3 py-1 bg-yellow-500 text-white rounded">Sell</button>
      <button onClick={()=>onSwap('sell-all')} className="px-3 py-1 bg-red-500 text-white rounded">Sell All</button>
    </div>
  );
}
