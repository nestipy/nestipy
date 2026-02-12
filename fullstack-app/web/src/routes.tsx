import { createBrowserRouter } from 'react-router-dom';
import Page0 from './pages/index';
import Page1 from './pages/user/page';

export const router = createBrowserRouter([
  { path: '/', element: <Page0 /> },
  { path: '/user', element: <Page1 /> }
]);
