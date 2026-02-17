from __future__ import annotations


DEFAULT_PAGE_TEMPLATE = """from nestipy.web import component, h

# Tip: auto-generate typed JS imports with:
#   nestipy run web:actions --actions-types app/_generated/actions_types.py
#   nestipy run web:codegen --router-types app/_generated/api_types.py
#
# Example:
#   from nestipy.web import js_import
#   from app._generated.actions_types import ActionsClient
#   from app._generated.api_types import ApiClient
#
#   @js_import("../actions.client", "createActions")
#   def create_actions() -> ActionsClient: ...
#
#   @js_import("../api/client", "createApiClient")
#   def create_api_client() -> ApiClient: ...

@component
def Page():
    features = [
        ("Python-first UI", "Write React UI in Python and compile to TSX."),
        ("Typed APIs", "Generate typed actions and HTTP clients automatically."),
        ("Vite + React", "Use the full React ecosystem with Vite tooling."),
    ]
    cards = []
    for title, body in features:
        cards.append(
            h.div(
                h.h3(title, class_name="text-lg font-semibold text-white"),
                h.p(body, class_name="text-sm text-slate-300"),
                class_name="rounded-2xl border border-white/10 bg-white/5 p-5 shadow-sm",
            )
        )
    code = \"\"\"from nestipy.web import component, h

@component
def Page():
    return h.div(
        h.h1("Nestipy Web"),
        h.p("Python-first UI"),
        class_name="p-8",
    )
\"\"\"
    return h.div(
        h.section(
            h.div(
                h.span(
                    "Build UIs like Uniwind",
                    class_name="inline-flex items-center rounded-full border border-white/15 bg-white/10 px-3 py-1 text-xs uppercase tracking-wide text-white/80",
                ),
                h.h1(
                    "Nestipy Web",
                    class_name="mt-5 text-4xl font-semibold tracking-tight text-white md:text-6xl",
                ),
                h.p(
                    "Ship a modern frontend without leaving Python. Compile to React, keep typed APIs, and scale with Vite.",
                    class_name="mt-4 max-w-2xl text-base text-slate-300 md:text-lg",
                ),
                h.div(
                    h.a(
                        "Get Started",
                        href="/web/getting-started",
                        class_name="rounded-full bg-[#c10e0e] px-5 py-3 text-sm font-semibold text-white shadow-sm shadow-[#c10e0e]/30",
                    ),
                    h.a(
                        "View Docs",
                        href="/web/",
                        class_name="rounded-full border border-white/20 px-5 py-3 text-sm font-semibold text-white/90",
                    ),
                    class_name="mt-6 flex flex-wrap gap-3",
                ),
                class_name="max-w-3xl",
            ),
            h.div(
                h.pre(
                    h.code(code, class_name="text-sm text-slate-200"),
                    class_name="rounded-2xl border border-white/10 bg-slate-950/70 p-6 shadow-lg",
                ),
                class_name="mt-10",
            ),
            class_name="grid gap-10 lg:grid-cols-[1.1fr_0.9fr] lg:items-center",
        ),
        h.section(
            h.h2("Why teams pick Nestipy Web", class_name="text-2xl font-semibold text-white"),
            h.div(cards, class_name="mt-6 grid gap-4 md:grid-cols-3"),
        ),
        h.section(
            h.div(
                h.h3("Fullstack, from one command", class_name="text-xl font-semibold text-white"),
                h.p(
                    "Run backend and frontend together, keep typed clients in sync, and ship fast.",
                    class_name="mt-2 text-sm text-slate-300",
                ),
                h.div(
                    h.code(
                        "nestipy run web:dev --vite --install --proxy http://127.0.0.1:8001",
                        class_name="text-xs text-slate-200",
                    ),
                    class_name="mt-4 rounded-xl border border-white/10 bg-white/5 px-4 py-3",
                ),
                class_name="rounded-3xl border border-white/10 bg-white/5 p-6",
            ),
        ),
        class_name="space-y-16",
    )
"""


DEFAULT_LAYOUT_TEMPLATE = """from nestipy.web import component, h, Slot

@component
def Layout():
    return h.div(
        h.div(
            class_name="pointer-events-none fixed inset-0 bg-[radial-gradient(circle_at_top,_rgba(193,14,14,0.25),_transparent_45%)]",
        ),
        h.div(
            h.header(
                h.div(
                    h.span("Nestipy", class_name="text-sm font-semibold uppercase tracking-[0.3em] text-white/70"),
                    h.span("Web", class_name="ml-3 rounded-full bg-white/10 px-3 py-1 text-xs font-semibold text-white/80"),
                    class_name="flex items-center",
                ),
                h.nav(
                    h.a("Docs", href="/web/", class_name="text-sm text-white/80"),
                    h.a("GitHub", href="https://github.com/nestipy/nestipy", class_name="text-sm text-white/80"),
                    class_name="flex items-center gap-4",
                ),
                class_name="flex items-center justify-between",
            ),
            h.main(h(Slot), class_name="py-16"),
            h.footer(
                h.p("Built with Nestipy Web", class_name="text-xs text-white/60"),
                class_name="py-10",
            ),
            class_name="relative mx-auto flex min-h-screen w-full max-w-6xl flex-col gap-10 px-6",
        ),
        class_name="min-h-screen bg-slate-950 text-slate-100 antialiased",
    )
"""


DEFAULT_ACTIONS_TEMPLATE = """from nestipy.web import action

class DemoActions:
    @action()
    async def hello(self, name: str = "world") -> str:
        return f"Hello, {name}!"
"""
