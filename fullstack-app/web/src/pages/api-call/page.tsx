import React from 'react';
import type { JSX } from 'react';
import { ApiClient } from '../../api/client';
import { ThemeContext } from '../../components/layout';





export default function Page(): JSX.Element {
  const theme = React.useContext(ThemeContext);
  const [status, setStatus] = React.useState("Waiting...");
  const api = new ApiClient({"baseUrl": ""});
  const loadPing = () => {
    api.ping().then((value, ...DEFAULT) => setStatus(`API ping: ${value}`));
  };
  React.useEffect(loadPing, []);
  return (
    <section className="page"><div className="page-header"><h2 className="page-title">API Playground</h2><p className="page-subtitle">Ping the backend using the generated typed client.</p></div><div className="card api-card"><p className="card-title">{status}</p><button onClick={loadPing} className="btn">Reload API</button></div><p className="card-subtitle">{`Theme: ${theme["theme"]}`}</p></section>
  );
}
