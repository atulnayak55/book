# Deployment

This repo is set up to run on a VM with Docker Compose and Caddy serving the frontend.

## Expected Public URL

The current default target is:

- `http://46.225.99.187`

Password reset emails will use that public URL.

## Steps

1. Copy `.env.example` to `.env`
2. Fill in at least:
   - `APP_HOST`
   - `POSTGRES_PASSWORD`
   - `JWT_SECRET_KEY`
   - `RESEND_API_KEY`
   - `EMAIL_FROM`
3. For HTTPS on a real domain, also set:
   - `APP_SCHEME=https`
   - `APP_SITE=your-domain.example`
4. Open port `80` on the VM firewall/security group
5. If using HTTPS, also open port `443`
6. From the repo root run:

```bash
docker compose up -d --build
```

## Services

- `caddy`: serves the built React app and proxies `/api/*` to FastAPI
- `backend`: runs Alembic migrations and starts FastAPI on internal port `8000`
- `db`: PostgreSQL 16 with a persistent named volume

## Notes

- The frontend talks to the backend through same-origin `/api`
- Uploaded files are persisted in the `backend_uploads` volume
- PostgreSQL data is persisted in the `postgres_data` volume
- If `APP_SITE` is a real domain, Caddy can manage HTTPS automatically
- If you deploy directly on a raw IP, keep `APP_SCHEME=http` and `APP_SITE=:80`
