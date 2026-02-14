// Generated placeholder. Run:
// nestipy run web:build --spec http://127.0.0.1:8000/_router/spec --lang ts --output web/src/api/client.ts

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
    this._baseUrl = options.baseUrl.replace(/\/+$/, '');
    this._fetcher = options.fetcher ?? globalThis.fetch.bind(globalThis);
    this._headers = options.headers ?? {};
  }

  private _joinUrl(path: string): string {
    if (path.startsWith('http://') || path.startsWith('https://')) {
      return path;
    }
    return `${this._baseUrl}/${path.replace(/^\/+/, '')}`;
  }

  async ping(): Promise<string> {
    const url = this._joinUrl('/api/ping');
    const response = await this._fetcher(url, {
      method: 'GET',
      headers: { ...this._headers },
    });
    if (!response.ok) {
      throw new Error(await response.text());
    }
    return response.text();
  }
}