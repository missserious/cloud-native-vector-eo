# Base MinIO Image
FROM quay.io/minio/minio:latest

# TODO: Save credentials in a .env file instead of hardcoding for security
ENV MINIO_ROOT_USER=minioadmin
ENV MINIO_ROOT_PASSWORD=minioadmin

# Optional: Docker volume declaration (not strictly needed, using host mount)
# Advantages:
# You can see the files directly in Finder, Explorer, or the terminal
# Backup is very easy: just copy or archive the folder
# Other containers or processes can also use the folder
VOLUME ["/data"]

# Start MinIO server
CMD ["server", "/data", "--console-address", ":9001"]