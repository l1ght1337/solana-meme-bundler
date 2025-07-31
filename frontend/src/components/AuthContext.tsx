import { createContext, useState, useEffect } from 'react';
import axios from 'axios';

export const AuthContext = createContext<any>(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState<string|null>(null);
  const [role, setRole]   = useState<string|null>(null);

  useEffect(()=>{
    axios.interceptors.request.use(cfg=>{
      if(token) cfg.headers.Authorization = `Bearer ${token}`;
      return cfg;
    });
  },[token]);

  return (
    <AuthContext.Provider value={{ token, setToken, role, setRole }}>
      {children}
    </AuthContext.Provider>
  );
}
