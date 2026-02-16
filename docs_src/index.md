---
layout: home

hero:
  name: "Nestipy"
  text: "Full‑stack Python framework"
  tagline: "Build modular backends, typed actions, and React UIs from one codebase."
  image:
    src: /images/nestipy.png
    alt: Nestipy Logo
  actions:
    - theme: brand
      text: Get Started
      link: /overview/first-step
    - theme: alt
      text: Web Docs
      link: /web/

features:
  - title: "Modular architecture"
    details: "Controllers, providers, modules, and DI that scale with your team."
  - title: "Typed actions"
    details: "Generate action clients automatically and call them from UI."
  - title: "Typed HTTP clients"
    details: "Call controller methods as api.Controller.method()."
  - title: "Fast adapters"
    details: "Run on FastAPI or BlackSheep without changing your design."
  - title: "GraphQL ready"
    details: "First-class Strawberry GraphQL support."
  - title: "Web UI in Python"
    details: "Compile Python UI to React + Vite."

---

## Fullstack by design

Nestipy brings NestJS‑style architecture to Python and adds a web layer that compiles Python UI to React. You write services and UI in one language and ship both sides with typed clients.

### Backend example (controller + module)

```py
from nestipy.common import Controller, Get, Module

@Controller("/api")
class AppController:
    @Get("/ping")
    async def ping(self) -> dict:
        return {"ok": True}

@Module(controllers=[AppController])
class AppModule:
    pass
```

### Actions (typed RPC)

```py
from nestipy.common import Injectable
from nestipy.web import action

@Injectable()
class AppActions:
    @action()
    async def hello(self, name: str) -> str:
        return f"Hello {name}"
```

### Web UI (Python → React)

```py
from nestipy.web import component, h

@component
def Page():
    return h.div(
        h.h1("Nestipy Web"),
        h.p("Python-first UI"),
        class_name="p-8",
    )
```

## Run the backend

```bash
python main.py
```

## Web quickstart (frontend)

```bash
nestipy run web:init
nestipy run web:dev --vite --install --proxy http://127.0.0.1:8001
```
