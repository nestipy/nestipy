import { Outlet } from 'react-router-dom';




export function Layout(): JSX.Element {
  return (
    <section className="rounded-3xl border border-slate-800 bg-slate-900/40 p-6"><div className="space-y-2"><p className="text-xs uppercase tracking-[0.3em] text-slate-500">API Workspace</p><h3 className="text-xl font-semibold text-slate-100">Typed Client Playground</h3><p className="text-sm text-slate-400">This section has its own nested layout.</p></div><div className="mt-6"><Outlet /></div></section>
  );
}
