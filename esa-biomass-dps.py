#!/usr/bin/env python3
"""
esa-biomass-dps.py

Search the ESA STAC for BIOMASS L1B granules based on chosen inputs, flatten the granules, and save them as a COG
"""
# conda install gdal odc-stac

import requests
import pystac_client
import rasterio
import odc.stac
from odc.geo import GeoBox
import rioxarray 
import os
import argparse
from pyproj import Transformer

from maap.maap import MAAP
maap = MAAP()

parser = argparse.ArgumentParser(description="ESA BIOMASS DPS Job")
parser.add_argument("--bbox", type=str, required=True, help="Bounding box as min_lon,min_lat,max_lon,max_lat")
parser.add_argument("--crs", type=str, required=True, help="CRS of bbox and output")
parser.add_argument("--datetime", type=str, required=True, help="Datetime range e.g. 2026-01-01/2026-02-02")
parser.add_argument("--resolution", type=float, default=0.01, help="Output resolution in CRS units, eg. 0.1")
args = parser.parse_args()

# Parse bbox string into tuple of floats
bbox = tuple(float(x) for x in args.bbox.split(","))
bbox_crs = args.crs
datetime = args.datetime
resolution = args.resolution

"""
If you're using NASA MAAP, you'll need to obtain a long-term token from ESA
For instructions on obtaining a long-term token, see: https://docs.maap-project.org/en/latest/science/ESA_BIOMASS/ESA_BIOMASS_Data_Access.html#Getting-the-ESA-MAAP-Long-Lasting-Token

Run the following to add secrets using maap-py:

CLIENT_ID = maap.secrets.add_secret("CLIENT_ID", "offline-token")
CLIENT_SECRET = maap.secrets.add_secret("CLIENT_SECRET", "p1eL7uonXs6MDxtGbgKdPVRAmnGxHpVE")
OFFLINE_TOKEN = maap.secrets.add_secret("OFFLINE_TOKEN", "INSERT YOUR LONG-TERM ESA TOKEN HERE")

The code below will then retrieve a short-lived token
If you're running on ESA MAAP, comment out lines 48-77
"""

def get_token():

    OFFLINE_TOKEN = maap.secrets.get_secret("OFFLINE_TOKEN")
    CLIENT_ID = maap.secrets.get_secret("CLIENT_ID")
    CLIENT_SECRET = maap.secrets.get_secret("CLIENT_SECRET")

    if not all([OFFLINE_TOKEN, CLIENT_ID, CLIENT_SECRET]):
        raise ValueError("Missing OFFLINE_TOKEN, CLIENT_ID, or CLIENT_SECRET in credentials file")

    url = "https://iam.maap.eo.esa.int/realms/esa-maap/protocol/openid-connect/token"
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "refresh_token",
        "refresh_token": OFFLINE_TOKEN,
        "scope": "offline_access openid"
    }

    response = requests.post(url, data=data)
    response.raise_for_status()

    response_json = response.json()
    access_token = response_json.get('access_token')

    if not access_token:
        raise RuntimeError("Failed to retrieve access token from IAM response")

    return access_token

token = get_token()

# Search the ESA STAC for BiomassLevel1B items that match the spatial and temporal parameters
# Note: the CRS must be ESPG:4326 for STAC search, but the final output will be what the user input

transformer = Transformer.from_crs(bbox_crs, "epsg:4326", always_xy=True)
bbox_4326 = list(transformer.transform_bounds(*bbox))

client = pystac_client.Client.open("https://catalog.maap.eo.esa.int/catalogue/")
search = client.search(
    collections=["BiomassLevel1b"],
    bbox=bbox_4326,
    datetime=datetime,
    filter="productType='S2_DGM__1S'",
    method="GET"
)
items = search.item_collection()

# Convert results to a list and remove proj information. This is to ensure odc stac works properly.
item_list = []
for item in items:
    item.properties.pop("proj:code", None)
    item.stac_extensions = [extension for extension in item.stac_extensions if "projection" not in extension]
    item_list.append(item)

os.makedirs("./output", exist_ok=True)

# Retrieve assets, flatten, and save as a COG
cfg = {
    "BiomassLevel1b": {
        "assets": {
            "enclosure_tiff": {
                "data_type": "float32",
                "nodata": float("nan"),
            },
        },
        "*": {"warnings": "ignore"}
    }
}

with rasterio.Env(GDAL_HTTP_HEADERS=f"Authorization: Bearer {token}"): # remove this line if running on ESA MAAP
    stack = odc.stac.load(
        item_list,
        bands=["enclosure_tiff"],
        stac_cfg=cfg,
        chunks={"x": 512, "y": 512},
        geobox=GeoBox.from_bbox(bbox=bbox, crs=bbox_crs, resolution=resolution, tight=True),
    ).sortby("time")

    #stack["enclosure_tiff"].resample(time="ME").first().plot.imshow(col="time")
    #stack["enclosure_tiff"].ffill(dim='time').isel(time=-1).plot.imshow()

    data = stack["enclosure_tiff"].ffill(dim='time').isel(time=-1)
    data.rio.to_raster("./output/biomass.tiff", driver="COG")

