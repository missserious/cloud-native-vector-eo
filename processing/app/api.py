import logging
import os

from fastapi import FastAPI

from conversion_pipeline import ConversionPipeline
from minio_storage import MinioStorage
from stac_generator import generate_stac_item

logging.basicConfig(level=logging.INFO)

app = FastAPI()

storage: MinioStorage = MinioStorage()
output_dir = os.getenv("OUTPUT_DIR", "data/output")
pipeline: ConversionPipeline = ConversionPipeline(output_dir)

# TODO: RESULT naming
RESULT: dict[str, str] | None = None

# DuckDB Connection global - con = duckdb.connect()


@app.on_event("startup")
def startup():
    global RESULT

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
    # logging.info(RESULT)
    RESULT = data_assets


# TODO: signed URLs
@app.get("/results")
def get_results() -> dict[str, str]:
    return RESULT


# New Endpoint - GeoParquet Query → JSON
# @app.get("/features")
# def get_features():
#     parquet_path = RESULT["parquet"]

#     result = con.execute(f"""
#         SELECT *
#         FROM 's3://{storage.bucket_name}/{parquet_path}'
#         LIMIT 100
#     """).fetchdf()

#     return result.to_dict(orient="records")
