import logging
import os
import json

from fastapi import FastAPI

from conversion_pipeline import ConversionPipeline
from minio_storage import MinioStorage
from stac_generator import generate_stac_item

logging.basicConfig(level=logging.INFO)

app = FastAPI()

# CORS issue solved
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

storage: MinioStorage = MinioStorage()
output_dir = os.getenv("OUTPUT_DIR", "data/output")
pipeline: ConversionPipeline = ConversionPipeline(output_dir)


# DuckDB Connection global - con = duckdb.connect()


@app.on_event("startup")
def startup():

    storage.create_bucket()

    input_file_path: str = os.path.join(
        os.getenv("INPUT_DIR", "data/input"),
        "ndvi-change-vector-result-example.json"
    )

    # TODO: TypeDict
    data_assets: dict[str, str] = pipeline.run(input_file_path)

    storage.upload_all_assets(data_assets)
    stac_file = generate_stac_item(data_assets)
    storage.upload_stac_file(stac_file)

    logging.info("API IS RUNNING")
    # logging.info(data_assets)
    # logging.info(stac_file)


# -------------------------------------------
# STAC Endpoint: http://localhost:8000/stac
# -------------------------------------------
@app.get("/stac")
def get_stac():
    path = os.path.join(output_dir, "stac_item.json")

    with open(path, "r") as f:
        stac = json.load(f)

    pmtiles_key = os.path.basename(
        stac["assets"]["vector-tiles"]["href"]
    )

    # Browser points to FastAPI, NOT MinIO
    stac["assets"]["vector-tiles"]["href"] = (
        f"http://localhost:8000/tiles/{pmtiles_key}"
    )

    return stac


# ---------------------
# TILE PROXY ENDPOINT
# ---------------------
@app.get("/tiles/{key:path}")
def get_tiles(key: str):
    signed_url = storage.get_signed_url(key)
    return RedirectResponse(url=signed_url)