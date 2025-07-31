import { useEffect, useState } from 'react';
import axios from 'axios';

export function PnLDashboard() {
  const [pnl,setPnl] = useState<{ total:number, per:Record<number,number> }>({ total:0, per:{} });

  useEffect(()=>{
    axios.get('/pnl-summary').then(r=>
      setPnl({ total: r.data.total_realized_pnl, per: r.data.per_simulator })
    );
  },[]);

  return (
    <div className="p-4 border rounded mb-4">
      <h2>Total PnL: {pnl.total.toFixed(4)} SOL</h2>
      <ul>
        {Object.entries(pnl.per).map(([id,val])=>(
          <li key={id}>Trader{id}: {val.toFixed(4)} SOL</li>
        ))}
      </ul>
    </div>
  );
}
