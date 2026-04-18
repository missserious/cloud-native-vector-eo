import json
import os
import duckdb


def generate_stac_item(data_assets: dict[str, str]) -> str:
    """
    Generates a minimal STAC Item from pipeline outputs using DuckDB.
    """

    con = duckdb.connect()
    con.execute("INSTALL spatial")
    con.execute("LOAD spatial")

    endpoint = os.getenv("ENDPOINT", "http://localhost:9000")
    bucket = os.getenv("BUCKET_NAME", "geo-bucket")
    base_url = f"{endpoint}/{bucket}"

    parquet_path = data_assets["parquet_ogr"]

    # ----------------------------
    # DuckDB ANALYTICS
    # ----------------------------

    # Feature count
    feature_count = con.execute(f"""
        SELECT COUNT(*) 
        FROM read_parquet('{parquet_path}')
    """).fetchone()[0]

    # BBOX (expects geometry column)
    bounds = con.execute(f"""
        SELECT
            MIN(ST_XMin(geometry)) AS minx,
            MIN(ST_YMin(geometry)) AS miny,
            MAX(ST_XMax(geometry)) AS maxx,
            MAX(ST_YMax(geometry)) AS maxy
            FROM read_parquet('{parquet_path}')
    """).fetchone()

    bbox = [
        float(bounds[0]),
        float(bounds[1]),
        float(bounds[2]),
        float(bounds[3])
    ]

    # Columns
    columns = con.execute(f"""
        DESCRIBE SELECT * FROM read_parquet('{parquet_path}')
    """).fetchdf()

    column_names = columns["column_name"].tolist()

    # ----------------------------
    # STAC ITEM
    # ----------------------------

    # TODO: add STAC render extension when styling is needed
    # TODO: add STAC classification extension when classes exist
    stac = {
        "type": "Feature",
        "stac_version": "1.0.0",        # "id": "flood-severity-2026-03-08-aoi-001",
        "id": "test-item",
        "bbox": bbox,
        "properties": {
            # "datetime": "...",
            # "title": "...",
            "columns": column_names,
            "feature_count": feature_count
        },

        "assets": {
            "vector-data": {
                "href": f"{base_url}/{os.path.basename(parquet_path)}",
                "type": "application/vnd.apache.parquet",
                "roles": ["data"]
            },
            "vector-tiles": {
                "href": f"{base_url}/{os.path.basename(data_assets['pmtiles'])}",
                "type": "application/vnd.pmtiles",
                "roles": ["visual"]
            }
        }
    }

    # ----------------------------
    # WRITE FILE
    # ----------------------------

    output_path = "data/output/stac_item.json"

    with open(output_path, "w") as f:
        json.dump(stac, f, indent=2)

    print("STAC file created:", output_path)

    return output_path