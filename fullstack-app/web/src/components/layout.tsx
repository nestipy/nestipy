import React from 'react';
import type { JSX } from 'react';
import { Link, Outlet } from 'react-router-dom';
import { useAppStore } from '../store';


export const ThemeContext = React.createContext({"theme": "light", "toggle": null});


export function Layout(): JSX.Element {
  const theme = useAppStore((state) => state.theme);
  const toggleHandler = useAppStore((state) => state.toggleTheme);
  const sharedCount = useAppStore((state) => state.sharedCount);
  const navLinks = [];
  return (
    <ThemeContext.Provider value={{"theme": useAppStore((state) => state.theme), "toggle": useAppStore((state) => state.toggleTheme)}}><div className={(theme) === ("dark") ? "app-shell theme-dark" : "app-shell theme-light"}><header className="topbar"><div className="brand-block"><div className="brand"><span className="brand-name">Nestipy</span><span className="brand-pill">Web</span></div><p className="brand-subtitle">Python-first UI and typed APIs.</p></div><nav className="nav">{[{"label": "Home", "to": "/"}, {"label": "Counter", "to": "/counter"}, {"label": "API", "to": "/api-call"}].map((item) => (<Link to={item["to"]} key={item["to"]} className="nav-link">{item["label"]}</Link>))}</nav><div className="header-actions"><button onClick={useAppStore((state) => state.toggleTheme)} className="btn btn-ghost">{(theme) === ("dark") ? "Switch to light" : "Switch to dark"}</button><span className="shared-pill">{`Shared ${useAppStore((state) => state.sharedCount)}`}</span><span className="theme-label">{(theme) === ("dark") ? "Dark mode" : "Light mode"}</span></div></header><main className="container"><Outlet /></main><footer className="footer"><span>Nestipy Web</span><span>•</span><span>Fullstack scaffold</span></footer></div></ThemeContext.Provider>
  );
}
