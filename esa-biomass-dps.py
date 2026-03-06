#!/usr/bin/env python3
"""
esa-biomass-dps.py

"""
# conda install gdal odc-stac

import requests
from pathlib import Path
import pystac_client
import rasterio
import odc.stac
from odc.geo import GeoBox

bbox = (55, 64, 61, 67)
bbox_crs = "wgs84"
resolution = 30
datetime = "2026-01-01/2026-02-02"


# Search the ESA STAC for BiomassLevel1B items that match the spatial and temporal parameters
client = pystac_client.Client.open("https://catalog.maap.eo.esa.int/catalogue/")
search = client.search(
    collections=["BiomassLevel1b"],
    bbox=bbox,
    datetime=datetime,
    filter="productType='S2_DGM__1S'",
    method="GET"
)
items = search.item_collection()

"""
Next, you'll need to obtain a token
For instructions on obtaining a long-term token, see: https://docs.maap-project.org/en/latest/science/ESA_BIOMASS/ESA_BIOMASS_Data_Access.html#Getting-the-ESA-MAAP-Long-Lasting-Token

Then, create a credentials.txt file in your home directory, and edit and paste the following into the credentials.txt file:
CLIENT_ID=offline-token
CLIENT_SECRET=p1eL7uonXs6MDxtGbgKdPVRAmnGxHpVE
OFFLINE_TOKEN=your_esamaap_offline_token_here

Now the following code will retrieve a short-lived token
"""

# Retrieve token
CREDENTIALS_FILE = (Path.home() / "credentials.txt").resolve()

def load_credentials(file_path=CREDENTIALS_FILE):
    """Read key-value pairs from a credentials file into a dictionary."""
    creds = {}
    if not file_path.exists():
        raise FileNotFoundError(f"Credentials file not found: {file_path}")
    with open(file_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, value = line.split("=", 1)
            creds[key.strip()] = value.strip()
    return creds


# --- ESA MAAP API ---

def get_token():
    """Use OFFLINE_TOKEN to fetch a short-lived access token."""
    creds = load_credentials()

    OFFLINE_TOKEN = creds.get("OFFLINE_TOKEN")
    CLIENT_ID = creds.get("CLIENT_ID")
    CLIENT_SECRET = creds.get("CLIENT_SECRET")

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

# 
with rasterio.Env(GDAL_HTTP_HEADERS=f"Authorization: Bearer {token}"):
    stack = odc.stac.load(
         items,
         bands=["enclosure_tiff"],
         #chunks={"x": 512, "y": 512},  # TODO: figure out the right settings for this
         geobox=GeoBox.from_bbox(bbox=bbox, crs=bbox_crs, resolution=resolution, tight=True),
     ).sortby("time")