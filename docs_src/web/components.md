# Components + UI

## Basic Components

```py
from nestipy.web import component, h

@component
def Page():
    return h.div(
        h.h1("Hello"),
        h.p("Nestipy Web"),
        class_name="p-6",
    )
```

Any HTML tag is available as `h.tag`. Use `class_name` for `className`.

## Props (Typed)

```py
from nestipy.web import component, props, h

@props
class CardProps:
    title: str
    active: bool = False

@component
def Card(props: CardProps):
    return h.div(h.h2(props.title), class_name="card")
```

## External React Libraries

```py
from nestipy.web import component, h, external

Button = external("@radix-ui/react-button", "Button")

@component
def Page():
    return h.div(Button("Save"), class_name="p-6")
```

Utilities:

```py
from nestipy.web import external_fn

clsx = external_fn("clsx", "clsx")
```

## Hooks + JS Context

You can use simple Python lambdas in hooks. For complex JS, use `js("...")`:

```py
from nestipy.web import use_effect

use_effect(lambda: api.ping().then(lambda v: set_status(f"Ping: {v}")), deps=[])
```

### Async Effects

```py
from nestipy.web import use_effect_async

async def load():
    ...

use_effect_async(load, deps=[])
```

## Control Flow (Pure Python)

```py
items = ["A", "B"]
rows = []
for item in items:
    rows.append(h.li(item))

if items:
    message = h.p("Items found")
else:
    message = h.p("No items")

return h.div(h.ul(rows), message)
```

Limits:
- `for` loops must build UI via `list.append(...)`
- `if/elif/else` must assign the same variable(s) in each branch
- `while`, `break`, `continue`, and `for/else` are not supported

## What Python Runs in `app/`

The Python code in `app/` is **compile-time only**. It does **not** run in the browser.

Allowed:
- literals, f-strings
- `if/for` control flow (per rules above)
- simple arithmetic

Not allowed:
- `datetime.now()`, `os`, `pathlib`, file IO, network calls

Runtime work should be in:
- **JS** (`external_fn`, `js(...)`), or
- **backend** (actions or HTTP endpoints)
