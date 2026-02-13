import { createBrowserRouter } from 'react-router-dom';
import { Layout as LayoutApicall } from './components/api-call/layout';
import { Layout } from './components/layout';
import Page0 from './pages/index';
import Page1 from './pages/api-call@/page';
import Page2 from './pages/counter/page';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <Layout />,
    children: [
      { index: true, element: <Page0 /> },
      { path: 'api-call@', element: <Page1 /> },
      { path: 'counter', element: <Page2 /> },
  {
    path: 'api-call',
    element: <LayoutApicall />,
    children: [

    ],
  },
    ],
  },
]);
