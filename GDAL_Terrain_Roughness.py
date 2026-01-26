from __future__ import annotations

import argparse
import os
import requests
import numpy as np
import rasterio
from rasterio.mask import mask
from shapely.geometry import box, mapping
from osgeo import gdal


# AOI Class

class AOI:
    def __init__(self, bbox):
        self.west, self.south, self.east, self.north = bbox
        self._validate_bbox()
        self.geometry = mapping(box(self.west, self.south, self.east, self.north))

    def _validate_bbox(self):
        if self.west >= self.east or self.south >= self.north:
            raise ValueError("Invalid bounding box ordering (W,S,E,N).")

    def __repr__(self):
        return f"AOI(W={self.west}, S={self.south}, E={self.east}, N={self.north})"


# DEM Fetcher Class

class DEMFetcher:
    def __init__(self, filepath: str, aoi: AOI, demtype: str, api_key: str):
        self.filepath = filepath
        self.aoi = aoi
        self.demtype = demtype
        self.api_key = api_key

    def download(self) -> None:
        print(f"Downloading DEM ({self.demtype}) for AOI {self.aoi}...")
        print("API Key:", self.api_key)

        url = "https://portal.opentopography.org/API/globaldem"
        params = {
            "demtype": self.demtype,
            "west": self.aoi.west,
            "south": self.aoi.south,
            "east": self.aoi.east,
            "north": self.aoi.north,
            "outputFormat": "GTiff",
            "API_Key": self.api_key
        }

        response = requests.get(url, params=params)
        if response.status_code != 200:
            raise RuntimeError(f"OpenTopography download failed: {response.text}")

        with open(self.filepath, "wb") as f:
            f.write(response.content)

        print("DEM downloaded successfully.")

    def clip(self) -> None:
        if not os.path.exists(self.filepath):
            raise FileNotFoundError("Raster file not found for clipping.")

        with rasterio.open(self.filepath) as src:
            out_image, out_transform = mask(src, [self.aoi.geometry], crop=True)
            nodata = src.nodata
            out_meta = src.meta.copy()

            out_meta.update({
                "driver": "GTiff",
                "height": out_image.shape[1],
                "width": out_image.shape[2],
                "transform": out_transform,
                "nodata": nodata
            })

        with rasterio.open(self.filepath, "w", **out_meta) as dst:
            dst.write(out_image)

        print("DEM clipped and saved.")

    def reproject(self, target_crs: str = "EPSG:32632") -> None:
        if not os.path.exists(self.filepath):
            raise FileNotFoundError("DEM file not found. Run clip() first.")

        projected_path = self.filepath.replace(".tif", "_projected.tif")

        ds = gdal.Open(self.filepath)
        if ds is None:
            raise RuntimeError("Failed to open DEM for reprojection.")

        gdal.Warp(
            projected_path,
            ds,
            dstSRS=target_crs,
            resampleAlg=gdal.GRA_Bilinear,
            format="GTiff"
        )

        self.filepath = projected_path
        print(f"Reprojected DEM saved to {self.filepath}")


# Roughness Calculation

def compute_roughness(dem_path: str, out_path: str, window: int = 3) -> None:
    if window % 2 == 0:
        raise ValueError("Window must be odd (3, 5, 7, ...).")

    with rasterio.open(dem_path) as src:
        dem = src.read(1)
        profile = src.profile

    pad = window // 2
    padded = np.pad(dem, pad, mode="edge")

    roughness = np.zeros_like(dem, dtype=np.float32)

    for i in range(dem.shape[0]):
        for j in range(dem.shape[1]):
            window_data = padded[i:i + window, j:j + window]
            roughness[i, j] = window_data.max() - window_data.min()

    profile.update(dtype=rasterio.float32)

    with rasterio.open(out_path, "w", **profile) as dst:
        dst.write(roughness, 1)

    print(f"Roughness computed and saved to {out_path}")


# CLI Utilities

def parse_bbox(bbox_str):
    try:
        w, s, e, n = map(float, bbox_str.split(","))
    except ValueError:
        raise argparse.ArgumentTypeError("BBox must be four floats: W,S,E,N")

    if w >= e or s >= n:
        raise argparse.ArgumentTypeError("Invalid bbox ordering.")

    return w, s, e, n


# Main

def main():
    parser = argparse.ArgumentParser(description="Terrain Assessment Pipeline")

    parser.add_argument("--bbox", required=True, type=parse_bbox, help="Bounding box as W,S,E,N in WGS84")
    parser.add_argument("--demtype", required=True, help="DEM type (e.g. NASADEM)")
    parser.add_argument("--api-key", required=True, help="OpenTopography API key")
    parser.add_argument("--outdir", default="results", help="Output directory")
    parser.add_argument("--roughness", action="store_true", help="Compute terrain roughness")

    args = parser.parse_args()
    os.makedirs(args.outdir, exist_ok=True)

    aoi = AOI(args.bbox)

    dem = DEMFetcher(
        filepath=os.path.join(args.outdir, "dem.tif"),
        aoi=aoi,
        demtype=args.demtype,
        api_key=args.api_key
    )

    dem.download()
    dem.clip()
    dem.reproject("EPSG:32632")

    if args.roughness:
        roughness_path = os.path.join(args.outdir, "roughness.tif")
        compute_roughness(dem.filepath, roughness_path, window=3)

    print("Pipeline completed successfully.")


if __name__ == "__main__":
    main()
