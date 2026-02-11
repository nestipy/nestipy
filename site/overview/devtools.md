# Devtools Graph

Nestipy exposes a lightweight dependency‑graph view under the Devtools path.

When your app starts, the devtools static path is generated (e.g. `/_devtools/<token>/static`).
The graph endpoint is available at:

- `/_devtools/<token>/graph` (HTML + Mermaid)
- `/_devtools/<token>/graph.json` (raw JSON)

The graph is built from providers, controllers, and modules discovered at startup.

Notes:
- The HTML view loads Mermaid from a CDN.
- If you prefer fully offline use, consume the JSON endpoint and render it in your own UI.
