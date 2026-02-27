# src/wrr/landcover_fetcher.py

import numpy as np
import rasterio
import os

def fetch_landcover(bbox: str, landcover_tif: str = "data/landcover.tif"):
    """
    Placeholder landcover fetcher.

    Parameters
    ----------
    bbox : str
        Bounding box "minx,miny,maxx,maxy"
    landcover_tif : str
        Path to store a dummy landcover GeoTIFF

    Returns
    -------
    landcover_array : np.ndarray
        Array of landcover classes
    transform : affine.Affine
        Dummy affine transform
    """
    print(f"Fetching landcover for bbox: {bbox} (placeholder)")

    os.makedirs("data", exist_ok=True)

    # create a small 50x50 dummy raster with integer landcover classes 1–5
    width, height = 50, 50
    landcover_array = np.random.randint(1, 6, (height, width)).astype("int16")
    transform = rasterio.transform.from_origin(0, height, 1, 1)  # dummy

    with rasterio.open(
        landcover_tif,
        "w",
        driver="GTiff",
        height=height,
        width=width,
        count=1,
        dtype="int16",
        crs="EPSG:25832",
        transform=transform
    ) as dst:
        dst.write(landcover_array, 1)

    print(f"   ✓ Placeholder landcover saved at {landcover_tif}")
    return landcover_array, transform
