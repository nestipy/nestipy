import React from 'react';
import type { JSX } from 'react';
import { Link } from 'react-router-dom';
import { createActions } from '../actions.client';
import { ApiClient } from '../api/client';
import { ThemeContext } from '../components/layout';





export default function Page(): JSX.Element {
  const theme = React.useContext(ThemeContext);
  const [message, setMessage] = React.useState("Loading...");
  const [ping, setPing] = React.useState("Loading...");
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
  const links = [];
  const reloadAction = React.useCallback(loadAction, []);
  const reloadPing = React.useCallback(loadPing, []);
  const actionLabel = React.useMemo(label, [message]);
  React.useEffect(loadAction, []);
  React.useEffect(loadPing, []);
  return (
    <section className="home"><div className="logo-row"><img src="/nestipy.png" alt="Nestipy logo" className="logo nestipy" /><img src="/react.svg" alt="React logo" className="logo react" /><img src="/vite.svg" alt="Vite logo" className="logo vite" /></div><h1 className="home-title">Nestipy Web + React + Vite</h1><p className="home-subtitle">Build fullstack apps with Python-first UI, typed actions, and fast HMR.</p><div className="home-actions"><button onClick={reloadAction} className="btn btn-primary">Reload Action</button><button onClick={reloadPing} className="btn">Reload API</button></div><div className="home-card"><p className="text-sm">{actionLabel}</p><p className="text-xs text-slate-400">{(ping) === ("Loading...") ? "Loading API ping..." : `API ping: ${ping}`}</p><p className="text-xs text-slate-500">{`Theme: ${theme["theme"]}`}</p></div><nav className="home-nav">{[{"label": "Home", "to": "/"}, {"label": "Counter", "to": "/counter"}, {"label": "API", "to": "/api-call"}].map((item) => (<Link to={item["to"]} key={item["to"]} className="nav-link">{item["label"]}</Link>))}</nav></section>
  );
}
