import React from 'react';
import type { JSX } from 'react';
import { createActions } from '../../actions.client';
import { ThemeContext, use_app_store } from '../../components/state';

const create_actions = createActions;




export default function Page(): JSX.Element {
  const theme = React.useContext(ThemeContext);
  const [status, setStatus] = React.useState("Waiting...");
  const sharedCount = use_app_store((state) => state.sharedCount);
  const incShared = use_app_store((state) => state.incShared);
  const actions = createActions();
  const loadPing = () => {
    actions.AppActions.hello({"name": "Nestipy"}).then((value) => setStatus(`Action ping: ${((value.ok) && (value.data)) || (value.error)}`));
  };
  React.useEffect(loadPing, []);
  return (
    <section className="page page-centered"><div className="page-header"><span className="pill pill-accent">Action call</span><h2 className="page-title">Action playground</h2><p className="page-subtitle">Call the backend through the generated actions and keep responses typed.</p></div><div className="simple-panel"><span className="simple-label">Latest response</span><p className="simple-status">{status}</p><button onClick={loadPing} className="btn btn-primary">Reload Action</button></div><div className="simple-panel"><span className="simple-label">Shared count</span><span className="simple-value">{use_app_store((state) => state.sharedCount)}</span><button onClick={use_app_store((state) => state.incShared)} className="btn btn-outline">Inc Shared</button></div><p className="simple-note">{`Theme: ${theme["theme"]}`}</p></section>
  );
}
