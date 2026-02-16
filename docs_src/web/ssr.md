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

Notes:
- SSR is optional and still evolving.
- If SSR fails, the CSR bundle will still be served.
