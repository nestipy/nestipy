# Nestipy Web (Implementation Notes)

This folder contains the **Nestipy Web** runtime + compiler that lets you write
frontend components in Python and compile them to TSX for a Vite + React app.

This README is a quick technical map of the implementation, designed for
LLM handoff and future contributors.

## High‑Level Flow

1) `app/**/*.py` contains Python UI components (`page.py`, `layout.py`, etc.).
2) `nestipy.web.compiler.compile_app()` parses Python AST (libcst) and emits TSX
   into `web/src/` (pages + components).
3) `web/src/routes.tsx` is generated (React Router).
4) `web/src/main.tsx` boots the app, prefetches CSRF token for actions.
5) Actions and typed clients are generated under `web/src/actions*.ts` and
   `web/src/api/client.ts` (RouterSpec).

## Directory Layout

Typical project layout:

```
app/                 # Python UI (source)
  page.py            # Root page
  layout.py          # Root layout
  notfound.py        # 404 fallback (optional)
  error.py           # Error boundary (optional)
  counter/page.py    # Nested route
web/                 # Vite project (generated/managed)
  src/pages/**       # Generated pages (TSX)
  src/components/**  # Generated components (TSX)
  src/routes.tsx     # Generated router
  src/actions.ts     # Action runtime client (CSRF, meta, signatures)
  src/actions.client.ts  # Typed actions client (generated)
  src/api/client.ts      # Typed HTTP client (RouterSpec, generated)
```

## Module Map (Compiler)

- `compiler/compile.py`: Orchestrates the full compile (`compile_app`), delegates to routes + components + assets.
- `compiler/compile_routes.py`: Route discovery, nested layouts, notfound/error routing, writes `routes.tsx` + `main.tsx`.
- `compiler/compile_components.py`: Parses and emits component/page TSX, resolves imports, validates props.
- `compiler/compile_render.py`: JSX rendering helpers used by component/page generation.
- `compiler/compile_assets.py`: Ensures Vite/Tailwind scaffold and action runtime client exist.
- `compiler/parser.py`: Parser orchestrator (LibCST → component AST).
- `compiler/parser_*`: Specialized parser helpers (imports, props, hooks, control flow, expressions).

## Compiler Pipeline (Core)

- `compile_app()`
  - `discover_routes()` scans `app/**/page.py` and builds route metadata.
  - `parse_component_file()` (libcst) transforms Python to a component AST.
  - `compile_component_module()` emits TSX for each component.
  - `build_routes()` emits `routes.tsx` (nested layouts, notfound, error boundaries).
  - `ensure_vite_files()` ensures Vite files + default deps exist.

### Parsing Rules (Python → JSX)

Supported patterns (examples):

- **Elements**: `h.div(...)`, `h(ExternalComponent, ...)`
- **Props**: `class_name` → `className`
- **Control flow**:
  - `if/elif/else` assigning the same variable (compiled to ternaries)
  - `for` loops that append JSX to a list
  - list comprehensions -> `array.map`
- **Expressions**: comparisons, boolean ops, f‑strings, inline JS
- **Escape hatch**: `js("...")` inserts raw JS expression
- **Imports**:
  - `external(module, name)` for components
  - `external_fn(module, name)` for functions/hooks
  - `@js_import(module, name)` for typed function imports
- **Constructor**: `new_(Class, {...})` → `new Class({...})`

Notes:
- For `for` loops, we only accept `items.append(h.div(...))` style.
- Component output path is deterministic:
  - `app/foo/bar.py` -> `web/src/components/foo/bar.tsx`
  - `app/foo/page.py` -> `web/src/pages/foo/page.tsx`

## Layouts, NotFound, and Error Boundaries

- `layout.py` is compiled and inserted as a layout route node.
- Nested layouts map to nested routes (React Router `children`).
- `notfound.py` is compiled and inserted as a wildcard at the correct level:
  - If layout exists for the same folder: `path: '*'` child of that layout
  - If no layout: `path: '/segment/*'` at top level
