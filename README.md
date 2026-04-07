# [Cloud-Native Architecture for Vector EO Products](#)

## processing container

sudo docker build -t processing-mvp .
sudo docker run --rm -v $(pwd)/output:/app/output -u $(id -u):$(id -g) processing-mvp

## storage container

- Map container port 9000 (S3 API) to host port 9000
- Map container port 9001 (WebUI) to host port 9001

docker build -t minio-storage-mvp .
docker run -d \
 --name minio \
 -p 9000:9000 \
-p 9001:9001 \
-v $(pwd)/minio_data:/data \
 minio-storage-mvp

TODO: Docker-in-Docker Watcher
B) Docker-in-Docker Watcher (leichtgewichtig)
Ein separates Python-Script oder Shell-Watcher läuft nur auf Host, um docker run zu triggern
Vorteil: Container enthält alles → Host muss nur Docker haben, sonst nichts
