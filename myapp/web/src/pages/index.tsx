import React from 'react';
import type { JSX } from 'react';
import { Link } from 'react-router-dom';
import { createActions } from '../actions.client';
import { createApiClient } from '../api/client';
import { ThemeContext, use_app_store } from '../components/store';





export default function Page(): JSX.Element {
  const theme = React.useContext(ThemeContext);
  const [message, setMessage] = React.useState("Loading...");
  const [ping, setPing] = React.useState("Loading...");
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
    api.AppController.ping().then(onPing);
  };
  const toggleHandler = theme["toggle"];
  const reloadAction = React.useCallback(loadAction, []);
  const reloadPing = React.useCallback(loadPing, []);
  const actionLabel = React.useMemo(() => `Action says: ${message}`, [message]);
  React.useEffect(loadAction, []);
  React.useEffect(loadPing, []);
  return (
    <section className="home-next"><div className="flex flex-row gap-8 "><span className="start-pill">Get started by editing app/page.py</span><div className="center-right flex flex-col gap-2"><button className="btn-ghost">{toggleHandler ? (<button onClick={toggleHandler} className="ghost-btn">{(theme["theme"]) === ("dark") ? "Switch to light" : "Switch to dark"}</button>) : (<span className="theme-chip">{(theme["theme"]) === ("dark") ? "Dark" : "Light"}</span>)}</button></div></div><div className="hero-wrap"><div className="hero-center"><img src="/nestipy.png" alt="Nestipy" className="hero-logo" width="100" height="100" /><h1 className="hero-logo">Nestipy</h1><p className="hero-sub">Full-stack Python framework with typed actions and React UI.</p></div></div><div className="status-row"><div className="status-item"><span className="status-label">Action</span><span className="status-value">{actionLabel}</span></div><div className="status-item"><span className="status-label">API</span><span className="status-value">{(ping) === ("Loading...") ? "Connecting to API..." : `API ping: ${ping}`}</span></div></div><div className="status-actions"><button onClick={reloadAction} className="btn-ghost">Reload Action</button><button onClick={reloadPing} className="btn-ghost">Reload API</button><button onClick={incShared} className="btn-ghost">Inc Shared</button></div><div className="link-grid">{[{"title": "Docs", "desc": "Find in-depth guides for the Nestipy stack.", "href": "https://nestipy.vercel.app", "external": true}, {"title": "Counter", "desc": "Explore hooks and shared state updates.", "href": "/counter"}, {"title": "API Playground", "desc": "Call typed HTTP clients from Python UI.", "href": "/api-call"}, {"title": "Actions", "desc": "Trigger typed RPC actions instantly.", "href": "/action-call"}].map((item) => ((("external") in (item)) && (item["external"]) ? (<a href={item["href"]} target="_blank" rel="noreferrer" className="link-card-wrap" key={item["title"]}><div className="link-card"><h3 className="link-title">{`${item["title"]} →`}</h3><p className="link-desc">{item["desc"]}</p></div></a>) : (<Link to={item["href"]} className="link-card-wrap" key={item["title"]}><div className="link-card"><h3 className="link-title">{`${item["title"]} →`}</h3><p className="link-desc">{item["desc"]}</p></div></Link>)))}</div></section>
  );
}
