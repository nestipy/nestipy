import React from 'react';
import type { JSX } from 'react';
import { ApiClient } from '../../api/client';
import { ThemeContext, use_app_store } from '../../components/state';

export { ApiClient };




export default function Page(): JSX.Element {
  const theme = React.useContext(ThemeContext);
  const [status, setStatus] = React.useState("Waiting...");
  const sharedCount = use_app_store((state) => state.sharedCount);
  const incShared = use_app_store((state) => state.incShared);
  const api = new ApiClient({"baseUrl": ""});
  const loadPing = () => {
    api.ping().then((value) => setStatus(`API ping: ${value}`));
  };
  React.useEffect(loadPing, []);
  return (
    <section className="page"><div className="page-header"><h2 className="page-title">API Playground</h2><p className="page-subtitle">Ping the backend using the generated typed client.</p></div><div className="card api-card"><p className="card-title">{status}</p><button onClick={loadPing} className="btn">Reload API</button></div><div className="stat-card"><span className="stat-label">Shared count</span><span className="stat-value">{use_app_store((state) => state.sharedCount)}</span><button onClick={use_app_store((state) => state.incShared)} className="btn btn-outline">Inc Shared</button></div><p className="card-subtitle">{`Theme: ${theme["theme"]}`}</p></section>
  );
}
