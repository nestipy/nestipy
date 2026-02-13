import React from 'react';
import type { JSX } from 'react';
import { Link } from 'react-router-dom';
import { ThemeContext } from '../../components/layout';





export default function Page(): JSX.Element {
  const theme = React.useContext(ThemeContext);
  const [count, setCount] = React.useState(0);
  const increment = () => {
    setCount((count) + (1));
  };
  const decrement = () => {
    setCount((count) - (1));
  };
  const label = () => {
    return `Count: ${count}`;
  };
  const links = [];
  const inc = React.useCallback(increment, [count]);
  const dec = React.useCallback(decrement, [count]);
  const title = React.useMemo(label, [count]);
  return (
    <section className="page"><nav className="home-nav">{[{"label": "Home", "to": "/"}, {"label": "Counter", "to": "/counter"}, {"label": "API", "to": "/api-call"}].map((item) => (<Link to={item["to"]} key={item["to"]} className="nav-link">{item["label"]}</Link>))}</nav><div className="space-y-2 text-center"><h2 className="text-2xl font-semibold text-slate-100">Counter</h2><p className="text-sm text-slate-400">Use hooks to keep state and memoize values.</p></div><div className="home-card"><p className="text-base text-slate-200">{title}</p>{((count) % (2)) === (0) ? (<span className="text-xs text-emerald-400">Even</span>) : (<span className="text-xs text-amber-400">Odd</span>)}<div className="home-actions"><button onClick={inc} className="btn btn-primary">+1</button><button onClick={dec} className="btn">-1</button></div></div><p className="text-xs text-slate-500">{`Theme: ${theme["theme"]}`}</p></section>
  );
}
