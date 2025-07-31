import { useEffect, useState } from 'react';
import axios from 'axios';

export function TradersList({ onSelect }: { onSelect:(s:string)=>void }) {
  const [list, setList] = useState<any[]>([]);
  useEffect(()=> axios.get('/simulators').then(r=> setList(r.data)), []);
  return (
    <div className="mb-4">
      <label>Trader:</label>
      <select onChange={e=>onSelect(e.target.value)} className="ml-2">
        <option value="">All</option>
        {list.map(s=><option key={s.id} value={s.id}>Trader{s.id}</option>)}
      </select>
    </div>
  );
}
