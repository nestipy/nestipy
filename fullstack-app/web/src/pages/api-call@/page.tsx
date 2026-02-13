import React from 'react';
import type { JSX } from 'react';
import { Link } from 'react-router-dom';
import { ApiClient } from '../../api/client';
import { ThemeContext } from '../../components/layout';





export default function Page(): JSX.Element {
  const theme = React.useContext(ThemeContext);
  const [status, setStatus] = React.useState("Waiting...");
  const api = new ApiClient({"baseUrl": ""});
  const loadPing = () => {
    api.ping().then((value, ...DEFAULT) => setStatus(`API ping: ${value}`));
  };
  const links = [];
  React.useEffect(loadPing, []);
  return (
    <section className="page"><nav className="home-nav">{[{"label": "Home", "to": "/"}, {"label": "Counter", "to": "/counter"}, {"label": "API", "to": "/api-call"}].map((item) => (<Link key={item["to"]} to={item["to"]} className="nav-link">{item["label"]}</Link>))}</nav><div className="space-y-2 text-center"><h2 className="text-2xl font-semibold text-slate-100">API Playground</h2><p className="text-sm text-slate-400">Ping the backend using the generated typed client.</p></div><div className="home-card"><p className="text-base text-slate-200">{status}</p><button onClick={loadPing} className="btn">Reload API</button></div><p className="text-xs text-slate-500">{`Theme: ${theme["theme"]}`}</p></section>
  );
}
