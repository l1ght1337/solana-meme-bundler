import '../styles/globals.css';
import { AuthProvider } from '../components/AuthContext';
import { WalletConnector } from '../components/WalletConnector';

export default function App({ Component, pageProps }) {
  return (
    <AuthProvider>
      <WalletConnector>
        <Component {...pageProps}/>
      </WalletConnector>
    </AuthProvider>
  );
}
