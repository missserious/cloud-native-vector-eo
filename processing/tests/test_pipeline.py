import os
from app.conversion_pipeline import ConversionPipeline

# TODO: more tests: 
# Pipeline Tests (Core Processing), STAC Metadata Tests, Storage / MinIO Tests, API Tests...
def test_pipeline_runs():
    output_dir = "data/output"
    pipeline = ConversionPipeline(output_dir)

    input_file = os.path.join(
        os.getenv("INPUT_DIR", "data/input"),
        "ndvi-change-vector-result-example.json"
    )

    result = pipeline.run(input_file)

    assert isinstance(result, dict)
    assert "parquet_ogr" in result
    assert "parquet_gpd" in result
    assert "pmtiles" in result