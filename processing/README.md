# BACKEND: Processing Pipeline + API

## System Requirements

A shared Docker network is required when running containers manually with `docker run`.
This ensures communication between services via container names instead of localhost.

If using `docker compose`, this network is created automatically.

### Create Docker Network

```bash
docker network create app-network
```

To remove the network (if created manually):

```bash
docker network rm app-network
```

## Startup Order

When running the system manually using `docker run` (without docker compose), containers must be started in a specific order due to explicit service dependencies and required data availability.

1. Storage (MinIO)
2. Backend (API + Processing)
3. Frontend (UI)

## Build & Run Backend Container

Build Processing Image

```bash
docker build -t processing-mvp .
```

Run Processing Container

```bash
docker run --rm \
 --network app-network \
 --env-file ../.env \
 -v $(pwd)/app:/app \
 -v $(pwd)/data:/app/data \
 -p 8000:8000 \
 processing-mvp
```

## Backend Configuration (.env)

## API

The backend exposes a FastAPI-based interface:

- `GET /stac` → returns STAC metadata from MinIO storage: http://localhost:8000/stac
- `GET /tiles/{key}` → returns signed URLs for PMTiles access
- `GET /stats` → runs DuckDB analytics queries on GeoParquet data:
- `GET /features/{uuid}` → returns feature-level data from dataset

## Testing

### Run Pytests

The backend includes a pytest-based test suite for validating the processing pipeline and storage integration.

```bash
docker run --rm processing-mvp pytest
```

## Code Quality Tools (Dev)

The backend includes a set of development tools for code quality and consistency. These tools are intended for local development and CI checks, not for production runtime logic.

The following tools are available inside the container:

- **ruff** → fast linting and import/order checks
- **black** → automatic code formatting
- **mypy** → static type checking

These tools help keep the codebase clean, consistent, and type-safe.

### Example usage (inside container)

```bash
ruff check .
black .
mypy .
```