- `error.py` is compiled and wired to `errorElement`.
  - If absent, a default error boundary is generated in `routes.tsx`.

## Actions (RPC) + Security

Backend:
- `ActionsModule` exposes a single endpoint (default `/_actions`).
- Guards:
  - `OriginActionGuard` (origin allowlist)
  - `CsrfActionGuard` (header/meta vs cookie)
  - `ActionSignatureGuard` (HMAC + nonce)

Frontend:
- `web/src/actions.ts`
  - `createActionClient()` handles RPC calls
  - `fetchCsrfToken()` preloads CSRF cookie
  - `createActionMetaProvider()` auto‑injects CSRF + ts + nonce
- `web/src/actions.client.ts`
  - typed wrappers for each action provider

## RouterSpec + Typed HTTP Client

If RouterSpec is enabled:
- `/_router/spec` serves JSON metadata.
- `nestipy run web:build --spec ... --lang ts` generates `web/src/api/client.ts`.

## State Management (Zustand Example)

You can define the store in TS and call it from Python:

```ts
// web/src/store.ts
import { create } from 'zustand';
export const useAppStore = create((set) => ({
  theme: 'light',
  sharedCount: 0,
  toggleTheme: () => set((s) => ({ theme: s.theme === 'light' ? 'dark' : 'light' })),
  incShared: () => set((s) => ({ sharedCount: s.sharedCount + 1 })),
}));
```

```py
# app/page.py
from nestipy.web import component, h, external_fn
use_app_store = external_fn("../store", "useAppStore", alias="useAppStore")

@component
def Page():
    shared = use_app_store(lambda s: s.sharedCount)
    inc = use_app_store(lambda s: s.incShared)
    return h.div(
        h.span(shared),
        h.button("+", on_click=inc),
    )
```

## Dev / Build Commands

- Dev (compiler + Vite):
  ```bash
  nestipy run web:dev --vite --install
  ```

- Build:
  ```bash
  nestipy run web:build --vite --install
  ```

- Serve built UI from backend:
  ```bash
  NESTIPY_WEB_DIST=web/dist python main.py --web
  ```

## Key Files

- `nestipy/web/compiler/parser.py` – Python → AST/JSX conversion
- `nestipy/web/compiler/compile.py` – Emits TSX + router + Vite scaffold
- `nestipy/web/actions.py` – Action RPC, guards, CSRF
- `nestipy/web/commands.py` – CLI entry points (`web:dev`, `web:build`)

## Design Constraints

- Components must return `h(...)` / `h.tag(...)`
- Limited Python control flow; no arbitrary statements in JSX trees
- Use `external_fn()` for hooks and state libraries (e.g., Zustand)
- Use `@js_import()` when you want a Python-typed wrapper for a JS import
- Use `js("...")` for raw JS when needed

## Async Effects

React effects must be sync. If you need async logic, use `use_effect_async()`:

```py
from nestipy.web import use_effect_async

async def load():
    ...

use_effect_async(load, deps=[])
```

If the async function returns a cleanup, it will be invoked on unmount.

## What Python Code Can Run in `app/`

Nestipy Web **compiles** Python to TSX. Your `app/` code does **not** execute
at runtime in the browser, so only compile‑time Python is supported.

### ✅ Allowed (compile‑time only)

- Pure constants and simple literal expressions
- `if/elif/else` that assign the same variables in all branches
- `for` loops that build JSX lists via `items.append(h.div(...))`
- f‑strings for string formatting
- Simple arithmetic or comparisons

### ❌ Not allowed (runtime/system)

- `datetime.now()`, `time.time()`, `os`, `pathlib`, `sys`, `subprocess`
- File IO, environment variables, network calls, database access
- Anything that depends on runtime state inside the browser

### How to do runtime things

- **In the browser:** use `js("...")` or `external_fn()` to call JS APIs.
  - Example: `js("new Date().toISOString()")`
- **From the backend:** expose an action/API and fetch it.

---

If you need deeper behavior (custom AST nodes, new control flow, new hooks),
start with `parser.py` and `compile.py`.
