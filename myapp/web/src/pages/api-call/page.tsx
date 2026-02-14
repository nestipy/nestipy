import React from 'react';
import type { JSX } from 'react';
import { createApiClient } from '../../api/client';
import { ThemeContext, use_app_store } from '../../components/state';

const __ssr__ = true;
const create_api_client = createApiClient;




export default function Page(): JSX.Element {
  const theme = React.useContext(ThemeContext);
  const [status, setStatus] = React.useState("Waiting...");
  const sharedCount = use_app_store((state) => state.sharedCount);
  const incShared = use_app_store((state) => state.incShared);
  const api = createApiClient();
  const loadPing = () => {
    api.App.ping().then((value) => setStatus(`API ping: ${value}`));
  };
  React.useEffect(loadPing, []);
  return (
    <section className="page"><div className="page-header"><span className="pill pill-accent">Typed client</span><h2 className="page-title">API playground</h2><p className="page-subtitle">Call the backend through the generated client and keep responses typed.</p></div><div className="card api-card"><p className="card-title">{status}</p><button onClick={loadPing} className="btn btn-primary">Reload API</button></div><div className="stat-row"><div className="stat-card"><span className="stat-label">Shared count</span><span className="stat-value">{use_app_store((state) => state.sharedCount)}</span></div><button onClick={use_app_store((state) => state.incShared)} className="btn btn-outline">Inc Shared</button></div><p className="card-subtitle">{`Theme: ${theme["theme"]}`}</p></section>
  );
}
