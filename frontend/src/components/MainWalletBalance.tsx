import { useEffect, useState } from 'react';
import axios from 'axios';

export function MainWalletBalance() {
  const [bal,setBal] = useState(null);
  useEffect(()=>{
    axios.get('/main-wallet/balance').then(r=>setBal(r.data.balance_sol));
  },[]);
  return (
    <div className="mb-4 p-2 border rounded">
      Main Wallet Balance: {bal===null?'…':`${bal.toFixed(4)} SOL`}
    </div>
  );
}
