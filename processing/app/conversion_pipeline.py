# from typing import TypedDict
import os

# import logging

import uuid
import json

# GDAL configuration (must be set before importing geopandas)
os.environ["OGR_GEOJSON_MAX_OBJ_SIZE"] = os.getenv("OGR_GEOJSON_MAX_OBJ_SIZE", "0")

import subprocess

import geopandas as gpd
from shapely.validation import make_valid


class ConversionPipeline:

    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    # TODO: Structured Return Type/Structured Data Return (via dict)
    def run(self, input_file_path: str) -> dict[str, str]:
        # INCLUDE METHOD: to add id in geojson dataset
        geojson_with_ids = self.add_feature_ids_to_geojson(
            input_file_path, "data/cache_input_file_uuid.geojson"
        )
        # call _load_and_validate, geojson_to_parquet_geopandas, geojson_to_parquet_ogr2ogr, geojson_to_pmtiles
        gdf = self._load_and_validate(geojson_with_ids)

        parquet_gpd = self.geojson_to_parquet_geopandas(gdf)
        parquet_ogr = self.geojson_to_parquet_ogr2ogr(geojson_with_ids)
        pmtiles = self.geojson_to_pmtiles(geojson_with_ids)

        return {
            "parquet_gpd": parquet_gpd,
            "parquet_ogr": parquet_ogr,
            "pmtiles": pmtiles,
        }

    # -------------------------
    # Include uuid in geojson
    # -------------------------
    def add_feature_ids_to_geojson(self, input_file_path: str, cache_path: str) -> str:

        with open(input_file_path) as f:
            data = json.load(f)

        for ftr in data["features"]:
            ftr["properties"]["uuid"] = str(uuid.uuid4())
        with open(cache_path, "w") as f:
            json.dump(data, f)

        return cache_path

    # ---------------------
    # Load & Validate: Exceptions only Pipeline
    # File exists, File has CRS, repair File if necessary/possible, File is valid geojson
    # ---------------------
    def _load_and_validate(self, input_file_path: str) -> gpd.GeoDataFrame:

        if not os.path.exists(input_file_path):
            raise RuntimeError(
                f"INPUT FILE NOT FOUND\n"
                f"  ├─ Path: {input_file_path}\n"
                f"  → Pipeline stopped\n"
            )

        try:
            gdf = gpd.read_file(input_file_path)
        except Exception as e:
            raise RuntimeError(
                f" INVALID GEO DATA\n"
                f" → File: {input_file_path}\n"
                f" → Reason: cannot be parsed (GDAL/GeoPandas)\n"
                f" → Error: {str(e)}\n"
                f"  → Pipeline stopped\n"
            ) from e

        if gdf.crs is None:
            raise RuntimeError(
                f" MISSING CRS\n"
                f" → File: {input_file_path}\n"
                f" → Fix: define source CRS before processing\n"
                f"  → Pipeline stopped\n"
            )

        # normalize
        gdf = gdf.to_crs("EPSG:4326")
        gdf["geometry"] = gdf["geometry"].apply(make_valid)

        return gdf

    # ---------------------
    # Parquet: geopandas
    # ---------------------
    def geojson_to_parquet_geopandas(self, gdf: gpd.GeoDataFrame) -> str:
        output_path: str = os.path.join(self.output_dir, "parquet_geopandas.geoparquet")
        # best practise
        if os.path.exists(output_path):
            os.remove(output_path)

        try:
            compression = os.getenv("GEOPANDAS_PARQUET_COMPRESSION", "snappy")

            gdf.to_parquet(
                output_path,
                engine="pyarrow",
                index=False,
                compression=compression,
            )

        except Exception as e:
            raise RuntimeError(
                "PARQUET EXPORT FAILED (GeoPandas)\n"
                f" → Output: {output_path}\n"
                f" → Reason: {str(e)}\n"
            ) from e

        return output_path

    # -----------------------
    # Parquet: GDAL / ogr2ogr
    # -----------------------
    def geojson_to_parquet_ogr2ogr(self, input_file_path: str) -> str:

        output_path = os.path.join(self.output_dir, "parquet_ogr2ogr.geoparquet")
        # best practise
        if os.path.exists(output_path):
            os.remove(output_path)

        compression = os.getenv("OGR_PARQUET_COMPRESSION", "SNAPPY")

        cmd = [
            "ogr2ogr",
            "-f",
            "Parquet",
            output_path,
            input_file_path,
            "-lco",
            "GEOMETRY_NAME=geometry",
            "-lco",
            "FID=id",
            "-lco",
            f"COMPRESSION={compression}",
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            raise RuntimeError(
                "OGR2OGR EXPORT FAILED\n"
                f" → Output: {output_path}\n"
                f" → STDERR: {result.stderr}\n"
            )

        return output_path

    # ---------------------
    # Tiles
    # ---------------------
    def geojson_to_pmtiles(self, input_file_path: str) -> str:

        output_mbtiles_path: str = os.path.join(self.output_dir, "tiles.mbtiles")
        output_pmtiles_path: str = os.path.join(self.output_dir, "tiles.pmtiles")

        # best practice cleanup
        for path in [output_mbtiles_path, output_pmtiles_path]:
            if os.path.exists(path):
                os.remove(path)

        try:
            cmd = [
                "tippecanoe",
                "-o",
                output_mbtiles_path,
                "-l",
                "data",  # LAYER NAME FOR FRONTEND
                "-Z",
                os.getenv("TILE_ZOOM_MIN", "0"),
                "-z",
                os.getenv("TILE_ZOOM_MAX", "10"),
            ]
            if os.getenv("TIPPECANOE_READ_PARALLEL", "true") == "true":
                cmd.append("--read-parallel")

            if os.getenv("TIPPECANOE_DROP_DENSE", "true") == "true":
                cmd.append("--drop-densest-as-needed")

            cmd.append(input_file_path)

            # logging.info(f"TIPPECANOE CMD: {cmd}")
            subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True,
            )

            subprocess.run(
                ["pmtiles", "convert", output_mbtiles_path, output_pmtiles_path],
                check=True,
                capture_output=True,
                text=True,
            )

        except subprocess.CalledProcessError as e:
            raise RuntimeError(
                "PMTILES PIPELINE FAILED\n"
                f" → Input: {input_file_path}\n"
                f" → MBTiles: {output_mbtiles_path}\n"
                f" → Error: {e.stderr if hasattr(e, 'stderr') else str(e)}\n"
            ) from e

        except Exception as e:
            raise RuntimeError(
                "UNEXPECTED ERROR IN PMTILES PIPELINE\n" f" → Reason: {str(e)}"
            ) from e

        return output_pmtiles_path
