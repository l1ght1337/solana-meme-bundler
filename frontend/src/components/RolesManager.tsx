import { useEffect, useState, useContext } from 'react';
import axios from 'axios';
import { AuthContext } from './AuthContext';

export function RolesManager() {
  const { role } = useContext(AuthContext);
  const [users,setUsers] = useState<any[]>([]);
  const [newRole,setNewRole] = useState('trader');

  useEffect(()=>{
    if(role==='admin'){
      axios.get('/users').then(r=>setUsers(r.data));
    }
  },[role]);

  async function change(id:number){
    await axios.patch(`/users/${id}/role`,{new_role:newRole});
    setUsers(users.map(u=>u.id===id?{...u,role:newRole}:u));
  }

  if(role!=='admin') return null;
  return (
    <div className="mb-4 p-4 border rounded">
      <h2>User Roles</h2>
      <select value={newRole} onChange={e=>setNewRole(e.target.value)} className="mb-2">
        <option value="admin">admin</option>
        <option value="trader">trader</option>
      </select>
      <table className="w-full">
        <thead><tr><th>ID</th><th>User</th><th>Role</th><th>Action</th></tr></thead>
        <tbody>
          {users.map(u=>(
            <tr key={u.id}>
              <td>{u.id}</td><td>{u.username}</td><td>{u.role}</td>
              <td><button onClick={()=>change(u.id)} className="px-2 py-1 bg-green-500 text-white">Set {newRole}</button></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
