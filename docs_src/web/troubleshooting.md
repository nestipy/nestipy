# Troubleshooting

- **Actions 403**: ensure you fetched a CSRF token and configured guards.
- **Actions client not updating**: set `NESTIPY_WEB_ACTIONS_WATCH=./src` so schema refetch happens only on backend changes.
- **Router spec 403**: pass token via `/_router/spec?token=...` or `x-router-spec-token` header.
- **Vite proxy not working**: confirm `--proxy` points to backend URL and `--proxy-paths` include `/_actions` and `/api`.
