export type ActionPayload = {
  action: string;
  args?: unknown[];
  kwargs?: Record<string, unknown>;
};

export type ActionError = {
  message: string;
  type: string;
};

export type ActionResponse<T> =
  | { ok: true; data: T }
  | { ok: false; error: ActionError };

export type ActionClientOptions = {
  endpoint?: string;
  baseUrl?: string;
  fetcher?: typeof fetch;
};

export function createActionClient(options: ActionClientOptions = {}) {
  const endpoint = options.endpoint ?? '/_actions';
  const baseUrl = options.baseUrl ?? '';
  const fetcher = options.fetcher ?? fetch;
  return async function callAction<T>(
    action: string,
    args: unknown[] = [],
    kwargs: Record<string, unknown> = {},
    init?: RequestInit,
  ): Promise<ActionResponse<T>> {
    const payload: ActionPayload = { action, args, kwargs };
    const response = await fetcher(baseUrl + endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...(init?.headers || {}) },
      body: JSON.stringify(payload),
      ...init,
    });
    return (await response.json()) as ActionResponse<T>;
  };
}
