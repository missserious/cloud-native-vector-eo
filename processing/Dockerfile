# GDAL Base Image
FROM ghcr.io/osgeo/gdal:ubuntu-full-3.10.1

# Install system tools and pmtiles CLI
# TODO: Optional: Fix package versions for reproducibility: e.g., python3=3.12.2-1ubuntu1, tippecanoe=2.40.1-1
RUN apt-get update && apt-get install -y \
        python3 \
        python3-pip \
        tippecanoe \
        curl \
        tar \
    && curl -L -o /tmp/pmtiles.tar.gz \
        https://github.com/protomaps/go-pmtiles/releases/download/v1.30.1/go-pmtiles_1.30.1_Linux_x86_64.tar.gz \
    && tar -xzf /tmp/pmtiles.tar.gz -C /usr/local/bin pmtiles \
    && chmod +x /usr/local/bin/pmtiles \
    && rm -rf /tmp/pmtiles.tar.gz \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install python dependencies from requirements.txt
COPY requirements.txt /app/
RUN pip3 install --no-cache-dir --break-system-packages -r requirements.txt

COPY . /app/

# TODO: Optional: .dockerignore - see comment/issue in file

# PROD-SERVER
# CMD ["python3", "app/main.py"]

# port 8000
EXPOSE 8000

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]


