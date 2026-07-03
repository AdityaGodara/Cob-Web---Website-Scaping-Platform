# Cob Web — Website Scraping Platform

A full-stack web scraping platform with a React frontend, FastAPI backend, Celery task worker, PostgreSQL database, Redis broker/cache, and Nginx reverse proxy.

## What this project does

Cob Web provides a production-ready scraping workflow:

- Accepts scraping jobs through a web interface and API.
- Uses WebSockets to stream job progress updates to the frontend.
- Dispatches background scraping tasks to Celery workers.
- Stores scraped data and job metadata in PostgreSQL.
- Supports scalable task execution with Redis as Celery broker/backend.
- Serves the frontend and API behind an Nginx gateway.

## Tech stack

- Backend: Python 3.12, FastAPI, SQLAlchemy, Pydantic, Celery
- Database: PostgreSQL 17
- Broker / cache: Redis 7
- Frontend: React, TypeScript, Vite
- Reverse proxy: Nginx
- Container orchestration: Docker Compose

## Production architecture

The production architecture is container-based and includes the following services:

1. **Nginx**
   - Acts as the public edge router.
   - Routes `/api/*` to the FastAPI backend.
   - Routes `/ws/*` through to the backend with WebSocket support.
   - Routes all other requests to the static React frontend.

2. **Frontend**
   - Built with React + TypeScript and served as static assets by Nginx.
   - Connects to the API and WebSocket endpoints for scraping job management and live progress.

3. **API**
   - FastAPI application exposing REST endpoints under `/api/v1`.
   - Exposes a health check and WebSocket routes for live updates.
   - Reads configuration from `.env` for database and Redis connection strings.

4. **Worker**
   - Celery worker executes scraping tasks asynchronously.
   - Uses Redis as both broker and result backend.
   - Autodiscover tasks from `app.workers`.

5. **PostgreSQL**
   - Persists job definitions, job URLs, scrape results, and metadata.
   - Uses SQLAlchemy for ORM access.

6. **Redis**
   - Manages Celery task queue and task results.
   - Also supports runtime cache or WebSocket state if required.

## Repository structure

- `app/` — Python backend implementation
- `frontend/` — React + TypeScript frontend
- `nginx/` — Nginx configuration for reverse proxying API, WebSockets, and frontend
- `Dockerfile` — backend image definition
- `docker-compose.yml` — local compose development stack
- `docker-compose-prod.yml` — production-style compose stack
- `pyproject.toml` — backend Python dependencies

## Environment variables

Create a `.env` file in the root folder with values like:

```env
app_name=Cob Web
app_version=0.1.0
db_url=postgresql+psycopg://postgres:password@postgres:5432/cobweb
redis_url=redis://redis:6379/0
debug=False
```

> Note: `db_url` and `redis_url` must point to the service names used by Docker Compose when running inside containers.

## Run locally with Docker Compose

The easiest way to run Cob Web on any machine is with Docker Compose.

```bash
docker compose up --build
```

This starts:

- `postgres` database
- `redis` broker
- `api` FastAPI service
- `worker` Celery background worker
- `frontend` React app
- `nginx` reverse proxy on port `80`

Then open `http://localhost` in your browser.

## Run production-style stack

For the production compose file, use:

```bash
docker compose -f docker-compose-prod.yml up --build
```

## Frontend development

From `frontend/`:

```bash
npm install
npm run dev
```

Or build the static assets for production:

```bash
npm install
npm run build
```

## Backend development

From the project root, use Python 3.12 and install dependencies using a virtual environment. Example:

```bash
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install -U pip
python -m pip install uv
python -m pip install -e .
```

Then run the API locally:

```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Useful commands

- `docker compose up --build` — start the full stack
- `docker compose down` — stop and remove containers
- `docker compose ps` — list running services
- `npm run build` — build frontend assets
- `uv run uvicorn app.main:app --reload` — run API in dev mode

## Notes

- The backend uses FastAPI plus WebSocket routes for realtime job progress.
- Celery runs tasks from `app.workers.tasks.py` with Redis as the broker.
- Nginx serves the frontend and proxies API/WebSocket traffic.
- PostgreSQL stores all persistent scraper data.

---

Thank you for using Cob Web. If you want, I can also add a `CONTRIBUTING` section or a quick architecture diagram.