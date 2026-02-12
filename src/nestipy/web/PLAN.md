# nestipy_web (Vite target) - Plan

## Goal
Provide a Next.js-like developer experience for frontend, but compile Python components to TSX and run with Vite. Integrate with existing `nestipy-cli` (no new CLI package) and reuse Nestipy RouterSpec for typed clients.

## Constraints
- Target: Vite (default).
- Use `nestipy-cli` commands to invoke `nestipy_web` functionality.
- Support external React TS libraries (shadcn/ui, tailwind, etc.).
- Prefer existing libraries for parsing/generation when useful.

## Proposed Architecture
- `nestipy_web.ui`: Python DSL for components.
- `nestipy_web.compiler`: Python -> TSX/TS generator.
- `nestipy_web.client`: typed client generator (wrap existing router spec).
- `nestipy_web.config`: config schema and defaults.
- `nestipy_web.commands`: entrypoints called by nestipy-cli.

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

### Step 6: Docs + examples
- Add `docs/web/overview.md`
- Add example using shadcn + tailwind

### Step 7: Tests
- Unit tests for compiler output
- Snapshot tests for generated TSX
- CLI command smoke tests

## Libraries to Consider
- Parsing Python: `libcst` (preferred) or stdlib `ast`
- Code formatting: `black` for Python, `prettier` for TSX (optional)
- HTML/JSX emit: generate string directly or use `jinja2` templates
