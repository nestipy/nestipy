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
- `NESTIPY_WEB_SSR_CACHE=100`
- `NESTIPY_WEB_SSR_CACHE_TTL=30`
- `NESTIPY_WEB_SSR_STREAM=1`
- `NESTIPY_WEB_SSR_ROUTES=/,/pricing`
- `NESTIPY_WEB_SSR_EXCLUDE=/admin`

Notes:
- SSR is optional and still evolving.
- If SSR fails, the CSR bundle will still be served.
