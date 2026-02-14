export type ActionMeta = {
  csrf?: string;
  ts?: number;
  nonce?: string;
  sig?: string;
};

export type ActionPayload = {
  action: string;
  args?: unknown[];
  kwargs?: Record<string, unknown>;
  meta?: ActionMeta;
};

export type ActionError = {
  message: string;
  type: string;
};

export type ActionResponse<T> =
  | { ok: true; data: T }
  | { ok: false; error: ActionError };

export type ActionCallContext = {
  action: string;
  args: unknown[];
  kwargs: Record<string, unknown>;
};

export type ActionMetaProvider =
  | ActionMeta
  | ((ctx: ActionCallContext) => ActionMeta | Promise<ActionMeta>);

export type ActionClientOptions = {
  endpoint?: string;
  baseUrl?: string;
  fetcher?: typeof fetch;
  meta?: ActionMetaProvider;
};

export function csrfMetaFromCookie(cookieName = 'csrf_token'): ActionMeta | undefined {
  if (typeof document === 'undefined') return undefined;
  const match = document.cookie.match(new RegExp(`(?:^|; )${cookieName}=([^;]*)`));
  if (!match) return undefined;
  return { csrf: decodeURIComponent(match[1]) };
}

export async function fetchCsrfToken(
  endpoint = '/_actions/csrf',
  baseUrl = '',
  fetcher: typeof fetch = globalThis.fetch.bind(globalThis),
): Promise<string> {
  const response = await fetcher(baseUrl + endpoint, { method: 'GET', credentials: 'include' });
  const payload = (await response.json()) as { csrf?: string };
  return payload.csrf ?? '';
}

export function createActionMeta(options: { csrfCookie?: string; includeTs?: boolean; includeNonce?: boolean } = {}): ActionMeta {
  const meta: ActionMeta = {};
  if (options.includeTs ?? true) {
    meta.ts = Math.floor(Date.now() / 1000);
  }
  if (options.includeNonce ?? true) {
    meta.nonce = (globalThis.crypto?.randomUUID?.() ?? `${Date.now()}-${Math.random()}`);
  }
  const csrfMeta = csrfMetaFromCookie(options.csrfCookie ?? 'csrf_token');
  if (csrfMeta?.csrf) {
    meta.csrf = csrfMeta.csrf;
  }
  return meta;
}

export function createActionMetaProvider(options: { endpoint?: string; baseUrl?: string; csrfCookie?: string; includeTs?: boolean; includeNonce?: boolean } = {}): ActionMetaProvider {
  let inflight: Promise<string> | null = null;
  return async () => {
    let meta = createActionMeta({
      csrfCookie: options.csrfCookie,
      includeTs: options.includeTs,
      includeNonce: options.includeNonce,
    });
    if (!meta.csrf) {
      if (!inflight) {
        inflight = fetchCsrfToken(options.endpoint ?? '/_actions/csrf', options.baseUrl ?? '');
      }
      await inflight;
      meta = createActionMeta({
        csrfCookie: options.csrfCookie,
        includeTs: options.includeTs,
        includeNonce: options.includeNonce,
      });
    }
    return meta;
  };
}

function stableStringify(value: unknown): string {
  if (value === null || value === undefined) return 'null';
  if (typeof value !== 'object') return JSON.stringify(value);
  if (Array.isArray(value)) {
    return '[' + value.map(stableStringify).join(',') + ']';
  }
  const obj = value as Record<string, unknown>;
  const keys = Object.keys(obj).sort();
  return '{' + keys.map((k) => JSON.stringify(k) + ':' + stableStringify(obj[k])).join(',') + '}';
}

async function hmacSha256(secret: string, message: string): Promise<string> {
  if (!globalThis.crypto?.subtle) {
    throw new Error('WebCrypto is not available for HMAC signatures');
  }
  const encoder = new TextEncoder();
  const key = await globalThis.crypto.subtle.importKey(
    'raw',
    encoder.encode(secret),
    { name: 'HMAC', hash: 'SHA-256' },
    false,
    ['sign'],
  );
  const signature = await globalThis.crypto.subtle.sign('HMAC', key, encoder.encode(message));
  const bytes = new Uint8Array(signature);
  return Array.from(bytes, (b) => b.toString(16).padStart(2, '0')).join('');
}

export async function createSignedMeta(
  secret: string,
  ctx: ActionCallContext,
  options: { ts?: number; nonce?: string; csrf?: string } = {},
): Promise<ActionMeta> {
  const ts = options.ts ?? Math.floor(Date.now() / 1000);
  const nonce = options.nonce ?? (globalThis.crypto?.randomUUID?.() ?? `${Date.now()}-${Math.random()}`);
  const body = stableStringify({ args: ctx.args, kwargs: ctx.kwargs });
  const message = `${ctx.action}|${ts}|${nonce}|${body}`;
  const sig = await hmacSha256(secret, message);
  return { ts, nonce, sig, csrf: options.csrf };
}

export function createActionClient(options: ActionClientOptions = {}) {
  const endpoint = options.endpoint ?? '/_actions';
  const baseUrl = options.baseUrl ?? '';
  const fetcher = options.fetcher ?? globalThis.fetch.bind(globalThis);
  const metaProvider = options.meta;

  return async function callAction<T>(
    action: string,
    args: unknown[] = [],
    kwargs: Record<string, unknown> = {},
    init?: RequestInit,
    meta?: ActionMeta,
  ): Promise<ActionResponse<T>> {
    const ctx = { action, args, kwargs };
    const metaValue = meta ??
      (typeof metaProvider === 'function' ? await metaProvider(ctx) : metaProvider);
    const payload: ActionPayload = metaValue
      ? { action, args, kwargs, meta: metaValue }
      : { action, args, kwargs };
    const response = await fetcher(baseUrl + endpoint, {
      method: 'POST',
      credentials: init?.credentials ?? 'include',
      headers: { 'Content-Type': 'application/json', ...(init?.headers || {}) },
      body: JSON.stringify(payload),
      ...init,
    });
    return (await response.json()) as ActionResponse<T>;
  };
}