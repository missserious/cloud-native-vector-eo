import subprocess
import os
# minIO 
import boto3
from botocore.client import Config
# conversion
import geopandas as gpd

############################################
## Step 3: Generate vector tiles: mbtiles ##
## Step 4: Convert to PMTiles: pmtiles    ##
############################################

## TODO: simple setup: formatter and linter


def main():
    #####################
    ## Step 1: geojson ##
    #####################
    # Paths
    geojson_path = "data/ndvi-change-vector-result-example.json"

    # 
    mbtiles_path = "output/tiles.mbtiles"
    pmtiles_path = "output/tiles.pmtiles"
    geoparquet_path = "output/parquet.parquet"

    # load geojson
    gdf = gpd.read_file(geojson_path)
    # check CRS sicherstellen
    if gdf.crs is None:
        gdf = gdf.set_crs("EPSG:4326")

    # repair geometry if necessary
    gdf["geometry"] = gdf["geometry"].buffer(0)

    ###################################
    ## Step 2: Convert to GeoParquet ##
    ###################################
    # save GeoParquet 
    # TODO: check if converstion is successfull
    gdf.to_parquet(geoparquet_path, engine="pyarrow", index=False)    
    # end: geoparquet
    
    # Ensure output folder exists
    os.makedirs(os.path.dirname(mbtiles_path), exist_ok=True)

    # Delete old MBTiles if they exist
    if os.path.exists(mbtiles_path):
        print(f"{mbtiles_path} already exists → will be recreated")
        os.remove(mbtiles_path)

    # TODO: Externalize Tippecanoe configuration (e.g., min/max zoom, flags)
    # via environment variables or config file to make the processing pipeline
    # more flexible and reusable in different environments (dev, batch, cloud)
    print(f"Starting tile generation: {geojson_path}")
    subprocess.run([
        "tippecanoe",
        "-o", mbtiles_path,
        "-Z", "0", "-z", "14",
        "--drop-densest-as-needed",
        "--extend-zooms-if-still-dropping",
        geojson_path
    ], check=True)
    print(f"MBTiles created: {mbtiles_path}")

    # Delete old PMTiles if they exist
    if os.path.exists(pmtiles_path):
        print(f"{pmtiles_path} already exists → will be recreated")
        os.remove(pmtiles_path)

    # Convert MBTiles → PMTiles
    print(f"Converting MBTiles → PMTiles: {pmtiles_path}")
    subprocess.run([
        "pmtiles", "convert",
        mbtiles_path,
        pmtiles_path
    ], check=True)
    print(f"PMTiles created: {pmtiles_path}")

    #################################################################
    ## Step 5: TODO:  Upload PMTiles to MinIO (persistent storage) ##
    ## class MinioClient:                                          ##
    #################################################################

    # Documentation: https://www.stackhero.io/en-US/services/MinIO/documentations/Getting-started
    # TODO: .env for security 
    ENDPOINT = "http://minio:9000"
    ACCESS_KEY = "minioadmin"
    SECRET_KEY = "minioadmin"
    USE_SSL = False  # True, if HTTPS

    s3 = boto3.client(
        's3',
        endpoint_url=ENDPOINT,  # Nutze die Variable
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
        config=Config(signature_version='s3v4'),
        region_name='eu-central-1',
        use_ssl=USE_SSL
    )

    BUCKET_NAME = 'pmtiles-bucket'
    # --- list buckets ---
    # 
    response = s3.list_buckets()
    print("Buckets:", [b["Name"] for b in response["Buckets"]])

    # --- create bucket if not exists ---
    existing_buckets = [b["Name"] for b in response["Buckets"]]

    if BUCKET_NAME not in existing_buckets:
        print(f"Creating bucket: {BUCKET_NAME}")
        s3.create_bucket(Bucket=BUCKET_NAME)
    else:
        print(f"Bucket already exists: {BUCKET_NAME}")


        # Upload: Filename, Bucket, Key oarameter-namen: boto3 API.
    s3.upload_file(
        Filename=pmtiles_path,
        Bucket=BUCKET_NAME,
        Key="tiles.pmtiles"
    )

    print(f"Uploaded {pmtiles_path} → s3://{BUCKET_NAME}/{"tiles.pmtiles"}")


if __name__ == "__main__":
    main()