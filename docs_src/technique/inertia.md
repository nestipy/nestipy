# Inertia

Nestipy ships a first-class [Inertia.js](https://inertiajs.com) adapter,
`nestipy-inertia`, with full latest-protocol parity: partial reloads
(`only` / `except` / `reset`), optional and deferred props, merge / deep-merge
props, history encryption, SSR, flash messages and validation handling.

Inertia lets you build a single-page app **without building an API**. Your
controllers return a component name + props; Inertia turns that into a real SPA
page on the client (React, Vue or Svelte). No client-side routing layer, no
serializers — just controllers and page components.

```
Browser ──visit /dashboard──▶  Controller  ──render("Dashboard", props)──▶  React/Vue/Svelte page
        ◀──── HTML (first visit) / JSON page object (subsequent visits) ────
```

## Quickstart (CLI)

The fastest way to start. The CLI scaffolds the Nestipy backend and generates a
real Vite frontend for the framework you pick:

```bash
nestipy new myapp --fullstack --react   # or --vue / --svelte
# omit the framework flag to be prompted
```

Then run **both** dev servers with a single command — `--web` starts the Inertia
frontend (Vite) alongside the backend:

```bash
cd myapp
uv sync
nestipy start --dev --web
```

Open the backend URL (default `http://localhost:8000`). The backend HTML
references the Vite dev server for the JS, so you get hot-reload on the frontend
and Python reload on the backend.

> `--web` runs `npm run dev` in `./inertia` (installing deps first if needed). Use
> `--web-dir` to point at a different folder. Prefer separate terminals? Skip
> `--web` and run `cd inertia && npm run dev` yourself.

> `--fullstack` is a lean Inertia starter. `--full` gives the same Inertia
> frontend **plus** a database + JWT auth backend.

### What gets generated

```
myapp/
├── main.py                 # NestipyFactory + session() + view dir
├── src/
│   ├── app_module.py       # InertiaModule.register(...)
│   ├── app_controller.py   # returns res.inertia.render("Index", {...})
│   └── app_service.py
├── views/
│   └── index.html          # root template (inertiaHead / inertiaBody)
└── inertia/                # the Vite app (React / Vue / Svelte)
    ├── nestipy.inertia.ts  # Vite plugin (build output + manifest)
    ├── vite.config.ts
    └── src/
        ├── main.tsx        # createInertiaApp(...)
        └── Pages/          # one component per rendered page
            ├── Index.tsx
            └── About.tsx
```

## Manual setup

To add Inertia to an existing Nestipy project instead of scaffolding:

```bash
pip install nestipy-inertia
```

**`main.py`** — point the view engine at the root template and enable sessions:

```python
import os
from granian.constants import Interfaces
from nestipy.common import session
from nestipy.core import NestipyFactory
from src.app_module import AppModule

app = NestipyFactory.create(AppModule)

# minijinja view engine for the root template (views/index.html)
app.set_base_view_dir(os.path.join(os.path.dirname(__file__), "views"))

# session is required for flash messages / validation errors
app.use(session())

if __name__ == "__main__":
    app.listen("main:app", host="0.0.0.0", port=8000, interface=Interfaces.ASGI, reload=True)
```

**`src/app_module.py`** — register the module. `root_dir` is the Vite app folder
(its `dist/` + `manifest.json` are read in production):

```python
import os
from nestipy.common import Module
from nestipy_inertia import InertiaModule, InertiaConfig
from .app_controller import AppController


@Module(
    imports=[
        InertiaModule.register(
            InertiaConfig(root_dir=os.path.join(os.getcwd(), "inertia"))
        )
    ],
    controllers=[AppController],
)
class AppModule: ...
```

**`views/index.html`** — the root template Inertia injects the page object into.
`viteReactRefresh()` is **React-only** — omit it for Vue/Svelte:

```html
<!doctype html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    {{ inertiaHead() }}
</head>
<body>
{{ viteReactRefresh() }}  {# React only #}
{{ inertiaBody() }}
</body>
</html>
```

## The frontend

The Vite app boots Inertia and maps page names to components. With React:

```tsx
// inertia/src/main.tsx
import { createInertiaApp } from '@inertiajs/react'
import { createRoot } from 'react-dom/client'

createInertiaApp({
    resolve: (name) => {
        const pages = import.meta.glob('./Pages/**/*.tsx', { eager: true })
        return pages[`./Pages/${name}.tsx`] as never
    },
    setup({ el, App, props }) {
        createRoot(el).render(<App {...props} />)
    },
})
```

When a controller calls `render("Dashboard", ...)`, Inertia loads
`./Pages/Dashboard.tsx` and passes the props in. Vue and Svelte use
`@inertiajs/vue3` / `@inertiajs/svelte` with the same `resolve` pattern (the CLI
generates the right entry for your choice).

## The Vite plugin (`nestipy.inertia.ts`)

The backend and the frontend agree on one contract: the **build output folder**
and the **manifest** filename. In production the adapter reads
`<root_dir>/dist/manifest.json` to find the hashed JS/CSS. The
`nestipy.inertia.ts` Vite plugin sets those build options for you (and switches
to the SSR bundle on an SSR build). The CLI generates it; for a manual setup,
create it once:

```ts
// inertia/nestipy.inertia.ts
import type { PluginOption } from 'vite'

type Input = {
    entry: string        // client entry, e.g. './src/main.tsx'
    ssr?: string         // optional SSR entry, e.g. './src/ssr.tsx'
    manifest?: string    // manifest filename (default: 'manifest.json')
}
type NestipyPlugin = (options: Input) => PluginOption

const nestipyVite: NestipyPlugin = ({ entry, ssr, manifest = 'manifest.json' }) => {
    return {
        name: 'nestipy-vite-plugin',
        config: (config, env) => ({
            ...config,
            build: {
                manifest: env.isSsrBuild ? false : manifest,
                outDir: env.isSsrBuild ? 'dist/ssr' : 'dist',
                rollupOptions: {
                    input: env.isSsrBuild && ssr ? ssr : entry,
                },
            },
        }),
    }
}

export default nestipyVite
```

Register it in `vite.config.ts` after your framework plugin, passing the client
entry (and the SSR entry if you use SSR):

```ts
// inertia/vite.config.ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'      // vue() / svelte() for Vue / Svelte
import nestipyVite from './nestipy.inertia'

export default defineConfig({
    plugins: [
        react(),
        nestipyVite({ entry: './src/main.tsx' }),   // add ssr: './src/ssr.tsx' for SSR
    ],
})
```

| Plugin option | Default | Purpose |
| --- | --- | --- |
| `entry` | — (required) | The client entry bundle Vite builds (`rollupOptions.input`). Must match the framework entry — `./src/main.tsx` (React) or `./src/main.ts` (Vue/Svelte). |
| `ssr` | — | The SSR entry bundle. On an SSR build (`vite build --ssr`) it becomes the input and the output goes to `dist/ssr/`. |
| `manifest` | `manifest.json` | Manifest filename written into `dist/`. Must match `InertiaConfig.manifest_json_path`. |

> **`entry` must match the file the backend's `views/index.html` loads in dev.**
> The default `InertiaConfig.entrypoint_filename` is `main.tsx`; if your entry is
> `main.ts` (Vue/Svelte) set `InertiaConfig(entrypoint_filename="main.ts")`.

## Rendering pages

Inject `InertiaResponse` and call `res.inertia.render(component, props)`:

```python
from typing import Annotated
from nestipy.common import Controller, Get, Response
from nestipy.ioc import Res
from nestipy_inertia import InertiaResponse


@Controller()
class AppController:
    @Get()
    async def index(self, res: Annotated[InertiaResponse, Res()]) -> Response:
        return await res.inertia.render("Dashboard", {"message": "hello"})
```

- For an Inertia XHR request it returns the JSON page object (`X-Inertia: true`).
- For a first/full visit it renders the root template with the `data-page` payload.
- If SSR is enabled it renders via the SSR server, falling back to the template.

`props` accepts a `dict` or a Pydantic `BaseModel`.

## Navigating

On the client, use `<Link>` (or the router) instead of `<a>` so navigation stays
a single XHR visit — no full page reload:

```tsx
import { Link, router } from '@inertiajs/react'

<Link href="/about">About</Link>
<Link href="/users" method="post" data={{ name: 'Ada' }}>Create</Link>

// programmatic
router.visit('/dashboard')
```

## Props

Every helper accepts a value or a zero-arg callable (evaluated lazily, so
expensive work runs only when the prop is actually sent).

```python
from nestipy_inertia import optional, defer, merge, deep_merge
```

| Helper | Behavior |
| --- | --- |
| plain value | Always sent, overwrites the client value. |
| `optional(fn)` | **Excluded** from the initial render; only sent when a partial reload names it. |
| `defer(fn, group="default")` | Excluded from the first render and fetched automatically after load. `group` batches requests. |
| `merge(fn)` | Always sent, but **appended** to the client value instead of overwriting. |
| `deep_merge(fn, match_on=["id"])` | Deep-merges; `match_on` dedupes array items by key. |

```python
@Get()
async def dashboard(self, res: Annotated[InertiaResponse, Res()]) -> Response:
    return await res.inertia.render("Dashboard", {
        "user": current_user,                       # always
        "permissions": optional(load_permissions),  # only on partial reload
        "stats": defer(load_stats),                 # fetched after first paint
        "feed": defer(load_feed, group="feed", merge=True),
        "notifications": merge(load_notifications),
    })
```

### Consuming deferred props on the client

`defer` props are advertised in `deferredProps`; the client refetches them after
paint. React exposes a `<Deferred>` wrapper:

```tsx
import { Deferred } from '@inertiajs/react'

<Deferred data="stats" fallback={<p>Loading stats…</p>}>
    <Stats stats={stats} />
</Deferred>
```

### Partial reloads from the client

Refetch only the props you need:

```tsx
import { router } from '@inertiajs/react'

router.reload({ only: ['notifications'] })   // X-Inertia-Partial-Data
router.reload({ except: ['feed'] })          // X-Inertia-Partial-Except
```

The server honors `only` (`X-Inertia-Partial-Data`), `except`
(`X-Inertia-Partial-Except`, which **takes precedence**), `X-Inertia-Reset`, and
guards the component with `X-Inertia-Partial-Component`. The `errors` prop is
always included.

## Forms & validation

Use `useForm` on the client — it tracks values, submit state and server `errors`:

```tsx
import { useForm } from '@inertiajs/react'

function Login() {
    const form = useForm({ email: '', password: '' })
    const submit = (e) => {
        e.preventDefault()
        form.post('/login')
    }
    return (
        <form onSubmit={submit}>
            <input value={form.data.email}
                   onChange={(e) => form.setData('email', e.target.value)} />
            {form.errors.email && <span>{form.errors.email}</span>}
            <button disabled={form.processing}>Sign in</button>
        </form>
    )
}
```

On the backend, validate with Pydantic. A `ValidationError` raised in a handler
is caught by `InertiaMiddleware`: the errors are flashed to the session
(honoring the `X-Inertia-Error-Bag` header) and the request is redirected back,
so the page re-renders with `errors` populated automatically.

```python
class UserLogin(BaseModel):
    email: EmailStr
    password: str

@Post("/login")
async def login(self, user: Annotated[UserLogin, Body()], res: Annotated[InertiaResponse, Res()]) -> Response:
    res.inertia.flash("Welcome back!", category="success")
    return await res.inertia.back()
```

## Shared props

Share props across a request (e.g. auth/flash from a middleware or guard) so
every page receives them:

```python
res.inertia.share(auth={"user": current_user}, flash=get_flash())
```

## History encryption

Protect sensitive page data in the browser history:

```python
@Get("/account")
async def account(self, res: Annotated[InertiaResponse, Res()]) -> Response:
    res.inertia.encrypt_history()           # encrypt this entry
    return await res.inertia.render("Account", {...})

@Post("/logout")
async def logout(self, res: Annotated[InertiaResponse, Res()]) -> Response:
    res.inertia.clear_history()             # wipe encrypted history
    return await res.inertia.location("/login")
```

Set `InertiaConfig(encrypt_history=True)` to encrypt every entry by default.

## Flash messages

Flash a message (requires `app.use(session())`); it lands in the `messages` prop
on the next render:

```python
res.inertia.flash("Saved!", category="success")
```

## Redirects

- `res.inertia.location(url)` — external/full redirect (`409` + `X-Inertia-Location`).
- `res.inertia.back()` — redirect to the referer.
- `302` responses to `PUT` / `PATCH` / `DELETE` are automatically converted to
  `303 See Other` (prevents the browser from re-submitting the body on redirect).

## SSR

```python
InertiaConfig(ssr_enabled=True, ssr_url="http://localhost:13714")
```

Build an SSR bundle and run the Inertia SSR server; the adapter posts the page
object to `{ssr_url}/render` and injects the returned `head` / `body`. Deferred
props are excluded from the SSR payload (fetched after load). On any SSR error it
falls back to the standard template render.

## Production build

Build the frontend, then run the backend in production mode:

```bash
cd inertia
npm run build            # outputs inertia/dist + manifest.json
cd ..
nestipy start            # serves the built assets via the manifest
```

In production the adapter reads `inertia/dist/manifest.json` to resolve the
hashed JS/CSS and injects them through `inertiaHead()` / `inertiaBody()` — no
Vite dev server needed.

## Configuration reference

| Field | Default | Purpose |
| --- | --- | --- |
| `environment` | `"development"` | `development` uses the Vite dev server; `production` uses the manifest. |
| `version` | `"1.0"` | Asset version; a mismatch triggers a `409` full reload (GET only). |
| `root_dir` | `os.getcwd()` | The Vite app folder (holds `dist/` + `manifest.json`). |
| `root_template_filename` | `"index.html"` | Root template in the view dir. |
| `entrypoint_filename` | `"main.tsx"` | Client entry referenced in dev. |
| `dev_url` | `http://localhost:5173` | Vite dev server URL. |
| `ssr_enabled` / `ssr_url` | `False` / `:13714` | Enable SSR + the SSR server URL. |
| `encrypt_history` | `False` | Encrypt every history entry by default. |
| `manifest_json_path` | `"manifest.json"` | Manifest filename inside `build_dir`. |
| `assets_prefix` / `build_dir` / `src_dir` | `/dist` / `dist` / `src` | Asset URL prefix + build/source folders. |
| `use_flash_messages` / `flash_message_key` | `True` / `"messages"` | Flash messages toggle + prop key. |
| `use_flash_errors` / `flash_error_key` | `True` / `"errors"` | Validation errors toggle + prop key. |
| `json_encoder` | `InertiaJsonEncoder` | Encoder for the page object. |

See the full example [here](https://github.com/nestipy/inertia/tree/main/example).
