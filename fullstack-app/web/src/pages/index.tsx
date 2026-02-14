import React from 'react';
import type { JSX } from 'react';
import { Link } from 'react-router-dom';
import { createActions } from '../actions.client';
import { ApiClient } from '../api/client';
import { useAppStore } from '../store';
import { ThemeContext } from '../components/layout';





export default function Page(): JSX.Element {
  const theme = React.useContext(ThemeContext);
  const [message, setMessage] = React.useState("Loading...");
  const [ping, setPing] = React.useState("Loading...");
  const sharedCount = useAppStore((state) => state.sharedCount);
  const incShared = useAppStore((state) => state.incShared);
  const actions = createActions();
  const api = new ApiClient({"baseUrl": ""});
  const onAction = (result) => {
    setMessage(((result.ok) && (result.data)) || ("Error"));
  };
  const onPing = (value) => {
    setPing(value);
  };
  const loadAction = () => {
    actions.AppActions.hello({"name": "Nestipy"}).then(onAction);
  };
  const loadPing = () => {
    api.ping().then(onPing);
  };
  const label = () => {
    return `Action says: ${message}`;
  };
  const features = [];
  const stats = [];
  const reloadAction = React.useCallback(loadAction, []);
  const reloadPing = React.useCallback(loadPing, []);
  const actionLabel = React.useMemo(label, [message]);
  React.useEffect(loadAction, []);
  React.useEffect(loadPing, []);
  return (
    <section className="home space-y-8"><div className="hero"><div className="pill-row"><span className="pill">Fullstack starter</span><span className="pill pill-accent">Nestipy + React + Vite</span></div><h1 className="hero-title">Ship Python UI with modern tooling.</h1><p className="hero-subtitle">Nestipy Web compiles Python components to React, keeps actions typed, and gives you a single fullstack workflow.</p><div className="hero-actions"><Link to="/counter" className="btn btn-primary">Explore Counter</Link><Link to="/api-call" className="btn btn-outline">Open API Playground</Link></div></div><div className="logo-row"><a href="https://nestipy.vercel.app" target="_blank" rel="noreferrer" className="logo-link"><img src="/nestipy.png" alt="Nestipy logo" className="logo nestipy" /></a><a href="https://react.dev" target="_blank" rel="noreferrer" className="logo-link"><img src="/react.svg" alt="React logo" className="logo react" /></a><a href="https://vitejs.dev" target="_blank" rel="noreferrer" className="logo-link"><img src="/vite.svg" alt="Vite logo" className="logo vite" /></a></div><p className="logo-caption">Click the logos to learn more.</p><div className="card status-card"><div className="card-content"><p className="card-title">{actionLabel}</p><p className="card-subtitle">{(ping) === ("Loading...") ? "Connecting to API..." : `API ping: ${ping}`}</p></div><div className="home-actions"><button onClick={reloadAction} className="btn btn-primary">Reload Action</button><button onClick={reloadPing} className="btn">Reload API</button><button onClick={useAppStore((state) => state.incShared)} className="btn btn-outline">Inc Shared</button></div></div><div className="feature-grid gap-4">{[{"title": "Python-first UI", "desc": "Write components in Python. Compile to TSX for Vite."}, {"title": "Typed Actions", "desc": "Call backend providers from the browser with type safety."}, {"title": "Instant Feedback", "desc": "Dev server + compiler keep your UI hot and fast."}].map((item) => (<div className="card feature-card"><h3 className="feature-title">{item["title"]}</h3><p className="feature-desc">{item["desc"]}</p></div>))}</div><div className="stat-grid gap-4">{[{"label": "Theme", "value": (theme["theme"]) === ("dark") ? "Dark" : "Light"}, {"label": "Shared", "value": `#${useAppStore((state) => state.sharedCount)}`}, {"label": "Action", "value": ((message) !== ("Loading...")) ? ("Live") : ("Booting")}, {"label": "API", "value": ((ping) !== ("Loading...")) ? ("Ready") : ("Syncing")}].map((item) => (<div className="stat-card"><span className="stat-label">{item["label"]}</span><span className="stat-value">{item["value"]}</span></div>))}</div></section>
  );
}
