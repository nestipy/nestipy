export type AppControllerPostBody = TestBody;
export type AppControllerTestHeaders = {
  headers: Record<string, unknown>;
};
export type AppControllerTestCookies = {
  cookies: Record<string, unknown>;
};
export type UserControllerGetUserHeaders = {
  headers: Record<string, unknown>;
};

export type FetchLike = (input: RequestInfo, init?: RequestInit) => Promise<Response>;

export interface ClientOptions {
  baseUrl: string;
  fetcher?: FetchLike;
  headers?: Record<string, string>;
}

export class ApiClient {
  private _baseUrl: string;
  private _fetcher: FetchLike;
  private _headers: Record<string, string>;

  constructor(options: ClientOptions) {
    this._baseUrl = options.baseUrl.replace(/\/+$/, "");
    this._fetcher = options.fetcher ?? fetch;
    this._headers = options.headers ?? {};
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
    options?: {
      query?: Record<string, unknown>;
      json?: unknown;
      headers?: Record<string, string>;
    },
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

  async post(options?: { body?: AppControllerPostBody }): Promise<unknown> {
    let path = "/";
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
    return this._request<unknown>("POST", path, { query: queryParams, json: jsonBody, headers: mergedHeaders });
  }

  async test(options?: { headers?: AppControllerTestHeaders; cookies?: AppControllerTestCookies }): Promise<unknown> {
    let path = "/";
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
    return this._request<unknown>("GET", path, { query: queryParams, json: jsonBody, headers: mergedHeaders });
  }

  async get_user(options?: { headers?: UserControllerGetUserHeaders }): Promise<Response | Record<string, unknown>> {
    let path = "/users";
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
    return this._request<Response | Record<string, unknown>>("GET", path, { query: queryParams, json: jsonBody, headers: mergedHeaders });
  }

  async get_user_by_id(): Promise<Response | Record<string, unknown>> {
    let path = "/users/{id}";
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
    return this._request<Response | Record<string, unknown>>("POST", path, { query: queryParams, json: jsonBody, headers: mergedHeaders });
  }

}

export type Response = Record<string, unknown>;
export type TestBody = Record<string, unknown>;