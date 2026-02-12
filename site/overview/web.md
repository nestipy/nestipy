# Nestipy Web (Vite)

Nestipy Web lets you write frontend components in Python and compile them to TSX. The output is a standard React app that runs with Vite, so you can use any TypeScript/React library (shadcn/ui, Tailwind, Radix, etc.).

## Folder Structure

```
app/
  page.py              # /
  layout.py            # root layout
  users/
    page.py            # /users
    [id]/
      page.py          # /users/:id
web/
  index.html
  src/
    main.tsx
    routes.tsx
    pages/...
```

## Routing Rules

- `app/page.py` maps to `/`
- `app/users/page.py` maps to `/users`
- `app/users/[id]/page.py` maps to `/users/:id`
- `app/blog/[...slug]/page.py` maps to `/*`

## Minimal Example

```py
from nestipy.web import component, h

@component
def Page():
    return h.div("Hello from Nestipy Web", class_name="p-6")
```

You can use any HTML tag as `h.tag`, and `class_name` is converted to `className`.

## Root Layout

Create `app/layout.py` to wrap all pages:

```py
from nestipy.web import component, h, Slot

@component
def Layout():
    return h.div(
        h.header("My App"),
        h(Slot),
        class_name="min-h-screen bg-slate-950 text-white",
    )
```

## External React Libraries

Use `external()` to import any TS/React library:

```py
from nestipy.web import component, h, external

Button = external("shadcn/ui/button", "Button")

@component
def Page():
    return h.div(
        Button("Save", variant="outline"),
        class_name="p-6",
    )
```

## Props (Typed)

```py
from nestipy.web import component, props, h, js

@props
class CardProps:
    title: str
    active: bool = False

@component
def Card(props: CardProps):
    return h.div(h.h2(js("props.title")), class_name="card")
```

## Commands (nestipy-cli)

- `nestipy web:build` — compile Python UI into `web/`
- `nestipy web:dev` — watch `app/` and rebuild on changes
- `nestipy web:codegen --output web/src/api/client.ts --lang ts` — generate typed clients
- `nestipy web:build --spec http://localhost:8001/_router/spec --lang ts` — build + generate client into `web/src/api/client.ts`

## Vite Scaffold

If `web/` is empty, the build generates:

- `web/package.json`
- `web/vite.config.ts`
- `web/tsconfig.json`
- `web/src/main.tsx`
- `web/src/routes.tsx`

## Notes

- Output is plain React + Vite and can be integrated with Tailwind or any React UI kit.
- Use `js("...")` for raw JS expressions inside props.
- Components must return a `h(...)` tree (no arbitrary Python execution in render).
- Nested components in the same file should be decorated with `@component` so the compiler emits them.
