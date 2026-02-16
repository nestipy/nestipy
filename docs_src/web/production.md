# Production Build + Serve

## Build

```bash
nestipy run web:build --vite --install
```

This compiles Python UI → TSX and runs `vite build`.

## Serve from Nestipy

```bash
NESTIPY_WEB_DIST=web/dist python main.py
```

Or via CLI flags:

```bash
python main.py --web --web-dist web/dist
```

Fallback order for `--web-dist`:
- `web/dist`
- `src/dist`
- `dist`

Optional environment variables:
- `NESTIPY_WEB_STATIC_PATH=/`
- `NESTIPY_WEB_STATIC_INDEX=index.html`
- `NESTIPY_WEB_STATIC_FALLBACK=1`

## Vite Proxy (Dev)

```bash
nestipy run web:dev --vite --proxy http://127.0.0.1:8001
```

Custom proxy paths:

```bash
nestipy run web:dev --vite --proxy http://127.0.0.1:8001 --proxy-paths /_actions,/_router,/api
```
