import { useEffect, useState } from 'react';
import axios from 'axios';

export function SettingsManager() {
  const [settings,setSettings] = useState<any>({});
  const [form,setForm] = useState<any>({});

  useEffect(()=>{
    axios.get('/settings').then(r=>{ setSettings(r.data); setForm(r.data); });
  },[]);

  async function save(){
    const r = await axios.patch('/settings', form);
    setSettings(r.data);
    alert('Saved');
  }

  return (
    <div className="mb-4 p-4 border rounded">
      <h2>Global Settings</h2>
      {['sim_min_interval','sim_max_interval','sim_min_qty','sim_max_qty'].map(k=>(
        <div key={k} className="mb-2">
          <label className="mr-2">{k}:</label>
          <input
            type="number" step="0.1"
            value={form[k]||0}
            onChange={e=>setForm({...form,[k]:parseFloat(e.target.value)})}
            className="border p-1 w-20"
          />
        </div>
      ))}
      <button onClick={save} className="px-4 py-2 bg-blue-500 text-white rounded">Save</button>
    </div>
  );
}
