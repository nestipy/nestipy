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
  const details = error?.stack ?? '';
  return (
    <section className="error-minimal"><div className="error-minimal-content"><div className="error-minimal-row"><span className="error-minimal-code">{isRouteErrorResponse(error) ? error.status : 500}</span><div className="error-minimal-divider" /><div className="error-minimal-text"><h1 className="error-minimal-title">{isRouteErrorResponse(error) ? error.statusText : 'Unexpected error'}</h1><p className="error-minimal-message">{error?.message ?? 'Something went wrong while rendering this page.'}</p></div></div><div className="error-details"><h2 className="error-details-title">Details</h2><pre className="error-details-body">{error?.stack ?? ''}</pre></div><div className="error-minimal-actions"><Link to="/" className="error-minimal-link">Back to home</Link></div></div></section>
  );
}
