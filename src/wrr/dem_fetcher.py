"""
Description: Handles downloading and processing of Digital Elevation Models (DEM).
"""

import os
import requests
import rasterio
from rasterio.mask import mask
from osgeo import gdal
from .aoi import AOI

class DEMFetcher:
    def __init__(self, aoi: AOI, output_dir: str = "data/dem"):
        """
        Tools for fetching and processing DEM data.
        """
        self.aoi = aoi
        self.output_dir = output_dir
        self.filepath = os.path.join(output_dir, "dem.tif")
        
        # Ensure the output folder exists
        os.makedirs(output_dir, exist_ok=True)

    def download(self, api_key: str):
        """
        Downloads SRTM GL1 (30m) data from OpenTopography.
        """
        if os.path.exists(self.filepath):
            print(f"File already exists at {self.filepath}. Skipping download.")
            return

        print(f"Requesting DEM for bounds: {self.aoi.bounds}...")
        
        url = "https://portal.opentopography.org/API/globaldem"
        params = {
            "demtype": "SRTMGL1",
            "south": self.aoi.bounds[1],
            "north": self.aoi.bounds[3],
            "west": self.aoi.bounds[0],
            "east": self.aoi.bounds[2],
            "outputFormat": "GTiff",
            "API_Key": api_key
        }
        
        try:
            response = requests.get(url, params=params, stream=True)
            response.raise_for_status()
            
            with open(self.filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"DEM successfully downloaded to {self.filepath}")
            
        except requests.exceptions.RequestException as e:
            print(f"Error downloading DEM: {e}")

    def clip(self):
        """
        Refines the DEM by clipping it exactly to the AOI geometry.
        """
        if not os.path.exists(self.filepath):
            print("DEM file not found. Run download() first.")
            return

        print("Clipping DEM to exact AOI...")
        
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

        with rasterio.open(self.filepath, "w", **out_meta) as dest:
            dest.write(out_image)
            
        print("DEM clipped and saved.")

    def reproject(self, target_crs: str = "EPSG:32632"):
        """
        Reproject DEM to a metric CRS using Bilinear interpolation.
        We DO NOT force a 10m grid, as that creates sinks (pits) that break flow routing.
        """
        if not os.path.exists(self.filepath):
            print("DEM file not found. Run clip() first.")
            return
    
        projected_path = self.filepath.replace(".tif", "_projected.tif")
        print(f"Reprojecting DEM to {target_crs} (Standard Bilinear)...")
    
        ds = gdal.Open(self.filepath)
        if ds is None:
            raise RuntimeError("Failed to open DEM for reprojection.")
    
        # SAFE REPROJECTION:
        # We let GDAL decide the resolution (keeping it close to original ~30m)
        gdal.Warp(
            projected_path,
            ds,
            dstSRS=target_crs,
            resampleAlg=gdal.GRA_Bilinear,
            format="GTiff"
        )
    
        self.filepath = projected_path
        print(f"Reprojected DEM saved to {self.filepath}")

    def __repr__(self):
        return f"DEMFetcher(location='{self.filepath}')"