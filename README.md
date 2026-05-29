# esa-biomass-dps

A MAAP DPS/OGC Application Package that queries the ESA BIOMASS Level 1B collection in ESA STAC for data within a user-defined bounding box and time range, retrieves the granules, and loads the assets using odc-stac. The data is optionally forward-filled over time and reduced to the latest available observation, then written as a Cloud Optimized GeoTIFF (COG) in the user-specified CRS and resolution.

## Runtime layout

- `environment.yml` is the canonical dependency manifest.
- `build.sh` creates or updates the `esa_biomass_dps` conda environment from `environment.yml`.
- `run.sh` is the MAAP/DPS runtime wrapper and invokes `run.py`.
- `run.sh` currently hard-codes the output path to `output/biomass.tif` and passes it to Python via `--output-path`.

## CLI arguments

`run.py` accepts:

- `--bbox`: bounding box as `min_lon,min_lat,max_lon,max_lat`
- `--crs`: CRS of the bbox and output raster
- `--datetime`: datetime range such as `2026-01-01/2026-02-02`
- `--resolution`: output resolution in CRS units
- `--output-path`: destination path for the output COG

Example:

```bash
conda run -n esa_biomass_dps python run.py \
  --bbox "55,64,61,67" \
  --crs "EPSG:4326" \
  --datetime "2026-01-01/2026-02-02" \
  --resolution 0.01 \
  --output-path ./output/biomass.tif
```

## Sample

```python
algo_id = "esa_biomass_dps"
version = "main"
queue = "maap-dps-worker-8gb"
bbox = "55,64,61,67"
crs = "EPSG:4326"
datetime = "2026-01-01/2026-02-02"
resolution = "0.01"
```
