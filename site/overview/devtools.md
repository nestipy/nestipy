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
- The Mermaid view bundles Mermaid locally for offline use.
- The Cytoscape view loads a local `/_devtools/static/vendor/cytoscape.min.js` if available and falls back to CDN.
- To bundle Cytoscape locally, run `scripts/fetch_devtools_vendor.sh`.
- If you prefer fully offline use, consume the JSON endpoint and render it in your own UI.
