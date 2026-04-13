# [Cloud-Native Architecture for Vector EO Products](#)

## Context

There is a growing demand for services that process **vector data**. This repository proposes a **cloud-native architecture** to support such services.

## Architecture Overview

This solution is implemented using **three Docker containers**:

1. **Processing Container**

   **Step 1:** Handles transformation of vector data. It reads GeoJSON input files, validates and processes geospatial data, and generates output files such as GeoParquet, MBTiles, and PMTiles.

   **Step 2:** After processing, the resulting artifacts are uploaded to the **Storage container (MinIO)**.

2. **Storage Container**  
   Provides persistent object storage using **MinIO**. It stores processed vector data uploaded by the Processing container and serves it via an S3-compatible API. Provides the data for the **frontend**.

3. **Frontend Container**  
   Provides a user interface to visualize and interact with the vector data stored in the **Storage Container** .

## Local Development / Setup Steps

To get the architecture running locally, follow these **five main steps**:

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
 -v $(pwd):/app \
 processing-mvp
```

## Test Local Setup

### Test minIO

Access MinIO Interface via Browser:
`http://localhost:9001`
enter credentials

### Run Pytests

```bash
sudo docker run --rm processing-mvp pytest
```

## TODO'S

- Processing Container
  - [ ] Entry Point: main: input_file_path, call run(), start pipeline, start upload
  - [ ] Single File Pipeline: class ConversionPipeline
    - [ ] run: manages pipeline, validation and conversion
      - [x] Convert MBTiles → PMTiles
      - [x] Convert GeoJSON → GeoParquet (analytics dataset):
        - [x] Solution A: geopandas (+ pandas, + pyarrow, +shapely)
        - [x] Solution B: GDAL / ogr2ogr + ⚠️ parquet support
  - [ ] Upload: class MinioStorage
    - [x] Configure access to MinIO (endpoint, keys)
    - [x] Create bucket for PMTiles in MinIO
    - [ ] Upload processed files (1 pmtiles and 2 parquets to MinIO (boto3))
  - [ ] Tests: pytest (connection2minIO)
  - [ ] Basic logging / error handling
  - [ ] Linting / Prettier integration for Processing container
  - [ ] Hot Reload (Issue: watchdog)
  - [ ] PROD: versioned upload

- Storage Container (MinIO)
  - [x] Setup MinIO container

- Frontend Container
  - [ ] Setup
    - [ ] Vite (Build Tool)
    - [ ] React
    - [ ] TypeScript

  - [ ] Mapping / Visualization
    - [ ] React Map GL
    - [ ] MapLibre GL JS
    - [ ] Display STAC Item Example with Classification + Render

  - [ ] Styling
    - [ ] Tailwind CSS

  - [ ] Code Quality
    - [ ] ESLint
    - [ ] Prettier
    - [ ] Pre-commit hooks (husky & lint-staged)

### Optional / Architecture Features & Future Improvements

- [ ] Docker Diagram (e.g. Mermaid/PNG)
- [x] Docker Network  
       Enables communication between containers.  
       Without it, localhost in one container points only to itself, so containers cannot reach each other.  
       By putting them in the same network, containers can communicate via their container names.

- [ ] Docker Compose orchestration (Processing + Storage + Frontend)
  - [ ] Processing Dockerfile: see TODOs
- [ ] Development environment configurations (env files, debug setup)
- [ ] Basic testing (pipeline & storage)
- [ ] Documentation (setup + workflow)
