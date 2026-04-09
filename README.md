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
    -v $(pwd)/output:/app/output \
    processing-mvp
```

## TODO'S

- [ ] Docker Diagram ( e. g. Mermaid/PNG )

- Processing Container
  - [x] A
  - [ ] B
- Storage Container
  - [x] A
  - [ ] B
- Frontend Container
  - [x] A
  - [ ] B
