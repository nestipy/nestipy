import { Outlet } from 'react-router-dom';
import { ThemeContext, use_app_store } from './state';



export function Layout(): JSX.Element {
  const theme = use_app_store((state) => state.theme);
  const toggleHandler = use_app_store((state) => state.toggleTheme);
  return (
    <ThemeContext.Provider value={{"theme": use_app_store((state) => state.theme), "toggle": use_app_store((state) => state.toggleTheme)}}><div className={(theme) === ("dark") ? "app-shell theme-dark" : "app-shell theme-light"}><main className="page-shell"><Outlet /></main></div></ThemeContext.Provider>
  );
}
