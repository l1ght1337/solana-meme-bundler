import { useContext } from 'react';
import { AuthContext } from '../components/AuthContext';
import { LoginForm } from '../components/LoginForm';
import { RolesManager } from '../components/RolesManager';
import { MainWalletBalance } from '../components/MainWalletBalance';
import { SettingsManager } from '../components/SettingsManager';
import { SimulatorsManager } from '../components/SimulatorsManager';
import { TokenCreator } from '../components/TokenCreator';
import { TradeControls } from '../components/TradeControls';
import { PnLDashboard } from '../components/PnLDashboard';
import { TradersList } from '../components/TradersList';
import { Dashboard }    from '../components/Dashboard';

export default function Home() {
  const { token, role } = useContext(AuthContext);
  if (!token) return <LoginForm/>;

  return (
    <div className="container mx-auto p-4">
      {role === 'admin' && <RolesManager/>}
      <MainWalletBalance/>
      <SettingsManager/>
      <SimulatorsManager/>
      <TokenCreator/>
      <TradeControls/>
      <PnLDashboard/>
      <TradersList onSelect={()=>{}}/>
      <Dashboard filterTrader="" />
    </div>
  );
}
