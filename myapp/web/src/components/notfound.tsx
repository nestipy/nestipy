import React from 'react';
import type { JSX } from 'react';
import { Link } from 'react-router-dom';


export { Link };


export function NotFound(): JSX.Element {
  return (
    <section className="error-minimal"><div className="error-minimal-content"><div className="error-minimal-row"><span className="error-minimal-code">404</span><div className="error-minimal-divider" /><div className="error-minimal-text"><h1 className="error-minimal-title">This page could not be found.</h1><p className="error-minimal-message">The route you requested doesn’t exist yet. Check your navigation or update routes.</p></div></div><div className="error-minimal-actions"><Link to="/" className="error-minimal-link">Back to home</Link></div></div></section>
  );
}
