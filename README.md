# esa-biomass-dps 
A MAAP DPS/OGC Application Package that queries the ESA BIOMASS Level 1B collection in ESA STAC for data within a user-defined bounding box and time range, retrieves the granules, and loads the assets using odc stac. The data is optionally forward-filled over time and reduced to the latest available observation, then written as a Cloud Optimized GeoTIFF (COG) in the user-specified CRS and resolution.

## Sample
    algo_id="esa_biomass_dps",
    version="main",
    queue="maap-dps-worker-8gb",
    bbox="55,64,61,67",
    crs="EPSG:4326",
    datetime="2026-01-01/2026-02-02",
    resolution="0.01"
