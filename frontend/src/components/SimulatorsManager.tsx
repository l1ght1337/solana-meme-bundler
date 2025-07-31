import { useEffect, useState, useContext } from 'react';
import axios from 'axios';
import { AuthContext } from './AuthContext';

export function SimulatorsManager() {
  const { role } = useContext(AuthContext);
  const [sims,setSims] = useState([]);
  const [fundAmt,setFundAmt] = useState(0.1);
  useEffect(()=>load(),[]);
  async function load(){
    const r=await axios.get('/simulators'); setSims(r.data);
  }
  async function add(){ await axios.post('/simulators'); load(); }
  async function save(sim){ await axios.patch(`/simulators/${sim.id}`,sim); load(); }
  async function del(id){ await axios.delete(`/simulators/${id}`); load(); }
  async function fund(id){
    await axios.post(`/simulators/${id}/fund`,{amount_sol:fundAmt}); load();
  }

  return (
    <div className="mb-4 p-4 border rounded">
      <h2>Simulators Manager</h2>
      <button onClick={add}>Add Simulator</button>
      <div className="my-2">
        Fund Amount:
        <input className="ml-2 border p-1 w-16" type="number" step="0.01"
          value={fundAmt} onChange={e=>setFundAmt(parseFloat(e.target.value))}/>
      </div>
      <table className="w-full">
        <thead><tr>
          <th>ID</th><th>Name</th><th>Active</th><th>AvgInt</th>
          <th>VolMean</th><th>VolStd</th><th>BuyBias</th><th>LastTrade</th><th>Actions</th>
        </tr></thead>
        <tbody>
        {sims.map(s=>(
          <tr key={s.id}>
            <td>{s.id}</td>
            <td><input value={s.name} readOnly className="w-24"/></td>
            <td><input type="checkbox" checked={s.is_active}
                 onChange={e=>save({...s,is_active:e.target.checked})}/></td>
            <td><input type="number" step="0.1" value={s.avg_interval}
                 onChange={e=>save({...s,avg_interval:parseFloat(e.target.value)})}
                 className="w-16"/></td>
            <td><input type="number" step="0.1" value={s.vol_mean}
                 onChange={e=>save({...s,vol_mean:parseFloat(e.target.value)})}
                 className="w-16"/></td>
            <td><input type="number" step="0.1" value={s.vol_std}
                 onChange={e=>save({...s,vol_std:parseFloat(e.target.value)})}
                 className="w-16"/></td>
            <td><input type="number" step="0.01" value={s.buy_bias}
                 onChange={e=>save({...s,buy_bias:parseFloat(e.target.value)})}
                 className="w-16"/></td>
            <td>{s.last_trade||'–'}</td>
            <td>
              <button onClick={()=>fund(s.id)} className="mr-1 px-2 py-1 bg-indigo-500 text-white">Fund</button>
              <button onClick={()=>del(s.id)} className="px-2 py-1 bg-red-500 text-white">Del</button>
            </td>
          </tr>
        ))}
        </tbody>
      </table>
    </div>
  );
}
