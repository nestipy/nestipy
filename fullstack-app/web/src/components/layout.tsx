import React from 'react';
import type { JSX } from 'react';
import { Outlet } from 'react-router-dom';


export const ThemeContext = React.createContext({"theme": "dark", "toggle": null});


export function Layout(): JSX.Element {
  const [theme, setTheme] = React.useState("dark");
  const toggleTheme = () => {
    setTheme(((theme) === ("dark")) ? ("light") : ("dark"));
  };
  const toggleHandler = React.useCallback(toggleTheme, [theme]);
  return (
    <ThemeContext.Provider value={{"theme": theme, "toggle": toggleHandler}}><div className="min-h-screen flex flex-col"><header className="flex items-center justify-between gap-4 border-b border-slate-900 px-6 py-4"><div className="flex items-center gap-3"><span className="text-xs uppercase tracking-[0.35em] text-slate-400">Nestipy Web</span><span className="text-xs text-slate-500">Python-first UI</span></div><button onClick={toggleHandler} className="rounded-full border border-slate-800 bg-slate-900/70 px-4 py-2 text-xs font-semibold text-slate-200 hover:bg-slate-800">{`Switch to ${((theme) === ("dark")) ? ("light") : ("dark")} mode`}</button></header><main className="flex-1 px-6"><Outlet /></main></div></ThemeContext.Provider>
  );
}
