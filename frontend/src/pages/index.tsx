import { useContext, useState } from 'react';
import { AuthContext } from '../components/AuthContext';
import { LoginForm } from '../components/LoginForm';
import { RolesManager } from '../components/RolesManager';
import { MainWalletBalance } from '../components/MainWalletBalance';
import { SettingsManager } from '../components/SettingsManager';
import { SimulatorsManager } from '../components/SimulatorsManager';
import { PnLDashboard } from '../components/PnLDashboard';
import { TradersList } from '../components/TradersList';
import { Dashboard }    from '../components/Dashboard';

export default function Home() {
  const { token, role } = useContext(AuthContext);
  const [mint, setMint] = useState<string|null>(null);

  if (!token) return <LoginForm/>;

  return (
    <div className="container mx-auto p-4">
      {role === 'admin' && <RolesManager/>}
      <MainWalletBalance/>
      <SettingsManager/>
      {!mint
        ? <div className="mb-4 p-4 border rounded">
            <h2>Use Existing Token</h2>
            <input
              placeholder="Mint address"
              className="w-full p-2 border mb-2"
              onChange={e=>setMint(e.target.value.trim())}
            />
          </div>
        : <>
            <SimulatorsManager mint={mint}/>
            <PnLDashboard/>
            <TradersList onSelect={()=>{}}/>
            <Dashboard filterTrader=""/>
          </>
      }
    </div>
  );
}
