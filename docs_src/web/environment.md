# Environment Variables

This page explains the environment variables used by Nestipy Web and shows when you should set them.

## Dev Server Defaults

These variables affect `web:dev` and help avoid repeating CLI flags:

- `NESTIPY_WEB_BACKEND`
  - Default backend command to run alongside the web dev server.
  - Example: `NESTIPY_WEB_BACKEND="python main.py"`

- `NESTIPY_WEB_BACKEND_CWD`
  - Working directory for the backend command.
  - Example: `NESTIPY_WEB_BACKEND_CWD=./backend`

- `NESTIPY_WEB_PROXY`
  - Backend URL used by Vite proxy (e.g. `http://127.0.0.1:8001`).

- `NESTIPY_WEB_PROXY_PATHS`
  - Comma‑separated list of paths to proxy to the backend.
  - Default: `/_actions,/_router,/_devtools`
  - Example: `NESTIPY_WEB_PROXY_PATHS=/_actions,/_router,/api`

## Typed Client Codegen (Dev)

These control automatic regeneration of clients while developing:

- `NESTIPY_WEB_ACTIONS_WATCH`
  - CSV of backend paths to watch for action schema updates.
  - When set, **polling is disabled** and schema is refetched only on changes.
  - Example: `NESTIPY_WEB_ACTIONS_WATCH=./src,./app`

- `NESTIPY_WEB_ACTIONS_POLL`
  - Poll interval (seconds) for `/_actions/schema` when watch is not set.
  - Default: `1.0`

- `NESTIPY_WEB_ROUTER_POLL`
  - Poll interval (seconds) for `/_router/spec` when watch is not set.
  - Default: `2.0`

- `NESTIPY_WEB_ROUTER_SPEC_URL`
  - Full URL to `/_router/spec` when auto‑generating HTTP clients.
  - Example: `NESTIPY_WEB_ROUTER_SPEC_URL=http://127.0.0.1:8001/_router/spec`

- `NESTIPY_WEB_ROUTER_OUTPUT`
  - Output path for the generated HTTP client.
  - Default: `web/src/api/client.ts`

## Production Serving

These variables are used when the backend serves the built frontend:

- `NESTIPY_WEB_DIST`
  - Directory that contains the Vite build output (e.g. `web/dist`).

- `NESTIPY_WEB_STATIC_PATH`
  - Mount path for static files (default `/`).

- `NESTIPY_WEB_STATIC_INDEX`
  - Index file name (default `index.html`).

- `NESTIPY_WEB_STATIC_FALLBACK=1`
  - Enable SPA fallback for HTML requests when a file is not found.

## Quick Example

```bash
export NESTIPY_WEB_BACKEND="python main.py"
export NESTIPY_WEB_PROXY="http://127.0.0.1:8001"
export NESTIPY_WEB_ACTIONS_WATCH=./src

nestipy run web:dev --vite
```
