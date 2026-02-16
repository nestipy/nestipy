export type ActionsControllerHandleBody = Record<string, unknown>;

export type FetchLike = (input: RequestInfo, init?: RequestInit) => Promise<Response>;

export interface ClientOptions {
  baseUrl: string;
  fetcher?: FetchLike;
  headers?: Record<string, string>;
}

export type RequestOptions = {
  query?: Record<string, unknown>;
  json?: unknown;
  headers?: Record<string, string>;
};

export type RequestFn = <T>(method: string, path: string, options?: RequestOptions) => Promise<T>;

export class AppControllerApi {
  private _request: RequestFn;

  constructor(request: RequestFn) {
    this._request = request;
  }

  async message(options?: {query: Record<string, unknown>; headers: Record<string, string>; body: unknown; cookies: Record<string, string>}): Promise<string> {
    let path = "/api/message";
    const queryParams = options?.query;
    const headerParams = options?.headers;
    const jsonBody = options?.body;
    const cookieParams = options?.cookies;
    const mergedHeaders = { ...(headerParams ?? {}) };
    if (cookieParams) {
      const cookieHeader = Object.entries(cookieParams)
        .map(([key, value]) => `${key}=${String(value)}`)
        .join("; ");
      if (cookieHeader) mergedHeaders["Cookie"] = cookieHeader;
    }
    return this._request<string>("GET", path, { query: queryParams, json: jsonBody, headers: mergedHeaders });
  }

  async ping(options?: {query: Record<string, unknown>; headers: Record<string, string>; body: unknown; cookies: Record<string, string>}): Promise<string> {
    let path = "/api/ping2";
    const queryParams = options?.query;
    const headerParams = options?.headers;
    const jsonBody = options?.body;
    const cookieParams = options?.cookies;
    const mergedHeaders = { ...(headerParams ?? {}) };
    if (cookieParams) {
      const cookieHeader = Object.entries(cookieParams)
        .map(([key, value]) => `${key}=${String(value)}`)
        .join("; ");
      if (cookieHeader) mergedHeaders["Cookie"] = cookieHeader;
    }
    return this._request<string>("GET", path, { query: queryParams, json: jsonBody, headers: mergedHeaders });
  }

}

export class ActionsControllerApi {
  private _request: RequestFn;

  constructor(request: RequestFn) {
    this._request = request;
  }

  async csrf(options?: {query: Record<string, unknown>; headers: Record<string, string>; body: unknown; cookies: Record<string, string>}): Promise<Record<string, unknown>> {
    let path = "/_actions/csrf";
    const queryParams = options?.query;
    const headerParams = options?.headers;
    const jsonBody = options?.body;
    const cookieParams = options?.cookies;
    const mergedHeaders = { ...(headerParams ?? {}) };
    if (cookieParams) {
      const cookieHeader = Object.entries(cookieParams)
        .map(([key, value]) => `${key}=${String(value)}`)
        .join("; ");
      if (cookieHeader) mergedHeaders["Cookie"] = cookieHeader;
    }
    return this._request<Record<string, unknown>>("GET", path, { query: queryParams, json: jsonBody, headers: mergedHeaders });
  }

  async handle(options?: { body?: ActionsControllerHandleBody , query: Record<string, unknown>; headers: Record<string, string>; cookies: Record<string, string>}): Promise<Record<string, unknown>> {
    let path = "/_actions";
    const queryParams = options?.query;
    const headerParams = options?.headers;
    const jsonBody = options?.body;
    const cookieParams = options?.cookies;
    const mergedHeaders = { ...(headerParams ?? {}) };
    if (cookieParams) {
      const cookieHeader = Object.entries(cookieParams)
        .map(([key, value]) => `${key}=${String(value)}`)
        .join("; ");
      if (cookieHeader) mergedHeaders["Cookie"] = cookieHeader;
    }
    return this._request<Record<string, unknown>>("POST", path, { query: queryParams, json: jsonBody, headers: mergedHeaders });
  }

  async schema(options?: {query: Record<string, unknown>; headers: Record<string, string>; body: unknown; cookies: Record<string, string>}): Promise<Record<string, unknown>> {
    let path = "/_actions/schema";
    const queryParams = options?.query;
    const headerParams = options?.headers;
    const jsonBody = options?.body;
    const cookieParams = options?.cookies;
    const mergedHeaders = { ...(headerParams ?? {}) };
    if (cookieParams) {
      const cookieHeader = Object.entries(cookieParams)
        .map(([key, value]) => `${key}=${String(value)}`)
        .join("; ");
      if (cookieHeader) mergedHeaders["Cookie"] = cookieHeader;
    }
    return this._request<Record<string, unknown>>("GET", path, { query: queryParams, json: jsonBody, headers: mergedHeaders });
  }

}

export class ApiClient {
  private _baseUrl: string;
  private _fetcher: FetchLike;
  private _headers: Record<string, string>;
  public readonly AppController: AppControllerApi;
  public readonly ActionsController: ActionsControllerApi;
  public readonly App: AppControllerApi;
  public readonly Actions: ActionsControllerApi;

  constructor(options: ClientOptions) {
    this._baseUrl = options.baseUrl.replace(/\/+$/, "");
    this._fetcher = options.fetcher ?? globalThis.fetch.bind(globalThis);
    this._headers = options.headers ?? {};
    this.AppController = new AppControllerApi(this._request.bind(this));
    this.ActionsController = new ActionsControllerApi(this._request.bind(this));
    this.App = this.AppController;
    this.Actions = this.ActionsController;
  }

  private _joinUrl(path: string): string {
    if (path.startsWith("http://") || path.startsWith("https://")) {
      return path;
    }
    return `${this._baseUrl}/${path.replace(/^\/+/, "")}`;
  }

  private _buildQuery(query?: Record<string, unknown>): string {
    if (!query) return "";
    const params = new URLSearchParams();
    for (const [key, value] of Object.entries(query)) {
      if (value === undefined || value === null) continue;
      params.append(key, String(value));
    }
    const qs = params.toString();
    return qs ? `?${qs}` : "";
  }

  private async _request<T>(
    method: string,
    path: string,
    options?: RequestOptions,
  ): Promise<T> {
    const url = this._joinUrl(path) + this._buildQuery(options?.query);
    const headers: Record<string, string> = { ...this._headers, ...(options?.headers ?? {}) };
    let body: BodyInit | undefined = undefined;
    if (options && options.json !== undefined) {
      body = JSON.stringify(options.json);
      if (!headers["content-type"]) {
        headers["content-type"] = "application/json";
      }
    }
    const response = await this._fetcher(url, { method, headers, body });
    if (!response.ok) {
      const message = await response.text();
      throw new Error(`${response.status} ${response.statusText}: ${message}`);
    }
    if (response.status === 204) {
      return undefined as unknown as T;
    }
    const text = await response.text();
    try {
      return JSON.parse(text) as T;
    } catch {
      return text as unknown as T;
    }
  }

}

export function createApiClient(options: Partial<ClientOptions> = {}): ApiClient {
  return new ApiClient({ baseUrl: "", ...options });
}
export const create_api_client = createApiClient;