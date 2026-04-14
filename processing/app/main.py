from conversion_pipeline import ConversionPipeline
from minio_storage import MinioStorage

from dotenv import load_dotenv
load_dotenv() 

# TODO: Type Checker (mypy / pyright), Prettier (Code Formatter), Linter (ruff / flake8)
# TODO: Typisieren 
# TODO: logging.error instead of print - import logging - logging.info
# TODO: ENV validation,
def main() -> None:
    # Entry Point 
    #
    # Flow:
    # Storage Init → Bucket Setup → Pipeline Execution → Output Validation → Conditional Upload
    #
    # Rules:
    # - No upload if any pipeline step fails
    # - No upload if any expected output file is missing
    # - Fail fast on exceptions 

    storage: MinioStorage = MinioStorage()
    storage.create_bucket()

    input_file_path: str = "data/input/ndvi-change-vector-result-example.json"
    # input_file_path: str = "data/input/ndvi-change-vector-result-example_invalid.json"
    # input_file_path: str = "data/input/ndvi-change-vector-result-example_empty.txt"
    pipeline: ConversionPipeline = ConversionPipeline("data/output/")
    # Run pipeline (returns result=output file paths)
    # TODO: TypeDict
    result: dict[str, str] = pipeline.run(input_file_path)

    # TODO: check: result before upload
    if result:
        storage.upload_all_files(result)
    else:
        raise RuntimeError("Pipeline incomplete → upload skipped")

if __name__ == "__main__":
    main()