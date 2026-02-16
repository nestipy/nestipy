# Routing + Layouts

## Routing Rules

- `app/page.py` → `/`
- `app/users/page.py` → `/users`
- `app/users/[id]/page.py` → `/users/:id`
- `app/blog/[...slug]/page.py` → `/*`

## Layouts (Nested)

Root layout:

```
app/layout.py
app/page.py
```

Nested layout:

```
app/
  layout.py
  page.py
  api/
    layout.py
    page.py
```

### Import Rules

- `from app.layout import ThemeContext` → always root layout
- `from .layout import ThemeContext` → local layout
- `from layout import ...` → nearest layout (local or root)

## Root Layout Example

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
