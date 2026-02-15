import React from 'react';
import { renderToString } from 'react-dom/server.browser';
import { RouterProvider, createMemoryRouter } from 'react-router-dom';
import { routes } from './routes';

export function render(url: string) {
  const router = createMemoryRouter(routes, { initialEntries: [url] });
  const html = renderToString(<RouterProvider router={router} />);
  return { html };
}

export default { render };
