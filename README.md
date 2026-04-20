# Cloud-Native Architecture for Vector EO Products

As the demand for **vector data processing** continues to grow, this repository introduces a **cloud-native architecture** to support such services.

## Table of Contents

- [Cloud-Native Architecture for Vector EO Products](#cloud-native-architecture-for-vector-eo-products)
  - [Table of Contents](#table-of-contents)
  - [Architecture Overview](#architecture-overview)
  - [Service Documentation](#service-documentation)
  - [Getting Started](#getting-started)
    - [Prerequisites](#prerequisites)
      - [Git LFS – Test Data Setup](#git-lfs--test-data-setup)
    - [Environment Setup Requirements](#environment-setup-requirements)
    - [Frontend Setup](#frontend-setup)
    - [Run with Docker Compose](#run-with-docker-compose)
  - [After startup:](#after-startup)
  - [API Overview](#api-overview)
  - [Testing](#testing)
    - [Run Pytests](#run-pytests)

## Architecture Overview

```text
FRONTEND: React Container
-------------------------
The frontend is a React-based MapLibre application for interactive visualization of geospatial vector EO products.

It consumes STAC metadata and visualizes vector data through two main data paths:

- Map visualization via PMTiles vector tiles (client-side read)
- Statistical exploration via GeoParquet datasets (storage-read server-side)

All data access is mediated by the backend. The frontend does not access object storage directly. Instead, the backend provides:
- signed URLs for PMTiles access from object storage
- API endpoints for querying GeoParquet datasets using DuckDB
- STAC metadata is retrieved via a backend endpoint.
```

```text
BACKEND: Processing Pipeline + API Container
--------------------------------------------
The backend is responsible for geospatial data processing pipeline execution, storage writing, and serving as the central API layer of the system.

Processing Pipeline:
- Reads GeoJSON input files in ⚠️ valid WGS84 format
- Validates input data
- Generates output formats:
  - GeoParquet (via pandas and ogr2ogr)
  - PMTiles (via MBTiles intermediate step)
- Generates STAC metadata
- Stores all generated artifacts and STAC metadata in MinIO storage (Storage Writer responsibility)

API Layer:
The backend exposes a FastAPI-based interface that provides:
- signed URLs for PMTiles access from object storage
- endpoints for querying GeoParquet datasets using DuckDB (reading directly from object storage)
- endpoints for retrieving STAC metadata from object storage
```

```text
MINIO: Object Storage Container
-------------------------------
Provides persistent S3-compatible object storage for all system data products.

Data Products:
- GeoParquet for analytical access (generated via pandas and ogr2ogr)
- PMTiles for web-based visualization
- STAC metadata for dataset description and discovery
```

```
                        ┌───────────────────────┐
                        │       FRONTEND        │
                        │  (Browser / React)    │
                        └──────────┬────────────┘
                                   │
               GET API             │      Signed URL access
               requests            │      (client-side PMTiles rendering)
                                   │
            ┌──────────────────────┴─────────────────────────┐
            │                                                │
            │                                                │
            ▼                                                ▼
┌───────────┴──────────────┐                    ┌────────────┴────────────┐
│       BACKEND            │                    │        MINIO            │
│   PROCESSING + API       │                    │   Object Storage        │
│                          │                    │                         │
│  Processing              │                    │                         │
│  on container startup    │                    │ - GeoParquet datasets   │
│  → runs pipeline         │                    │ - PMTiles tilesets      │
│  → uploads to MinIO      │                    │ - STAC metadata         │
│                          │                    │                         │
│  API                     │                    │                         │
│  GET /tiles/{key}        │                    │                         │
│  → generates signed URLs │                    │                         │
│  → redirects to MinIO    │                    │                         │
│    via signed URL        │                    │                         │
│  GET /stac               │                    │                         │
│  → metadata              │                    │                         │
│  GET /stats              │                    │                         │
│  → uses geoparquet       │                    │                         │
│                          │                    │                         │
└──────────┬───────────────┘                    └──────────┬──────────────┘
           │                                               ▲
           │ upload (write assets)                         │
           └───────────────────────────────────────────────┘
                                                           │
                          backend read access (GeoParquet via DuckDB)

```

## Service Documentation

Each component contains its own detailed documentation:

- [Frontend README](frontend/README.md)
- [Backend README](processing/README.md)
- [Storage (MinIO) README](storage/README.md)

## Getting Started

This section explains how to run the system locally. The system is fully containerized using Docker Compose.

### Prerequisites

- Git and Git LFS (required for test datasets)
- Docker and Docker Compose
- Node.js ⚠️ (>= 24 required, see [Frontend Setup](#frontend-setup))

#### Git LFS – Test Data Setup

This repository uses Git LFS to manage large test datasets.

Test data is stored in: [processing/tests/data](processing/tests/data) \
See dataset details: [Test Data README](processing/tests/data/README.md)

⚠️ Make sure Git LFS is installed and the data is pulled successfully.\
This is also required to run the pytest suite.

---

### Environment Setup Requirements

Host configuration:

⚠️ Add the following entry to your `/etc/hosts` file:

127.0.0.1 minio

ℹ️ This is required to allow the services to resolve the MinIO endpoint locally.

### Frontend Setup

⚠️ Install frontend dependencies via npm before building/running the frontend container:

```bash
cd frontend
npm install
```

### Run with Docker Compose

Start the full system:

```bash
docker compose up --build
```

## After startup:

- MinIO object storage is initialized and accessible (via web interface at http://localhost:9001, use configured credentials in [.env](.env) file )
- The backend automatically runs the processing pipeline on container startup
- GeoParquet datasets, PMTiles tilesets, and STAC metadata are generated and stored in MinIO
- The FastAPI backend is available at: http://localhost:8000
- The frontend application is available at: http://localhost:8080

## API Overview

The backend exposes a FastAPI-based interface:

- `GET /stac` → returns STAC metadata
- `GET /tiles/{key}` → returns signed URLs for PMTiles access
- `GET /stats` → example endpoint for GeoParquet-based analytics queries

## Testing

### Run Pytests

The backend includes a pytest-based test suite for validating the processing pipeline and storage integration.

```bash
sudo docker run --rm processing-mvp pytest
```
