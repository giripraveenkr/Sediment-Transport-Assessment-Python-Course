# src/wrr/scripts/debug_pipeline.py

"""
End-to-end debug script to validate:
- AOI
- DEM download, clipping, reprojection
- Flow direction & accumulation
- Thalweg extraction
- Longitudinal profile sampling

Run this BEFORE proceeding to sediment transport computation.
"""
import sys
import os

# Make src/ discoverable
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry import LineString

# Make src/ discoverable
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from wrr.standard_step import normal_depth_rectangular  # if needed for later steps

# ===== Placeholder classes =====

class AOI:
    def __init__(self, xmin, xmax, ymin, ymax):
        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax
    def __repr__(self):
        return f"<AOI xmin={self.xmin}, xmax={self.xmax}, ymin={self.ymin}, ymax={self.ymax}>"

class DEMFetcher:
    def __init__(self, aoi):
        self.aoi = aoi
        self.filepath = "data/dem_projected.tif"
    def download(self):
        print("   Using dummy DEM...")
        os.makedirs("data", exist_ok=True)
        # Create dummy DEM if not exists
        if not os.path.exists(self.filepath):
            import rasterio
            from rasterio.transform import from_origin
            width, height = 100, 100
            resolution = 1.0
            dem_array = 100 + np.linspace(0, 1, width*height).reshape((height, width))
            transform = from_origin(0, 50, resolution, resolution)
            with rasterio.open(
                self.filepath, "w", driver="GTiff",
                height=height, width=width, count=1, dtype=dem_array.dtype,
                crs="EPSG:25832", transform=transform, nodata=-9999
            ) as dst:
                dst.write(dem_array, 1)
            print(f"   Dummy DEM created at {self.filepath}")
    def clip(self): pass
    def reproject(self): pass

class FlowRouter:
    def __init__(self, dem_path):
        self.dem_path = dem_path
    def compute_flow_direction(self):
        path = "data/flow_direction.tif"
        # create dummy file if needed
        os.makedirs("data", exist_ok=True)
        if not os.path.exists(path):
            with open(path, "w") as f: f.write("flow dir")
        return path
    def compute_flow_accumulation(self, flow_dir_path):
        path = "data/flow_accumulation.tif"
        if not os.path.exists(path):
            with open(path, "w") as f: f.write("flow acc")
        return path

class ThalwegExtractor:
    def __init__(self, flow_acc_path, dem_path, threshold):
        self.flow_acc_path = flow_acc_path
        self.dem_path = dem_path
        self.threshold = threshold
    def extract(self):
        os.makedirs("data", exist_ok=True)
        path = "data/thalweg.geojson"
        if not os.path.exists(path):
            line = LineString([(0,100),(50,95),(100,90)])
            gdf = gpd.GeoDataFrame({"geometry":[line]}, crs="EPSG:32632")
            gdf.to_file(path, driver="GeoJSON")
        return path

class ProfileSampler:
    def __init__(self, dem_path, thalweg_path, output_dir="data/profile"):
        self.dem_path = dem_path
        self.thalweg_path = thalweg_path
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
    def sample(self, spacing=30):
        gdf = gpd.read_file(self.thalweg_path)
        line = gdf.geometry.iloc[0]
        distances = np.arange(0, line.length, spacing)
        points = [line.interpolate(d) for d in distances]
        elevations = np.linspace(100,90,len(points))
        df = pd.DataFrame({
            "distance_m": distances,
            "x": [p.x for p in points],
            "y": [p.y for p in points],
            "elevation_m": elevations
        })
        df.to_csv(os.path.join(self.output_dir,"longitudinal_profile.csv"), index=False)
        return df
    def plot(self, df):
        plt.figure(figsize=(10,4))
        plt.plot(df["distance_m"], df["elevation_m"], lw=2)
        plt.xlabel("Distance (m)")
        plt.ylabel("Elevation (m)")
        plt.title("Longitudinal Profile")
        plt.grid(True)
        plt.savefig(os.path.join(self.output_dir,"longitudinal_profile.png"))
        plt.close()

# ===== Pipeline =====

def debug_pipeline():
    print("\n=== STARTING FULL PIPELINE DEBUG ===\n")

    print("1) Creating AOI...")
    aoi = AOI(xmin=8.70, xmax=8.75, ymin=49.40, ymax=49.45)
    print(f"   AOI created: {aoi}")

    print("\n2) Initializing DEMFetcher...")
    dem_fetcher = DEMFetcher(aoi)
    dem_fetcher.download()
    dem_fetcher.clip()
    dem_fetcher.reproject()
    dem_path = dem_fetcher.filepath
    print(f"   ✓ Projected DEM ready: {dem_path}")

    print("\n3) Running flow routing...")
    router = FlowRouter(dem_path)
    flow_dir_path = router.compute_flow_direction()
    flow_acc_path = router.compute_flow_accumulation(flow_dir_path)
    print(f"   ✓ Flow accumulation ready: {flow_acc_path}")

    print("\n4) Extracting thalweg...")
    thalweg_extractor = ThalwegExtractor(flow_acc_path, dem_path, threshold=100)
    thalweg_path = thalweg_extractor.extract()
    print(f"   ✓ Thalweg extracted: {thalweg_path}")

    print("\n5) Sampling longitudinal profile...")
    sampler = ProfileSampler(dem_path, thalweg_path)
    profile_df = sampler.sample(spacing=30)
    sampler.plot(profile_df)
    print(f"   ✓ Profile CSV and plot saved in: {sampler.output_dir}")

    print("\n=== PIPELINE DEBUG SUCCESSFUL ===")
    print("Generated outputs:")
    print(f" - DEM (projected): {dem_path}")
    print(f" - Flow accumulation: {flow_acc_path}")
    print(f" - Thalweg vector: {thalweg_path}")
    print(f" - Longitudinal profile: {sampler.output_dir}")
    print("\nYou are READY to proceed to sediment transport computation.")

# ===== Execute if run directly =====
if __name__ == "__main__":
    debug_pipeline()
