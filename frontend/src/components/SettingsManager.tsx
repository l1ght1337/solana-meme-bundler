import { useEffect, useState } from 'react';
import axios from 'axios';

export function SettingsManager() {
  const [settings,setSettings] = useState({});
  const [form,setForm] = useState({});
  useEffect(()=>{
    axios.get('/settings').then(r=>{ setSettings(r.data); setForm(r.data); });
  },[]);
  async function save(){
    const r=await axios.patch('/settings',form);
    setSettings(r.data);
    alert('Saved');
  }
  return (
    <div className="mb-4 p-4 border rounded">
      <h2>Global Settings</h2>
      {['sim_min_interval','sim_max_interval','sim_min_qty','sim_max_qty'].map(k=>(
        <div key={k}>
          <label>{k}:</label>
          <input type="number" step="0.1"
            value={form[k]||0}
            onChange={e=>setForm({...form,[k]:parseFloat(e.target.value)})}/>
        </div>
      ))}
      <button onClick={save}>Save</button>
    </div>
  );
}
