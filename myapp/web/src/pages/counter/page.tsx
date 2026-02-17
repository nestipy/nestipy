import React from 'react';
import type { JSX } from 'react';
import { use_app_store } from '../../components/store';





export default function Page(): JSX.Element {
  const [count, setCount] = React.useState(0);
  const sharedCount = use_app_store((state) => state.sharedCount);
  const incShared = use_app_store((state) => state.incShared);
  const decShared = use_app_store((state) => state.decShared);
  const increment = () => {
    setCount((count) + (1));
  };
  const decrement = () => {
    setCount((count) - (1));
  };
  const label = () => {
    return `Count: ${count}`;
  };
  const inc = React.useCallback(increment, [count]);
  const dec = React.useCallback(decrement, [count]);
  return (
    <section className="page page-centered"><div className="page-header"><span className="pill">Interactive demo</span><h2 className="page-title">Counter lab</h2><p className="page-subtitle">Stateful hooks, memoized labels, and shared store updates in one place.</p></div><div className="simple-grid"><div className="simple-panel"><span className="simple-label">Local count</span><span className="counter-display">{count}</span><div className="home-actions"><button onClick={dec} className="btn btn-outline">-1</button><button onClick={inc} className="btn btn-primary">+1</button></div></div><div className="simple-panel"><span className="simple-label">Shared count</span><span className="counter-display">{sharedCount}</span><div className="home-actions"><button onClick={decShared} className="btn">-1</button><button onClick={incShared} className="btn btn-outline">+1</button></div></div></div></section>
  );
}
