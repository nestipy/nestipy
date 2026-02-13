<p align="center">
  <a href="http://nestipy.vercel.app" target="blank"><img src="https://raw.githubusercontent.com/nestipy/nestipy/release-v1/nestipy.png" width="320" alt="Nestipy Logo" /></a>
</p>

<p align="center">A <a href="http://python.org" target="_blank">Python</a> ASGI framework for building modular, efficient and scalable server applications.</p>

## Description

[Nestipy](https://nestipy.vercel.app)

## Installation

```bash
$ uv sync
```

## Running the app

```bash
# development
$ python main.py
```

## Support

**Nestipy** operates under the MIT license, making it an open source initiative. Its expansion is made possible through
the generous sponsorship and backing of remarkable supporters.

## Stay in touch

- Author - [Tsiresy Mila](https://tsiresymila.vercel.app)
- Website - [https://nestipy.vercel.app](https://nestipy.vercel.app)

## License

Nestipy is [MIT licensed](https://raw.githubusercontent.com/nestipy/nestipy/main/LICENSE).
## Frontend (Nestipy Web)

This project includes a Python-based frontend in `app/` plus a Vite scaffold in `web/`.

Build + run both backend and frontend:

```bash
nestipy start --dev --web --web-args "--vite --install"
```

Vite proxy defaults to `http://127.0.0.1:8000`. Override with:

```bash
export NESTIPY_WEB_PROXY=http://127.0.0.1:8001
```

Regenerate typed action client (optional):

```bash
nestipy run web:actions --spec http://127.0.0.1:8000/_actions/schema --output web/src/actions.client.ts
```

Enable RouterSpec for typed HTTP client:

```bash
export NESTIPY_ROUTER_SPEC=1
```

Then generate the typed client:

```bash
nestipy run web:build --spec http://127.0.0.1:8000/_router/spec --lang ts --output web/src/api/client.ts
```