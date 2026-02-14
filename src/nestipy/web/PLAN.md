# nestipy_web (Vite target) - Plan

## Goal
Provide a Next.js-like developer experience for frontend, compile Python components to TSX, and run with Vite. Integrate with existing `nestipy-cli` (no new CLI package) and reuse Nestipy RouterSpec for typed clients. Add optional SSR (via jsrun / V8) without requiring Node.

## Constraints
- Target: Vite (default).
- Use `nestipy-cli` commands to invoke `nestipy_web` functionality.
- Support external React TS libraries (shadcn/ui, tailwind, etc.).
- Prefer existing libraries for parsing/generation when useful.
- SSR must be optional and have safe CSR fallback.

## Proposed Architecture
- `nestipy_web.ui`: Python DSL for components.
- `nestipy_web.compiler`: Python -> TSX/TS generator.
- `nestipy_web.client`: typed client generator (wrap existing router spec).
- `nestipy_web.config`: config schema and defaults.
- `nestipy_web.commands`: entrypoints called by nestipy-cli.
- `nestipy_web.ssr`: optional SSR runtime adapters (jsrun first).

## Step-by-step Plan

### Step 1: Scope + Vite output conventions
- Define output folder layout (e.g., `web/` target):
  - `web/src/main.tsx`
  - `web/src/routes.tsx`
  - `web/src/pages/**` (compiled TSX)
  - `web/src/components/**` (shared compiled)
- Define mapping rules from `app/` (Python) to output routes.

### Step 2: Python UI DSL (minimal MVP)
- `@component` decorator
- `h(tag, props, *children)` factory
- `external(module, name)` for TS imports
- `Fragment` and `Text` helpers
- Optional props typing with `@props` (for TS interface generation)

### Step 3: Compiler MVP
- Parse Python using `ast` or `libcst` (prefer `libcst` for safer codegen).
- Build an intermediate UI tree (nodes, props, children, imports).
- Emit TSX + import lines.
- Emit `routes.tsx` + `main.tsx` for Vite.

### Step 4: Typed client integration
- Reuse `build_router_spec` + existing TS/Python client generators.
- Add `nestipy_web.client` wrapper to:
  - pull RouterSpec (local or via URL)
  - output `web/src/api/client.ts`

### Step 5: Nestipy CLI integration
- Add `nestipy web:build`, `nestipy web:dev`, `nestipy web:codegen` commands
  - `build`: compile Python -> TSX
  - `dev`: watch `app/` and recompile
  - `codegen`: generate typed client from RouterSpec

### Step 6: SSR build pipeline (optional)
- Emit SSR entrypoints (client + server).
- Update Vite config to support `vite build --ssr`.
- CLI flags:
  - `nestipy run web:build --vite --ssr`
  - `nestipy start --web --ssr`
- Environment:
  - `NESTIPY_WEB_SSR=1`
  - `NESTIPY_WEB_SSR_RUNTIME=jsrun|node`
  - `NESTIPY_WEB_SSR_ENTRY=web/dist/ssr/entry-server.js`

### Step 7: SSR runtime adapters (optional)
- Implement jsrun (V8 via PyO3) adapter.
- Provide CSR fallback on error.
- Optional dependency: `pip install nestipy[web-ssr]` (adds `jsrun`).

### Step 8: Docs + examples
- Add `docs/web/overview.md`
- Add example using shadcn + tailwind
- Add SSR usage guide and optional install (`nestipy[web-ssr]`)

### Step 9: Tests
- Unit tests for compiler output
- Snapshot tests for generated TSX
- CLI command smoke tests
- SSR adapter smoke tests (skip if jsrun not installed)

## Libraries to Consider
- Parsing Python: `libcst` (preferred) or stdlib `ast`
- Code formatting: `black` for Python, `prettier` for TSX (optional)
- HTML/JSX emit: generate string directly or use `jinja2` templates
