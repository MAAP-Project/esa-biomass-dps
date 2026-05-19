#!/usr/bin/env python3
"""
Search the ESA STAC for BIOMASS L1B granules based on chosen inputs,
flatten the granules, and save them as a COG.

If you're using NASA MAAP, you'll need to obtain a long-term token from ESA.
For instructions on obtaining a long-term token, see:
https://docs.maap-project.org/en/latest/science/ESA_BIOMASS/ESA_BIOMASS_Data_Access.html#Getting-the-ESA-MAAP-Long-Lasting-Token

Run the following to add your long-term ESA token using maap-py:

OFFLINE_TOKEN = maap.secrets.add_secret("OFFLINE_TOKEN", "INSERT YOUR LONG-TERM ESA TOKEN HERE")

The code below will then retrieve a short-lived token using the public
ESA MAAP client credentials.
If you're running on ESA MAAP, comment out the token retrieval path.
"""

import argparse
import os

import odc.stac
import pystac_client
import rasterio
import requests
import rioxarray  # noqa: F401 - activates the rio accessor on xarray objects
from maap.maap import MAAP
from odc.geo import GeoBox
from pyproj import Transformer

STAC_URL = "https://catalog.maap.eo.esa.int/catalogue/"
TOKEN_URL = "https://iam.maap.eo.esa.int/realms/esa-maap/protocol/openid-connect/token"
CLIENT_ID = "offline-token"
CLIENT_SECRET = "p1eL7uonXs6MDxtGbgKdPVRAmnGxHpVE"
COLLECTION = "BiomassLevel1b"
PRODUCT_FILTER = (
    "(productType='S2_DGM__1S' OR productType='S1_DGM__1S' OR productType='S3_DGM__1S')"
)


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="ESA BIOMASS DPS Job")
    parser.add_argument(
        "--bbox",
        type=str,
        required=True,
        help="Bounding box as min_lon,min_lat,max_lon,max_lat",
    )
    parser.add_argument("--crs", type=str, required=True, help="CRS of bbox and output")
    parser.add_argument(
        "--datetime",
        type=str,
        required=True,
        help="Datetime range e.g. 2026-01-01/2026-02-02",
    )
    parser.add_argument(
        "--resolution",
        type=float,
        default=0.01,
        help="Output resolution in CRS units, e.g. 0.1",
    )
    parser.add_argument(
        "--output-path",
        type=str,
        required=True,
        help="Path to the output COG file",
    )
    return parser.parse_args(argv)


def get_token(maap_client=None):
    """Exchange the long-lived offline token for a short-lived access token."""
    maap_client = maap_client or MAAP()

    offline_token = maap_client.secrets.get_secret("OFFLINE_TOKEN")

    if not offline_token:
        raise ValueError("Missing OFFLINE_TOKEN in credentials file")

    response = requests.post(
        TOKEN_URL,
        data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "grant_type": "refresh_token",
            "refresh_token": offline_token,
            "scope": "offline_access openid",
        },
    )
    response.raise_for_status()

    access_token = response.json().get("access_token")
    if not access_token:
        raise RuntimeError("Failed to retrieve access token from IAM response")

    return access_token


def search_items(bbox, bbox_crs, datetime_range):
    transformer = Transformer.from_crs(bbox_crs, "epsg:4326", always_xy=True)
    bbox_4326 = list(transformer.transform_bounds(*bbox))

    client = pystac_client.Client.open(STAC_URL)
    search = client.search(
        collections=[COLLECTION],
        bbox=bbox_4326,
        datetime=datetime_range,
        filter=PRODUCT_FILTER,
        method="GET",
    )

    item_list = []
    for item in search.item_collection():
        item.properties.pop("proj:code", None)
        item.stac_extensions = [
            extension
            for extension in item.stac_extensions
            if "projection" not in extension
        ]
        item_list.append(item)

    return item_list


def load_latest_data(item_list, bbox, bbox_crs, resolution, token):
    cfg = {
        COLLECTION: {
            "assets": {
                "enclosure_tiff": {
                    "data_type": "float32",
                    "nodata": float("nan"),
                }
            },
            "*": {"warnings": "ignore"},
        }
    }

    with rasterio.Env(GDAL_HTTP_HEADERS=f"Authorization: Bearer {token}"):
        stack = odc.stac.load(
            item_list,
            bands=["enclosure_tiff"],
            stac_cfg=cfg,
            chunks={"x": 512, "y": 512},
            geobox=GeoBox.from_bbox(
                bbox=bbox, crs=bbox_crs, resolution=resolution, tight=True
            ),
        ).sortby("time")

    return stack["enclosure_tiff"].ffill(dim="time").isel(time=-1)


def run(bbox, crs, datetime_range, resolution, output_path):
    token = get_token()
    item_list = search_items(bbox=bbox, bbox_crs=crs, datetime_range=datetime_range)

    output_dir = os.path.dirname(output_path) or "."
    os.makedirs(output_dir, exist_ok=True)

    data = load_latest_data(
        item_list=item_list,
        bbox=bbox,
        bbox_crs=crs,
        resolution=resolution,
        token=token,
    )
    data.rio.to_raster(output_path, driver="COG")


def main(argv=None):
    args = parse_args(argv)
    bbox = tuple(float(value) for value in args.bbox.split(","))
    run(
        bbox=bbox,
        crs=args.crs,
        datetime_range=args.datetime,
        resolution=args.resolution,
        output_path=args.output_path,
    )


if __name__ == "__main__":
    main()
