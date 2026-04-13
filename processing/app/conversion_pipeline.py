# from typing import TypedDict
import geopandas as gpd
from shapely.validation import make_valid
import subprocess
import os

class ConversionPipeline:

    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)


    # TODO: Structured Return Type/Structured Data Return (via dict)
    def run(self, input_file_path: str) -> dict[str, str]:
        # call _load_and_validate, geojson_to_parquet_geopandas, geojson_to_parquet_ogr2ogr, geojson_to_pmtiles
        gdf = self._load_and_validate(input_file_path)

        parquet_gpd = self.geojson_to_parquet_geopandas(gdf)
        parquet_ogr = self.geojson_to_parquet_ogr2ogr(input_file_path)
        pmtiles = self.geojson_to_pmtiles(input_file_path)

        return {
            "parquet_gpd": parquet_gpd,
            "parquet_ogr": parquet_ogr,
            "pmtiles": pmtiles
        }

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
        output_path: str = os.path.join(
            self.output_dir, 
            "parquet_geopandas.geoparquet"
            )
        # best practise 
        if os.path.exists(output_path):
            os.remove(output_path)

        try:
            gdf.to_parquet(
                output_path,
                engine="pyarrow",
                index=False
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

        output_path = os.path.join(
            self.output_dir,
            "parquet_ogr2ogr.geoparquet"
        )
        # best practise 
        if os.path.exists(output_path):
            os.remove(output_path)

        cmd = [
            "ogr2ogr",
            "-f", "Parquet",
            output_path,
            input_file_path,
            "-lco", "GEOMETRY_NAME=geometry",
            "-lco", "FID=id",
            "-lco", "COMPRESSION=SNAPPY"
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )

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

        output_mbtiles_path: str = os.path.join(
            self.output_dir,
            "tiles.mbtiles"
        )

        output_pmtiles_path: str = os.path.join(
            self.output_dir,
            "tiles.pmtiles"
        )

        # best practice cleanup
        for path in [output_mbtiles_path, output_pmtiles_path]:
            if os.path.exists(path):
                os.remove(path)

        try:
            subprocess.run([
                "tippecanoe",
                "-o", output_mbtiles_path,
                "-Z", "0", "-z", "14",
                "--drop-densest-as-needed",
                "--extend-zooms-if-still-dropping",
                input_file_path
            ], check=True, capture_output=True, text=True)

            subprocess.run([
                "pmtiles", "convert",
                output_mbtiles_path,
                output_pmtiles_path
            ], check=True, capture_output=True, text=True)

        except subprocess.CalledProcessError as e:
            raise RuntimeError(
                "PMTILES PIPELINE FAILED\n"
                f" → Input: {input_file_path}\n"
                f" → MBTiles: {output_mbtiles_path}\n"
                f" → Error: {e.stderr if hasattr(e, 'stderr') else str(e)}\n"
            ) from e

        except Exception as e:
            raise RuntimeError(
                "UNEXPECTED ERROR IN PMTILES PIPELINE\n"
                f" → Reason: {str(e)}"
            ) from e

        return output_pmtiles_path
