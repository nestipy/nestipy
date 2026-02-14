import React from 'react';
import type { JSX } from 'react';
import { Link } from 'react-router-dom';
import { createActions } from '../actions.client';
import { createApiClient } from '../api/client';
import { ThemeContext, use_app_store } from '../components/state';

const __ssr__ = true;
const create_actions = createActions;
const create_api_client = createApiClient;




export default function Page(): JSX.Element {
  const theme = React.useContext(ThemeContext);
  const [message, setMessage] = React.useState("Loading...");
  const [ping, setPing] = React.useState("Loading...");
  const sharedCount = use_app_store((state) => state.sharedCount);
  const incShared = use_app_store((state) => state.incShared);
  const actions = createActions();
  const api = createApiClient();
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
    api.App.ping().then(onPing);
  };
  const features = [];
  const stats = [];
  const reloadAction = React.useCallback(loadAction, []);
  const reloadPing = React.useCallback(loadPing, []);
  const actionLabel = React.useMemo(() => `Action says: ${message}`, [message]);
  React.useEffect(loadAction, []);
  React.useEffect(loadPing, []);
  return (
    <section className="home"><div className="hero-card"><div className="pill-row"><span className="pill">Fullstack starter</span><span className="pill pill-accent">Nestipy + React + Vite</span></div><h1 className="hero-title">Build modern web experiences in Python.</h1><p className="hero-subtitle">Nestipy Web turns Python UI into React, ships typed actions and API clients, and keeps everything hot in Vite.</p><div className="hero-actions"><Link to="/counter" className="btn btn-primary">View Counter</Link><Link to="/api-call" className="btn btn-outline">API Playground</Link></div></div><div className="logo-row"><a href="https://nestipy.vercel.app" target="_blank" rel="noreferrer" className="logo-link"><img src="/nestipy.png" alt="Nestipy logo" className="logo nestipy" /></a><a href="https://react.dev" target="_blank" rel="noreferrer" className="logo-link"><img src="/react.svg" alt="React logo" className="logo react" /></a><a href="https://vitejs.dev" target="_blank" rel="noreferrer" className="logo-link"><img src="/vite.svg" alt="Vite logo" className="logo vite" /></a></div><div className="card status-card"><div className="card-content"><p className="card-title">{actionLabel}</p><p className="card-subtitle">{(ping) === ("Loading...") ? "Connecting to API..." : `API ping: ${ping}`}</p></div><div className="home-actions"><button onClick={reloadAction} className="btn btn-primary">Reload Action</button><button onClick={reloadPing} className="btn">Reload API</button><button onClick={use_app_store((state) => state.incShared)} className="btn btn-outline">Inc Shared</button></div></div><div className="stat-grid">{[{"label": "Theme", "value": (theme["theme"]) === ("dark") ? "Dark" : "Light"}, {"label": "Shared", "value": `#${use_app_store((state) => state.sharedCount)}`}, {"label": "Action", "value": ((message) !== ("Loading...")) ? ("Live") : ("Booting")}, {"label": "API", "value": ((ping) !== ("Loading...")) ? ("Ready") : ("Syncing")}].map((item) => (<div className="stat-card" key={item["label"]}><span className="stat-label">{item["label"]}</span><span className="stat-value">{item["value"]}</span></div>))}</div><div className="feature-grid">{[{"title": "Python-first components", "desc": "Compose UI in Python and compile to TSX for Vite."}, {"title": "Typed actions + API", "desc": "Generate clients for providers and HTTP routes automatically."}, {"title": "Instant feedback loop", "desc": "Hot reload + schema regen keeps the stack synchronized."}].map((item) => (<div className="card feature-card" key={item["title"]}><h3 className="feature-title">{item["title"]}</h3><p className="feature-desc">{item["desc"]}</p></div>))}</div></section>
  );
}
