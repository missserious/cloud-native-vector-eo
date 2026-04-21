import logging
import os
import json

from fastapi import FastAPI

# CORS issue solved
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

import duckdb

from conversion_pipeline import ConversionPipeline
from minio_storage import MinioStorage
from stac_generator import generate_stac_item

from typing import Dict, Any

logging.basicConfig(level=logging.INFO)

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # DEV
        "http://localhost",  # PROD
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

storage: MinioStorage = MinioStorage()
output_dir = os.getenv("OUTPUT_DIR", "data/output")
pipeline: ConversionPipeline = ConversionPipeline(output_dir)


@app.on_event("startup")
def startup():

    storage.create_bucket()

    #########################################################################################
    # NOTE: Test input file (hardcoded for MVP / local development)
    # berlin_correct.geojson
    # braila_correct.geojson
    # countries_naturalEarth.geojson
    input_file_path: str = os.path.join(
        os.getenv("INPUT_DIR", "data/input"), "ndvi-change-vector-result-example.json"
    )
    #########################################################################################

    # TODO: TypeDict
    data_assets: dict[str, str] = pipeline.run(input_file_path)

    storage.upload_all_assets(data_assets)
    stac_file = generate_stac_item(data_assets)
    storage.upload_stac_file(stac_file)

    logging.info("API IS RUNNING")
    # logging.info(data_assets)
    # logging.info(stac_file)


# TODO: Define Single Source of Truth for STAC metadata
# Options: local filesystem (current) vs MinIO object storage
# Affects: /stac, /stats, /features endpoints

# -------------------------------------------
# STAC Endpoint: http://localhost:8000/stac
# -------------------------------------------
@app.get("/stac")
def stac() -> Dict[str, Any]:

    # load STAC
    stac = load_stac()

    pmtiles_key = os.path.basename(stac["assets"]["vector-tiles"]["href"])

    # URL Transformation: Browser points to FastAPI, NOT MinIO
    stac["assets"]["vector-tiles"][
        "href"
    ] = f"http://localhost:8000/tiles/{pmtiles_key}"

    return stac


# -------------------------------------------
# TILES Signed-URL-Redirect Gateway ENDPOINT
# -------------------------------------------
@app.get("/tiles/{key:path}")
def get_tiles(key: str):
    signed_url = storage.get_signed_url(key)
    return RedirectResponse(url=signed_url)


# --------------------------
# STATISTIC EXAMPLE ENPOINT
# --------------------------
@app.get("/stats")
def stats():

    # load STAC
    stac = load_stac()

    # GeoParquet from STAC
    parquet_key = os.path.basename(stac["assets"]["vector-data"]["href"])

    # IMPORTANG: use signed URL instead of raw MinIO URL
    parquet_url = storage.get_signed_url(parquet_key)

    con = duckdb.connect()

    result = con.execute(
        """
        SELECT
            COUNT(*) AS feature_count,
            SUM(population) AS total_population,
            AVG(Intensity) AS avg_intensity
        FROM read_parquet(?)
    """,
        [parquet_url],
    ).fetchone()

    return {
        "feature_count": result[0],
        "total_population": result[1],
        "avg_intensity": result[2],
    }


# ----------------
# FEATURE ENPOINT
# ----------------
@app.get("/features/{uuid}")
def get_feature(uuid: str):

    # load STAC
    stac = load_stac()

    # get parquet
    parquet_key = os.path.basename(stac["assets"]["vector-data"]["href"])

    parquet_url = storage.get_signed_url(parquet_key)

    con = duckdb.connect()

    # get all columns
    columns_info = con.execute(
        """
        DESCRIBE SELECT * FROM read_parquet(?)
    """,
        [parquet_url],
    ).fetchall()

    # filter out geometry
    columns = [col[0] for col in columns_info if col[0] != "geometry"]

    # dynamic query: quoten columns!!
    safe_columns = [f'"{col}"' for col in columns]

    query = f"""
        SELECT {", ".join(safe_columns)}
        FROM read_parquet(?)
        WHERE uuid = ?
        LIMIT 1
    """
    result = con.execute(query, [parquet_url, uuid]).fetchone()

    if not result:
        return {"error": "Feature not found"}

    # change to dictionary
    feature = dict(zip(columns, result))

    return feature


# helper
def load_stac() -> dict:
    path = os.path.join(output_dir, "stac_item.json")

    with open(path, "r") as f:
        return json.load(f)
