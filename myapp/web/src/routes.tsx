import { createBrowserRouter } from 'react-router-dom';
import { Error as AppErrorBoundary } from './components/error';
import { NotFound } from './components/notfound';
import { Layout as LayoutApicall } from './components/api-call/layout';
import { Layout } from './components/layout';
import Page0 from './pages/index';
import Page1 from './pages/api-call/page';
import Page2 from './pages/counter/page';

export const routes = [
  {
    path: '/',
    element: <Layout />,
    errorElement: <AppErrorBoundary />,
    children: [
      { index: true, element: <Page0 /> },
      { path: 'counter', element: <Page2 /> },
  {
    path: 'api-call',
    element: <LayoutApicall />,
    children: [
      { index: true, element: <Page1 /> }
    ],
  },
      { path: '*', element: <NotFound /> }
    ],
  }
];
export const router = createBrowserRouter(routes);
