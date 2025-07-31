import { useEffect, useState } from 'react'; 
import axios from 'axios';

export function TradersList({ onSelect }: { onSelect: (id: string) => void }) {
  const [sims, setSims] = useState<any[]>([]);

  useEffect(()=>{
    axios.get('/simulators').then(r=>setSims(r.data));
  },[]);

  return (
    <div className="mb-4">
      <label className="mr-2">Trader:</label>
      <select onChange={e=>onSelect(e.target.value)} className="p-1 border">
        <option value="">All</option>
        {sims.map(s=><option key={s.id} value={s.id}>Trader{s.id}</option>)}
      </select>
    </div>
  );
}
