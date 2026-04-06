import subprocess
import os

############################################
## Step 3: Generate vector tiles: mbtiles ##
## Step 4: Convert to PMTiles: pmtiles    ##
############################################

## TODO: simple setup: formatter and linter

# Paths
geojson_path = "data/ndvi-change-vector-result-example.json"
mbtiles_path = "output/tiles.mbtiles"
pmtiles_path = "output/tiles.pmtiles"

# Ensure output folder exists
os.makedirs(os.path.dirname(mbtiles_path), exist_ok=True)

# Delete old MBTiles if they exist
if os.path.exists(mbtiles_path):
    print(f"{mbtiles_path} already exists → will be recreated")
    os.remove(mbtiles_path)

# TODO: Externalize Tippecanoe configuration (e.g., min/max zoom, flags)
# via environment variables or config file to make the processing pipeline
# more flexible and reusable in different environments (dev, batch, cloud)
print(f"Starting tile generation: {geojson_path}")
subprocess.run([
    "tippecanoe",
    "-o", mbtiles_path,
    "-Z", "0", "-z", "14",
    "--drop-densest-as-needed",
    "--extend-zooms-if-still-dropping",
    geojson_path
], check=True)
print(f"MBTiles created: {mbtiles_path}")

# Delete old PMTiles if they exist
if os.path.exists(pmtiles_path):
    print(f"{pmtiles_path} already exists → will be recreated")
    os.remove(pmtiles_path)

# Convert MBTiles → PMTiles
print(f"Converting MBTiles → PMTiles: {pmtiles_path}")
subprocess.run([
    "pmtiles", "convert",
    mbtiles_path,
    pmtiles_path
], check=True)
print(f"PMTiles created: {pmtiles_path}")


# TODO: Ensure files are written to persistent storage