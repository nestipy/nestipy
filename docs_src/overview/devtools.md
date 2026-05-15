# Devtools Graph

Nestipy exposes a lightweight dependency‑graph view under the Devtools path.

When your app starts, the devtools static path is generated (e.g. `/_devtools/<token>/static`).
The graph endpoint is available at:

- `/_devtools/<token>/graph` (HTML, renderer selectable)
- `/_devtools/<token>/graph.json` (raw JSON)

The graph is built from providers, controllers, and modules discovered at startup.

Notes:
- Renderer can be switched via config (`devtools_graph_renderer="mermaid"` or `"cytoscape"`).
- You can also switch at runtime: `/_devtools/<token>/graph?renderer=mermaid` or `renderer=cytoscape`.
- View modes:
  - `mode=modules` (tree: AppModule → imports → providers/controllers)
  - `mode=dependencies` (DI dependency graph)
- The Mermaid view bundles Mermaid locally for offline use.
- The Cytoscape view loads a local `/_devtools/static/vendor/cytoscape.min.js` if available and falls back to CDN.
- To bundle Cytoscape locally, run `scripts/fetch_devtools_vendor.sh`.
- If you prefer fully offline use, consume the JSON endpoint and render it in your own UI.

## Static assets

Devtools assets are served from the built-in package directory:

- `src/nestipy/devtools/frontend/static/` → served under `/_devtools/<token>/static`

You can override the URL prefix via:

- `NestipyConfig(devtools_static_path="/_devtools/static")`
- `NESTIPY_DEVTOOLS_STATIC_PATH=/_devtools/static`

## CSP and security headers

If `security_headers=True` (default), Nestipy adds a default CSP header.
Devtools pages and Swagger UI add their own CSP so that:

- `data:` images used by Swagger UI are allowed (`img-src ... data:`)
- inline `<style>` / `<script>` used by the graph pages are allowed
