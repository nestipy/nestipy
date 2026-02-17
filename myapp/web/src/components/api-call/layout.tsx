import { Outlet } from 'react-router-dom';




export function Layout(): JSX.Element {
  return (
    <section className="panel panel-plain"><div className=" flex flex-col gap-2 items-center justify-center"><span className="pill">Workspace</span><h3 className="panel-title">Typed Client Playground</h3><p className="panel-subtitle">This nested layout scopes tooling for /api-call routes.</p></div><div className="panel-body"><Outlet /></div></section>
  );
}
