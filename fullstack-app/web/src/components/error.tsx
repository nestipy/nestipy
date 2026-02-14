import React from 'react';
import type { JSX } from 'react';
import { Link, isRouteErrorResponse, useRouteError } from 'react-router-dom';


export { Link };
export const use_route_error = useRouteError;
export const is_route_error_response = isRouteErrorResponse;


export function Error(): JSX.Element {
  const error = useRouteError();
  const status = isRouteErrorResponse(error) ? error.status : 500;
  const title = isRouteErrorResponse(error) ? error.statusText : 'Unexpected error';
  const message = error?.message ?? 'Something went wrong while rendering this page.';
  return (
    <section className="error-page"><div className="error-card"><span className="error-code">{isRouteErrorResponse(error) ? error.status : 500}</span><h1 className="error-title">{isRouteErrorResponse(error) ? error.statusText : 'Unexpected error'}</h1><p className="error-message">{error?.message ?? 'Something went wrong while rendering this page.'}</p><Link to="/" className="btn btn-primary">Back home</Link></div></section>
  );
}
