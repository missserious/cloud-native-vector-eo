from fastapi import FastAPI
from conversion_pipeline import ConversionPipeline
from minio_storage import MinioStorage
import logging
logging.basicConfig(level=logging.INFO)

app = FastAPI()

storage: MinioStorage = MinioStorage()
pipeline: ConversionPipeline = ConversionPipeline("data/output/")

RESULT = None

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
def get_results():
    return RESULT    
