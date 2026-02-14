import React from 'react';
import { createRoot, hydrateRoot } from 'react-dom/client';
import { RouterProvider } from 'react-router-dom';
import { fetchCsrfToken } from './actions';
import { router } from './routes';
import './index.css';

void fetchCsrfToken().catch(() => undefined);

const rootEl = document.getElementById('root');
const app = (
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>
);
if (rootEl) {
  if (rootEl.hasChildNodes()) {
    hydrateRoot(rootEl, app);
  } else {
    createRoot(rootEl).render(app);
  }
}
