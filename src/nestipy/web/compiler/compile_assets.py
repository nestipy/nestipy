"""Scaffold and asset helpers for the web compiler."""

from __future__ import annotations

import json
from pathlib import Path
import re

from nestipy.web.config import WebConfig


def _dedupe_api_client_stub(content: str) -> str:
    """Remove duplicate createApiClient stubs from placeholder files."""
    pattern = (
        r"export function createApiClient\\(.*?\\)\\s*:\\s*ApiClient\\s*\\{[\\s\\S]*?"
        r"export const create_api_client\\s*=\\s*createApiClient;\\s*"
    )
    match = re.search(pattern, content)
    if not match:
        return content
    start, end = match.span()
    tail = re.sub(pattern, "", content[end:])
    return content[:start] + match.group(0) + tail


def ensure_vite_files(config: WebConfig, root: str | None = None) -> None:
    """Ensure required Vite/Tailwind scaffold files exist."""
    out_dir = config.resolve_out_dir(root)
    project_name = _sanitize_package_name(out_dir.parent.name) or "nestipy-web"
    index_html = out_dir / "index.html"
    if not index_html.exists():
        index_html.write_text(
            "\n".join(
                [
                    "<!DOCTYPE html>",
                    "<html lang='en'>",
                    "  <head>",
                    "    <meta charset='UTF-8' />",
                    "    <meta name='viewport' content='width=device-width, initial-scale=1.0' />",
                    "    <title>Nestipy Web</title>",
                    "  </head>",
                    "  <body>",
                    "    <div id='root'></div>",
                    "    <script type='module' src='/src/main.tsx'></script>",
                    "  </body>",
                    "</html>",
                ]
            ),
            encoding="utf-8",
        )

    package_json = out_dir / "package.json"
    if not package_json.exists():
        package_json.write_text(
            json.dumps(
                {
                    "name": project_name,
                    "private": True,
                    "version": "0.0.0",
                    "type": "module",
                    "scripts": {
                        "dev": "vite",
                        "build": "vite build",
                        "preview": "vite preview",
                    },
                    "dependencies": {
                        "react": "^18.2.0",
                        "react-dom": "^18.2.0",
                        "react-router-dom": "^6.26.2",
                        "zustand": "^4.5.2",
                    },
                    "devDependencies": {
                        "@types/react": "^18.2.70",
                        "@types/react-dom": "^18.2.24",
                        "@tailwindcss/vite": "^4.0.0",
                        "@vitejs/plugin-react": "^4.3.1",
                        "tailwindcss": "^4.0.0",
                        "typescript": "^5.6.2",
                        "vite": "^5.4.1",
                    },
                },
                indent=2,
            ),
            encoding="utf-8",
        )
    else:
        try:
            data = json.loads(package_json.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            data = {}
        if isinstance(data, dict):
            updated = False
            name = data.get("name")
            if isinstance(name, str):
                cleaned = _sanitize_package_name(name)
                if cleaned and cleaned != name:
                    data["name"] = cleaned
                    updated = True
            deps = data.get("dependencies")
            dev_deps = data.get("devDependencies")
            is_scaffold = (
                data.get("private") is True
                and data.get("version") == "0.0.0"
                and isinstance(deps, dict)
                and deps.get("react")
                and deps.get("react-dom")
                and deps.get("react-router-dom")
            )
            if is_scaffold:
                if not isinstance(dev_deps, dict):
                    dev_deps = {}
                    data["devDependencies"] = dev_deps
                if "zustand" not in deps:
                    deps["zustand"] = "^4.5.2"
                    updated = True
                tailwind_version = dev_deps.get("tailwindcss")
                if not tailwind_version or str(tailwind_version).startswith("^3"):
                    dev_deps["tailwindcss"] = "^4.0.0"
                    updated = True
                if "@tailwindcss/vite" not in dev_deps:
                    dev_deps["@tailwindcss/vite"] = "^4.0.0"
                    updated = True
            if updated:
                package_json.write_text(json.dumps(data, indent=2), encoding="utf-8")

    vite_config = out_dir / "vite.config.ts"
    if not vite_config.exists():
        proxy_lines: list[str] = []
        if config.proxy:
            paths = [p for p in (config.proxy_paths or []) if isinstance(p, str) and p]
            if not paths:
                paths = ["/_actions", "/_router", "/_devtools"]
            proxy_lines = [
                "  server: {",
                "    proxy: {",
                *[
                    f"      '{path}': {{ target: '{config.proxy}', changeOrigin: true }},"
                    for path in paths
                ],
                "    },",
                "  },",
            ]
        vite_config.write_text(
            "\n".join(
                [
                    "import { defineConfig } from 'vite';",
                    "import tailwind from '@tailwindcss/vite';",
                    "import react from '@vitejs/plugin-react';",
                    "",
                    "export default defineConfig({",
                    "  plugins: [react(), tailwind()],",
                    "  ssr: {",
                    "    noExternal: true,",
                    "  },",
                    *proxy_lines,
                    "});",
                    "",
                ]
            ),
            encoding="utf-8",
        )
    else:
        try:
            existing = vite_config.read_text(encoding="utf-8")
        except OSError:
            existing = ""
        updated_existing = existing
        if "@tailwindcss/vite" not in updated_existing and "plugins: [react()]" in updated_existing:
            lines = existing.splitlines()
            new_lines: list[str] = []
            inserted = False
            for line in lines:
                new_lines.append(line)
                if "defineConfig" in line and "from 'vite'" in line:
                    new_lines.append("import tailwind from '@tailwindcss/vite';")
                    inserted = True
            if not inserted and lines:
                new_lines.insert(1, "import tailwind from '@tailwindcss/vite';")
            updated_existing = "\n".join(new_lines)
            updated_existing = updated_existing.replace("plugins: [react()],", "plugins: [react(), tailwind()],")

        if "ssr:" not in updated_existing:
            lines = updated_existing.splitlines()
            new_lines: list[str] = []
            inserted = False
            for line in lines:
                new_lines.append(line)
                if "plugins:" in line and not inserted:
                    new_lines.append("  ssr: {")
                    new_lines.append("    noExternal: true,")
                    new_lines.append("  },")
                    inserted = True
            if inserted:
                updated_existing = "\n".join(new_lines)

        if updated_existing != existing:
            vite_config.write_text(
                updated_existing + ("\n" if not updated_existing.endswith("\n") else ""),
                encoding="utf-8",
            )

    tsconfig = out_dir / "tsconfig.json"
    if not tsconfig.exists():
        tsconfig.write_text(
            json.dumps(
                {
                    "compilerOptions": {
                        "target": "ES2020",
                        "useDefineForClassFields": True,
                        "lib": ["ES2020", "DOM", "DOM.Iterable"],
                        "module": "ESNext",
                        "skipLibCheck": True,
                        "moduleResolution": "Bundler",
                        "resolveJsonModule": True,
                        "isolatedModules": True,
                        "noEmit": True,
                        "jsx": "react-jsx",
                        "strict": False,
                    },
                    "include": ["src"],
                    "references": [{"path": "./tsconfig.node.json"}],
                },
                indent=2,
            ),
            encoding="utf-8",
        )

    tsconfig_node = out_dir / "tsconfig.node.json"
    if not tsconfig_node.exists():
        tsconfig_node.write_text(
            json.dumps(
                {
                    "compilerOptions": {
                        "composite": True,
                        "skipLibCheck": True,
                        "module": "ESNext",
                        "moduleResolution": "Bundler",
                    },
                    "include": ["vite.config.ts"],
                },
                indent=2,
            ),
            encoding="utf-8",
        )

    src_dir = config.resolve_src_dir(root)
    src_dir.mkdir(parents=True, exist_ok=True)

    vite_env = src_dir / "vite-env.d.ts"
    if not vite_env.exists():
        vite_env.write_text(
            "/// <reference types=\"vite/client\" />\n",
            encoding="utf-8",
        )

    actions_client = src_dir / "actions.ts"
    if not actions_client.exists():
        actions_client.write_text(
            "\n".join(
                [
                    "export type ActionMeta = {",
                    "  csrf?: string;",
                    "  ts?: number;",
                    "  nonce?: string;",
                    "  sig?: string;",
                    "};",
                    "",
                    "export type ActionPayload = {",
                    "  action: string;",
                    "  args?: unknown[];",
                    "  kwargs?: Record<string, unknown>;",
                    "  meta?: ActionMeta;",
                    "};",
                    "",
                    "export type ActionError = {",
                    "  message: string;",
                    "  type: string;",
                    "};",
                    "",
                    "export type ActionResponse<T> =",
                    "  | { ok: true; data: T }",
                    "  | { ok: false; error: ActionError };",
                    "",
                    "export type ActionCallContext = {",
                    "  action: string;",
                    "  args: unknown[];",
                    "  kwargs: Record<string, unknown>;",
                    "};",
                    "",
                    "export type ActionMetaProvider =",
                    "  | ActionMeta",
                    "  | ((ctx: ActionCallContext) => ActionMeta | Promise<ActionMeta>);",
                    "",
                    "export type ActionClientOptions = {",
                    "  endpoint?: string;",
                    "  baseUrl?: string;",
                    "  fetcher?: typeof fetch;",
                    "  meta?: ActionMetaProvider;",
                    "};",
                    "",
                    "export function csrfMetaFromCookie(cookieName = 'csrf_token'): ActionMeta | undefined {",
                    "  if (typeof document === 'undefined') return undefined;",
                    "  const match = document.cookie.match(new RegExp(`(?:^|; )${cookieName}=([^;]*)`));",
                    "  if (!match) return undefined;",
                    "  return { csrf: decodeURIComponent(match[1]) };",
                    "}",
                    "",
                    "export async function fetchCsrfToken(endpoint = '/_actions/csrf', baseUrl = '', fetcher: typeof fetch = globalThis.fetch.bind(globalThis)): Promise<string> {",
                    "  const response = await fetcher(baseUrl + endpoint, { method: 'GET', credentials: 'include' });",
                    "  const payload = (await response.json()) as { csrf?: string };",
                    "  return payload.csrf ?? '';",
                    "}",
                    "",
                    "export function createActionMeta(options: { csrfCookie?: string; includeTs?: boolean; includeNonce?: boolean } = {}): ActionMeta {",
                    "  const meta: ActionMeta = {};",
                    "  if (options.includeTs ?? true) {",
                    "    meta.ts = Math.floor(Date.now() / 1000);",
                    "  }",
                    "  if (options.includeNonce ?? true) {",
                    "    meta.nonce = (globalThis.crypto?.randomUUID?.() ?? `${Date.now()}-${Math.random()}`);",
                    "  }",
                    "  const csrfMeta = csrfMetaFromCookie(options.csrfCookie ?? 'csrf_token');",
                    "  if (csrfMeta?.csrf) {",
                    "    meta.csrf = csrfMeta.csrf;",
                    "  }",
                    "  return meta;",
                    "}",
                    "",
                    "export function createActionMetaProvider(options: { endpoint?: string; baseUrl?: string; csrfCookie?: string; includeTs?: boolean; includeNonce?: boolean } = {}): ActionMetaProvider {",
                    "  let inflight: Promise<string> | null = null;",
                    "  return async () => {",
                    "    let meta = createActionMeta({",
                    "      csrfCookie: options.csrfCookie,",
                    "      includeTs: options.includeTs,",
                    "      includeNonce: options.includeNonce,",
                    "    });",
                    "    if (!meta.csrf) {",
                    "      if (!inflight) {",
                    "        inflight = fetchCsrfToken(options.endpoint ?? '/_actions/csrf', options.baseUrl ?? '');",
                    "      }",
                    "      await inflight;",
                    "      meta = createActionMeta({",
                    "        csrfCookie: options.csrfCookie,",
                    "        includeTs: options.includeTs,",
                    "        includeNonce: options.includeNonce,",
                    "      });",
                    "    }",
                    "    return meta;",
                    "  };",
                    "}",
                    "",
                    "function stableStringify(value: unknown): string {",
                    "  if (value === null || value === undefined) return 'null';",
                    "  if (typeof value !== 'object') return JSON.stringify(value);",
                    "  if (Array.isArray(value)) {",
                    "    return '[' + value.map(stableStringify).join(',') + ']';",
                    "  }",
                    "  const obj = value as Record<string, unknown>;",
                    "  const keys = Object.keys(obj).sort();",
                    "  return '{' + keys.map((k) => JSON.stringify(k) + ':' + stableStringify(obj[k])).join(',') + '}';",
                    "}",
                    "",
                    "async function hmacSha256(secret: string, message: string): Promise<string> {",
                    "  if (!globalThis.crypto?.subtle) {",
                    "    throw new Error('WebCrypto is not available for HMAC signatures');",
                    "  }",
                    "  const encoder = new TextEncoder();",
                    "  const key = await globalThis.crypto.subtle.importKey('raw', encoder.encode(secret), { name: 'HMAC', hash: 'SHA-256' }, false, ['sign']);",
                    "  const signature = await globalThis.crypto.subtle.sign('HMAC', key, encoder.encode(message));",
                    "  const bytes = new Uint8Array(signature);",
                    "  return Array.from(bytes, (b) => b.toString(16).padStart(2, '0')).join('');",
                    "}",
                    "",
                    "export async function createSignedMeta(secret: string, ctx: ActionCallContext, options: { ts?: number; nonce?: string; csrf?: string } = {}): Promise<ActionMeta> {",
                    "  const ts = options.ts ?? Math.floor(Date.now() / 1000);",
                    "  const nonce = options.nonce ?? (globalThis.crypto?.randomUUID?.() ?? `${Date.now()}-${Math.random()}`);",
                    "  const body = stableStringify({ args: ctx.args, kwargs: ctx.kwargs });",
                    "  const message = `${ctx.action}|${ts}|${nonce}|${body}`;",
                    "  const sig = await hmacSha256(secret, message);",
                    "  return { ts, nonce, sig, csrf: options.csrf };",
                    "}",
                    "",
                    "export function createActionClient(options: ActionClientOptions = {}) {",
                    "  const endpoint = options.endpoint ?? '/_actions';",
                    "  const baseUrl = options.baseUrl ?? '';",
                    "  const fetcher = options.fetcher ?? globalThis.fetch.bind(globalThis);",
                    "  const metaProvider = options.meta;",
                    "  return async function callAction<T>(",
                    "    action: string,",
                    "    args: unknown[] = [],",
                    "    kwargs: Record<string, unknown> = {},",
                    "    init?: RequestInit,",
                    "    meta?: ActionMeta,",
                    "  ): Promise<ActionResponse<T>> {",
                    "    const ctx = { action, args, kwargs };",
                    "    const metaValue = meta ??",
                    "      (typeof metaProvider === 'function' ? await metaProvider(ctx) : metaProvider);",
                    "    const payload: ActionPayload = metaValue",
                    "      ? { action, args, kwargs, meta: metaValue }",
                    "      : { action, args, kwargs };",
                    "    const response = await fetcher(baseUrl + endpoint, {",
                    "      method: 'POST',",
                    "      credentials: init?.credentials ?? 'include',",
                    "      headers: { 'Content-Type': 'application/json', ...(init?.headers || {}) },",
                    "      body: JSON.stringify(payload),",
                    "      ...init,",
                    "    });",
                    "    return (await response.json()) as ActionResponse<T>;",
                    "  };",
                    "}",
                    "",
                ]
            ),
            encoding="utf-8",
        )

    api_client = src_dir / "api" / "client.ts"
    if api_client.exists():
        try:
            content = api_client.read_text(encoding="utf-8")
        except OSError:
            content = ""
        if "Generated placeholder" in content:
            updated = _dedupe_api_client_stub(content)
            if "createApiClient" not in updated:
                stub = "\n".join(
                    [
                        "",
                        "export function createApiClient(options: Partial<ClientOptions> = {}): ApiClient {",
                        "  return new ApiClient({ baseUrl: \"\", ...options });",
                        "}",
                        "export const create_api_client = createApiClient;",
                        "",
                    ]
                )
                updated = updated + stub
            if updated != content:
                api_client.write_text(updated, encoding="utf-8")
    else:
        existing = actions_client.read_text(encoding="utf-8")
        updated = existing
        if "fetchCsrfToken" not in updated:
            updated = (
                updated.rstrip()
                + "\n\n"
                + "\n".join(
                    [
                        "export async function fetchCsrfToken(endpoint = '/_actions/csrf', baseUrl = '', fetcher: typeof fetch = globalThis.fetch.bind(globalThis)): Promise<string> {",
                        "  const response = await fetcher(baseUrl + endpoint, { method: 'GET', credentials: 'include' });",
                        "  const payload = (await response.json()) as { csrf?: string };",
                        "  return payload.csrf ?? '';",
                        "}",
                        "",
                    ]
                )
            )
        if "createActionMetaProvider" not in updated:
            updated = (
                updated.rstrip()
                + "\n\n"
                + "\n".join(
                    [
                        "export function createActionMetaProvider(options: { endpoint?: string; baseUrl?: string; csrfCookie?: string; includeTs?: boolean; includeNonce?: boolean } = {}): ActionMetaProvider {",
                        "  let inflight: Promise<string> | null = null;",
                        "  return async () => {",
                        "    let meta = createActionMeta({",
                        "      csrfCookie: options.csrfCookie,",
                        "      includeTs: options.includeTs,",
                        "      includeNonce: options.includeNonce,",
                        "    });",
                        "    if (!meta.csrf) {",
                        "      if (!inflight) {",
                        "        inflight = fetchCsrfToken(options.endpoint ?? '/_actions/csrf', options.baseUrl ?? '');",
                        "      }",
                        "      await inflight;",
                        "      meta = createActionMeta({",
                        "        csrfCookie: options.csrfCookie,",
                        "        includeTs: options.includeTs,",
                        "        includeNonce: options.includeNonce,",
                        "      });",
                        "    }",
                        "    return meta;",
                        "  };",
                        "}",
                        "",
                    ]
                )
            )
        if "credentials: init?.credentials" not in updated and "method: 'POST'" in updated:
            updated = updated.replace(
                "      method: 'POST',\n",
                "      method: 'POST',\n      credentials: init?.credentials ?? 'include',\n",
                1,
            )
        if updated != existing:
            actions_client.write_text(updated, encoding="utf-8")

    index_css = src_dir / "index.css"
    if not index_css.exists():
        index_css.write_text(
            "\n".join(
                [
                    "@import \"tailwindcss\";",
                    "",
                ]
            ),
            encoding="utf-8",
        )
    else:
        try:
            existing_css = index_css.read_text(encoding="utf-8")
        except OSError:
            existing_css = ""
        lines = [line.strip() for line in existing_css.splitlines() if line.strip()]
        if lines == ["@tailwind base;", "@tailwind components;", "@tailwind utilities;"]:
            index_css.write_text("@import \"tailwindcss\";\n", encoding="utf-8")


def _sanitize_package_name(name: str) -> str:
    """Normalize a package name for package.json."""
    cleaned = name.strip().strip("'").strip('"').strip()
    cleaned = cleaned.replace(" ", "-")
    return cleaned
