import { useContext, useState } from 'react';
import axios from 'axios';
import { AuthContext } from './AuthContext';

export function LoginForm() {
  const { setToken, setRole } = useContext(AuthContext);
  const [user,setUser] = useState('');
  const [pass,setPass] = useState('');

  async function login(){
    const r = await axios.post('/token',
      new URLSearchParams({username:user,password:pass}),
      { headers:{'Content-Type':'application/x-www-form-urlencoded'} }
    );
    setToken(r.data.access_token);
    const pl = JSON.parse(atob(r.data.access_token.split('.')[1]));
    setRole(pl.role);
  }

  return (
    <div className="p-4">
      <input placeholder="Username" value={user} onChange={e=>setUser(e.target.value)} className="block mb-2"/>
      <input placeholder="Password" type="password" value={pass} onChange={e=>setPass(e.target.value)} className="block mb-4"/>
      <button onClick={login} className="px-4 py-2 bg-blue-500 text-white rounded">Login</button>
    </div>
  );
}
