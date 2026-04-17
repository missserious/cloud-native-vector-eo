# [Cloud-Native Architecture for Vector EO Products](#)

There is a growing demand for services that process **vector data**. This repository proposes a **cloud-native architecture** to support such services.

- [Data Flow](#data-flow)
- [Data Products](#data-products)
- [Local Development / Setup](#local-development--setup)
- [API Overview](#api-overview)
- [Testing](#testing)
- [Run Pytests](#run-pytests)
- [Setup Verification](#setup-verification)
- [Test minIO](#test-minio)
- [Test processing webserver](#test-processing-webserver)
- [Test frontend](#test-frontend)
- [Troubleshooting](#troubleshooting)
- [Project Structure](#project-structure)

## Architecture Overview

This solution is implemented using **three Docker containers**:

> ℹ️ Note: This is a note! ⚠️

```md
> API + PROCESSING Container

    Step 1: Handles transformation of vector data. It reads GeoJSON input files, validates and processes geospatial data, and generates output files such as GeoParquet, MBTiles, and PMTiles.
    Step 2: After processing, the resulting artifacts are uploaded to **MinIO STORAGE**.
    Step 3: API Endpoint.
```

```md
> MinIO STORAGE Container

    Provides persistent object storage using **MinIO**. It stores processed vector data uploaded by the Processing container and serves it via an S3-compatible API.
    Provides two types of geospatial data access:
    	1.  Static tile-based visualization (PMTiles) for map rendering **in the frontend**.
    	2.  Analytical vector datasets (GeoParquet) stored in object storage, intended for query-based access via the FastAPI layer.
    GeoParquet files are not consumed directly by the frontend.
    They are accessed via query endpoints in the Processing API using DuckDB.
```

```md
> FRONTEND Container

    Provides a user interface to visualize and interact with the vector data stored in the **Storage Container**.
```

```
                        ┌───────────────────────┐
                        │       FRONTEND        │
                        │ (Browser / React)     │
                        └──────────┬────────────┘
                                   │
               GET /results        │      Download
             (request signed URLs) │      processed pmtiles
                                   │
            ┌──────────────────────┴─────────────────────────┐
            │                                                │
            │                                                │
            ▼                                                ▼
┌────────────────────────┐                      ┌────────────────────────┐
│   API + PROCESSING     │                      │        MINIO           │
│   (FastAPI Container)  │                      │   Object Storage       │
│                        │                      │                        │
│  POST /process         │                      │ - parquet outputs      │
│  → runs pipeline       │                      │ - pmtiles tiles        │
│  → uploads to MinIO    │                      │                        │
│                        │                      │                        │
│  GET /results          │                      │                        │
│  → generates signed    │                      │                        │
│    URLs                │                      │                        │
└──────────┬─────────────┘                      └──────────┬─────────────┘
           │                                               ▲
           │ signed URLs                                   │
           └───────────────────────────────────────────────┘
                        direct parquet access

```

## Data Flow

## Data Products

## Local Development / Setup

To get the architecture running locally, follow these **7 main steps**:

**Step 1: Create Docker Network**
This allows containers to communicate with each other.

```bash
sudo docker network create app-network
```

**Step 2: Build Processing Image**

```bash
sudo docker build -t processing-mvp .
```

**Step 3: Build Storage Image**

```bash
sudo docker build -t minio-storage-mvp .
```

**Step 4: Run Storage Container**

```bash
sudo docker run -d --name minio \
 --network app-network \
--env-file ../.env \
 -p 9000:9000 -p 9001:9001 \
 -v $(pwd)/minio_data:/data \
 minio-storage-mvp
```

**Troubleshooting**: MinIO is not reachable after system restart

If the container already exists but is stopped (e.g., after shutting down your machine), you can restart it with:

```bash
sudo docker start minio
```

**Step 5: Run Processing Container**

```bash
sudo docker run --rm \
 --network app-network \
 --env-file ../.env \
 -v $(pwd)/app:/app \
 -v $(pwd)/data:/app/data \
 -p 8000:8000 \
 processing-mvp
```

**Step 6: DEV: Build Frontend Image**

```bash
sudo docker build -f Dockerfile.dev -t frontend-mvp-dev .
```

**Step 7: DEV: Run Frontend Container**

```bash
sudo docker run --rm \
  --network app-network \
  --env-file ../.env \
  -e CHOKIDAR_USEPOLLING=true \
  -p 5173:5173 \
  -v $(pwd):/app \
  -v /app/node_modules \
  frontend-mvp-dev
```

**Step 8: PROD: Build Frontend Image**

```bash
sudo docker build -t frontend-mvp-prod .
```

**Step 9: PROD: Run Frontend Container**

```bash
sudo docker run --rm \
  --network app-network \
  --env-file ../.env \
  -p 8080:80 \
  frontend-mvp-prod
```

## API Overview

## Testing

### Run Pytests

```bash
sudo docker run --rm processing-mvp pytest
```

## Setup Verification

### Test minIO

Access MinIO Interface via Browser:
`http://localhost:9001`
enter credentials

### Test processing webserver

Access webserver via Browser:
`http://localhost:8000/results`

### Test frontend

Access frontend via Browser:
`http://localhost:8080`

## Troubleshooting

## Project Structure

## TODO'S / Roadmap

- Processing Container
  - [x] Entry Point: API Layer - startup
    - [ ] Orchestration: bucket, input_file_path, pipeline run(), signed urls, endpoint creation
      - [x] Single File Pipeline: class ConversionPipeline
      - [x] run: manages pipeline, validation and conversion
      - [x] Convert MBTiles → PMTiles
      - [x] Convert GeoJSON → GeoParquet (analytics dataset):
        - [x] Solution A: geopandas (+ pandas, + pyarrow, +shapely)
        - [x] Solution B: GDAL / ogr2ogr + ⚠️ parquet support
    - [ ] Upload: class MinioStorage
      - [x] Configure access to MinIO (endpoint, keys)
      - [x] Create bucket for PMTiles in MinIO
      - [x] Upload processed files (1 pmtiles and 2 parquets to MinIO (boto3))
      - [ ] get_signed_url
  - [ ] API Endpoint creation - Flow - Signed urls
    - [ ] 1. container start
    - [ ] 2. API (uvicorn) start
    - [ ] 3. Post /process gets results
    - [ ] 4. pipeline runs once
    - [ ] 5. data upload to minIO
    - [ ] API stays active
    - [ ] GET /results always possible
    - [ ] Test Endpoint with curl
    - [x] Change batch container to service container
    - [x] Webserver: uvicorn
  - [ ] API Endpoint creation - Flow - geoparquet
    - [ ] connection to minIO - duckdb
    - [ ] Endpoint for features
  - [ ] Input contract: All input GeoJSON files are expected to be: In WGS84 (EPSG:4326)
    - [ ] Add input format support via loader layer (GeoJSON, FlatGeobuf (.fgb), GeoPackage (.gpkg))
  - [ ] Dataset KEY: for tiles - geoparquet communication

  - [ ] Tests: pytest
    - [x] Basic setup
    - [x] Prepare and test testdata and upload per lfs
    - [ ] Test case: Basic testing pipeline with testdata
    - [ ] Test case: Basic testing connection to minIO
  - [ ] Basic logging / error handling
  - [ ] Linting / Prettier integration for Processing container > documentation

- Storage Container (MinIO)
  - [x] Setup MinIO container

- Frontend Container
  - [x] Setup
    - [x] Vite (Build Tool)
    - [x] React
    - [x] TypeScript
    - [x] Prod and Dev
    - [x] npm install local!!!

  - [ ] Mapping / Visualization
    - [ ] React Map GL (React Wrapper Library) - NOT FOR NOW
    - [x] PMTiles Protocol Plugin
    - [x] MapLibre GL(Map-Engine) + Typen + CSS +
    - [ ] Display STAC Item Example with Classification + Render

  - [x] Styling
    - [x] Tailwind CSS

  - [ ] Code Quality
    - [ ] ESLint
    - [ ] Prettier
    - [ ] Pre-commit hooks (husky & lint-staged)

### Optional / Architecture Features & Future Improvements

- [x] Docker Network
  - Enables communication between containers.
  - Without it, localhost in one container points only to itself, so containers cannot reach each other.
  - By putting them in the same network, containers can communicate via their container names.

- [ ] Docker Compose orchestration (Processing + Storage + Frontend)
  - [ ] Processing Dockerfile: see TODOs
- [ ] Development environment configurations (env files, debug setup)
- [ ] Documentation (setup + workflow) - Table of overview
  - [ ] Docker Diagram (e.g. Mermaid/PNG)

### Nice to have

- [ ] Processing: **multi-stage docker build** for clean/minimal image
  - Stage 1: Build PMTiles CLI + any other temporary tools (e.g., curl, tar)
  - Stage 2: Runtime stage with only Python3, Tippecanoe, PMTiles CLI + scripts
  - Alternative for single-stage MVP: purge temporary tools (curl, tar) after installation
- [ ] Processing: DEV-SERVER
  - Hot Reload (Issue: watchdog)
- [ ] Processing: in PROD: versioned upload
- [ ] Processing: Exception handling (DEV vs PROD)
  - DEV: full stacktrace for debugging
  - PROD: clean error output for users
  - Controlled via ENV variable DEBUG
- [ ] Processing: FastAPI Lifespan Context instead of on_event
