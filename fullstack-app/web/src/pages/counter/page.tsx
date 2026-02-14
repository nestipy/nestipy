import React from 'react';
import type { JSX } from 'react';
import { useAppStore } from '../../store';
import { ThemeContext } from '../../components/layout';





export default function Page(): JSX.Element {
  const theme = React.useContext(ThemeContext);
  const [count, setCount] = React.useState(0);
  const sharedCount = useAppStore((state) => state.sharedCount);
  const incShared = useAppStore((state) => state.incShared);
  const decShared = useAppStore((state) => state.decShared);
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
  const title = React.useMemo(label, [count]);
  return (
    <section className="page"><div className="page-header"><h2 className="page-title">Counter</h2><p className="page-subtitle">Stateful hooks, memoized labels, and responsive controls.</p></div><div className="card counter-card"><div className="counter-stack"><span className="stat-label">Current value</span><span className="counter-display">{count}</span>{((count) % (2)) === (0) ? (<span className="pill">Even</span>) : (<span className="pill pill-accent">Odd</span>)}</div><div className="home-actions"><button onClick={dec} className="btn">-1</button><button onClick={inc} className="btn btn-primary">+1</button></div><p className="card-subtitle">{title}</p></div><div className="card counter-card"><div className="counter-stack"><span className="stat-label">Shared count</span><span className="counter-display">{useAppStore((state) => state.sharedCount)}</span></div><div className="home-actions"><button onClick={useAppStore((state) => state.decShared)} className="btn">-1</button><button onClick={useAppStore((state) => state.incShared)} className="btn btn-outline">+1</button></div></div><div className="stat-card"><span>Theme</span><span className="stat-value">{(theme["theme"]) === ("dark") ? "Dark" : "Light"}</span></div></section>
  );
}
