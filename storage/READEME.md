# MINIO: Object Storage

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

## Build & Run Storage Container

Build Storage Image

```bash
docker build -t minio-storage-mvp .
```

Run Storage Container

```bash
docker run -d \
  --name minio \
  --network app-network \
  --env-file ../.env \
  -p 9000:9000 \
  -p 9001:9001 \
  -v $(pwd)/minio_data:/data \
  minio-storage-mvp
```

ℹ️ The container must be started after the Docker network has been created.

If the container already exists but is stopped (e.g. after restarting your machine), you can restart it with:

```bash
docker start minio
```

## Storage Configuration (.env)

All configuration for the storage container is managed via environment variables defined in the [.env file](../.env). This includes:

- **Bucket name** used for all stored assets
- Access **credentials**
