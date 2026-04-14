import logging

from fastapi import FastAPI

from conversion_pipeline import ConversionPipeline
from minio_storage import MinioStorage

logging.basicConfig(level=logging.INFO)

app = FastAPI()

storage: MinioStorage = MinioStorage()
pipeline: ConversionPipeline = ConversionPipeline("data/output/")

RESULT: dict[str, str]

# DuckDB Connection global - con = duckdb.connect()


@app.on_event("startup")
def startup():
    global RESULT

    storage.create_bucket()

    input_file_path: str = "data/input/ndvi-change-vector-result-example.json"

    # Run pipeline (returns result=output file paths)
    # TODO: TypeDict
    result: dict[str, str] = pipeline.run(input_file_path)

    storage.upload_all_files(result)

    RESULT = result
    logging.info("API IS RUNNING")
    logging.info(RESULT)


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
