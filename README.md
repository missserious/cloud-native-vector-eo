# [Cloud-Native Architecture for Vector EO Products](#)

## Context

There is a growing demand for services that process **vector data**. This repository proposes a **cloud-native architecture** to support such services.

## Architecture Overview

This solution is implemented using **three Docker containers**:

1. **Processing Container**  
   Handles transformation of vector data.

2. **Storage Container**  
   Stores processed vector data using **MinIO**. Provides the data for the **frontend**.

3. **Frontend Container**  
   Provides a user interface to visualize and interact with the vector data stored in the Storage container.

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
 -p 9000:9000 -p 9001:9001 \
 -v $(pwd)/minio_data:/data \
 minio-storage-mvp
```

**Step 5: Run Processing Container**

```bash
sudo docker run --rm \
 --network app-network \
 -v $(pwd):/app \
 processing-mvp

```

## Test Local Setup

Access MinIO Interface via Browser:
`http://localhost:9001`
enter credentials

## TODO'S

- Processing Container (2 separate processing steps and 1 upload step)
  - [x] Generate MBTiles from GeoJSON (Tippecanoe)
  - [x] Convert MBTiles → PMTiles
  - [ ] GeoJSON → GeoParquet converstion (analytics dataset)
  - [x] Configure access to MinIO (endpoint, keys)
  - [x] Create bucket for PMTiles in MinIO
  - [ ] Upload PMTiles to MinIO (boto3)
  - [ ] PROD: versioned upload
  - [ ] Basic logging / error handling
  - [ ] Tests: pytest (connection2minIO)
  - [ ] Hot Reload (Issue: watchdog)

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
- [ ] Development environment configurations (env files, debug setup)
- [ ] Linting / Prettier integration for Processing container
- [ ] Basic testing (pipeline & storage)
- [ ] Documentation (setup + workflow)
