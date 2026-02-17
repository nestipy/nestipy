# SSR (Optional)

Nestipy Web supports optional server‑side rendering. Start with CSR, then enable SSR if needed.

## Build

```bash
nestipy run web:build --vite --ssr
```

## Serve

```bash
nestipy start --web --ssr
```

## Runtimes

SSR runs on either:

- `jsrun` (default if available)
- `node` (fallback when jsrun is unavailable)

Force a runtime:

```bash
NESTIPY_WEB_SSR_RUNTIME=node nestipy start --web --ssr
```

Optional env flags:

- `NESTIPY_WEB_SSR=1`
- `NESTIPY_WEB_SSR_RUNTIME=jsrun|node|auto`
- `NESTIPY_WEB_SSR_ENTRY=web/dist/ssr/entry-server.js`
- `NESTIPY_WEB_SSR_MANIFEST=web/dist/.vite/manifest.json`
- `NESTIPY_WEB_SSR_POLYFILLS=/path/to/polyfills.js`
- `NESTIPY_WEB_SSR_CACHE=100`
- `NESTIPY_WEB_SSR_CACHE_TTL=30`
- `NESTIPY_WEB_SSR_STREAM=1`
- `NESTIPY_WEB_SSR_ROUTES=/,/pricing`
- `NESTIPY_WEB_SSR_EXCLUDE=/admin`

Notes:
- SSR is optional and still evolving.
- If SSR fails, the CSR bundle will still be served.

## jsrun (Python-only SSR)

The `jsrun` runtime is designed for **pre-render SSR** only:
- No streaming SSR
- No Suspense server features
- No React Server Components

Keep the SSR entry clean and render with `renderToString`, for example:

```ts
import ReactDOMServer from "react-dom/server";
export function render(url: string) {
  return ReactDOMServer.renderToString(<App />);
}
```

Nestipy loads a minimal polyfill bundle before executing the SSR entry when
`NESTIPY_WEB_SSR_RUNTIME=jsrun`. You can override it with:

```bash
export NESTIPY_WEB_SSR_POLYFILLS=/path/to/polyfills.js
```
