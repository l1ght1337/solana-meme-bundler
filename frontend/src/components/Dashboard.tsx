import { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer } from 'recharts';

export function Dashboard({ filterTrader }: { filterTrader:string }) {
  const [data,setData]=useState<any[]>([]);
  useEffect(()=>{
    const ws=new WebSocket(`${window.location.origin.replace(/^http/,'ws')}/ws/portfolio`);
    ws.onmessage=e=>{
      const sims=JSON.parse(e.data);
      const agg: any = {};
      sims.filter(s=>!filterTrader||s.id==filterTrader).forEach((s:any)=>{
        const t=new Date(s.last_trade).toLocaleTimeString();
        agg[t] = agg[t]||{ time:t };
        agg[t][`T${s.id}`] = 1;
      });
      setData(Object.values(agg));
    };
    return ()=>ws.close();
  },[filterTrader]);

  if(!data.length) return <div>Loading...</div>;
  const keys=Object.keys(data[0]).filter(k=>'time'!==k);
  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data}>
        <XAxis dataKey="time"/><YAxis/><Tooltip/><Legend/>
        {keys.map(k=><Line key={k} dataKey={k}/>)}
      </LineChart>
    </ResponsiveContainer>
  );
}
