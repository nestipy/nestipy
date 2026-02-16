# CLI Reference (nestipy-cli)

## `web:init`

```bash
nestipy run web:init [--app-dir app] [--out-dir web] [--no-build] [--clean]
```

- `--app-dir` / `--app` — UI source folder (default `app`)
- `--out-dir` / `--out` — Vite output folder (default `web`)
- `--proxy` — backend proxy URL for generated Vite config
- `--proxy-paths` — comma-separated proxy paths
- `--no-build` — scaffold only, skip compile
- `--clean` — remove previous output

## `web:dev`

```bash
nestipy run web:dev [--vite] [--install] [--proxy URL] [--backend CMD]
```

Common flags:
- `--vite` — start Vite dev server
- `--install` — install frontend deps before Vite
- `--proxy` — backend proxy URL
- `--proxy-paths` — comma-separated list of proxied paths
- `--backend` — command to start backend (e.g. `"python main.py"`)
- `--backend-cwd` — working directory for backend

Actions + router spec codegen:
- `--actions` — enable actions client generation
- `--actions-endpoint` — default `/_actions`
- `--actions-output` — default `web/src/actions.client.ts`
- `--actions-watch` — CSV of backend paths to watch; disables polling
- `--router-spec` — router spec URL (defaults from env)
- `--router-output` — output path (default `web/src/api/client.ts`)
- `--lang` — client language (`ts` or `python`) for router spec
- `--class` — client class name (default `ApiClient`)
- `--prefix` — URL prefix

## `web:build`

```bash
nestipy run web:build [--vite] [--install] [--ssr]
```

Flags:
- `--vite` — run Vite build after compile
- `--install` — install deps before build
- `--ssr` — build SSR bundle
- `--ssr-entry` — default `src/entry-server.tsx`
- `--ssr-out-dir` — default `dist/ssr`

Codegen flags (same as `web:dev`):
- `--spec`, `--output`, `--lang`, `--class`, `--prefix`
- `--actions`, `--actions-endpoint`, `--actions-output`

## `web:codegen`

```bash
nestipy run web:codegen --spec URL --output web/src/api/client.ts --lang ts
```

## `web:actions`

```bash
nestipy run web:actions --spec URL --output web/src/actions.client.ts
```

## `web:install`

```bash
nestipy run web:install
```

## `web:add`

```bash
nestipy run web:add react
nestipy run web:add -D tailwindcss
nestipy run web:add --peer react-dom
```
