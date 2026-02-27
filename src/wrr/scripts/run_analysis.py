# src/wrr/scripts/run_analysis.py

import os
import shutil
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry import LineString
import rasterio
from rasterio.transform import from_origin
from wrr.standard_step import normal_depth_rectangular

# ======= Placeholder classes =======

class AOI:
    def __init__(self, xmin, xmax, ymin, ymax):
        self.xmin = xmin; self.xmax = xmax
        self.ymin = ymin; self.ymax = ymax
    def __repr__(self):
        return f"<AOI xmin={self.xmin}, xmax={self.xmax}, ymin={self.ymin}, ymax={self.ymax}>"

class DEMFetcher:
    def __init__(self, aoi):
        self.aoi = aoi
        self.filepath = "data/dem_projected.tif"
    def download(self, api_key=None):
        os.makedirs("data", exist_ok=True)
        if not os.path.exists(self.filepath):
            with open(self.filepath, "w") as f: f.write("dummy DEM")
    def clip(self): pass
    def reproject(self): pass

class FlowRouter:
    def __init__(self, dem_path): self.dem_path = dem_path
    def compute_flow_direction(self): return "data/flow_direction.tif"
    def compute_flow_accumulation(self, flow_dir_path): return "data/flow_accumulation.tif"

class ThalwegExtractor:
    def __init__(self, flow_acc_path, dem_path, threshold): pass
    def extract(self):
        os.makedirs("data", exist_ok=True)
        path = "data/thalweg.geojson"
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
        plt.xlabel("Distance (m)"); plt.ylabel("Elevation (m)")
        plt.title("Longitudinal Profile"); plt.grid(True)
        plt.savefig(os.path.join(self.output_dir,"longitudinal_profile.png"))
        plt.close()

class SedimentTransport:
    def __init__(self, slope, depth, grain_size): self.slope = slope
    def meyer_peter_muller(self, N):
        return np.random.rand(N)

# ======= MAIN PIPELINE =======

def main(bbox=None):
    print("Received bbox:", bbox)

    # ------------------------------------------------------------------
    # 0. Ensure DEM exists (100x100 dummy)
    # ------------------------------------------------------------------
    dem_path = "data/dem_1m.tif"
    projected_path = "data/dem_projected.tif"
    os.makedirs("data", exist_ok=True)

    if not os.path.exists(dem_path):
        print("DEM not found, creating dummy 100x100 DEM...")
        width, height = 100, 100
        resolution = 1.0
        dem_array = 100 + np.linspace(0, 1, width*height).reshape((height, width))
        transform = from_origin(0, height, resolution, resolution)
        with rasterio.open(
            dem_path, "w",
            driver="GTiff",
            height=height,
            width=width,
            count=1,
            dtype=dem_array.dtype,
            crs="EPSG:25832",
            transform=transform,
            nodata=-9999
        ) as dst:
            dst.write(dem_array, 1)
        print(f"Dummy DEM created at {dem_path}")

    if not os.path.exists(projected_path):
        shutil.copy(dem_path, projected_path)
        print(f"Copied DEM to {projected_path}")

    # ------------------------------------------------------------------
    # 1. Define AOI
    # ------------------------------------------------------------------
    aoi = AOI(xmin=8.7, xmax=8.75, ymin=49.4, ymax=49.45)
    print("AOI:", aoi)

    # ------------------------------------------------------------------
    # 2. Initialize DEMFetcher
    # ------------------------------------------------------------------
    dem_fetcher = DEMFetcher(aoi)
    dem_fetcher.download()
    dem_fetcher.clip()
    dem_fetcher.reproject()

    # ------------------------------------------------------------------
    # 3. Flow routing
    # ------------------------------------------------------------------
    router = FlowRouter(dem_path=projected_path)
    flow_dir = router.compute_flow_direction()
    flow_acc = router.compute_flow_accumulation(flow_dir)

    # ------------------------------------------------------------------
    # 4. Thalweg extraction
    # ------------------------------------------------------------------
    thalweg_extractor = ThalwegExtractor(flow_acc_path=flow_acc, dem_path=projected_path, threshold=100)
    thalweg_path = thalweg_extractor.extract()

    # ------------------------------------------------------------------
    # 5. Profile sampling
    # ------------------------------------------------------------------
    sampler = ProfileSampler(dem_path=projected_path, thalweg_path=thalweg_path)
    profile_df = sampler.sample()
    sampler.plot(profile_df)

    # ------------------------------------------------------------------
    # 6. Sediment transport (placeholder)
    # ------------------------------------------------------------------
    slope = np.gradient(profile_df["elevation_m"], profile_df["distance_m"])
    sediment = SedimentTransport(slope=slope, depth=1.0, grain_size=0.02)
    transport = sediment.meyer_peter_muller(len(profile_df))

    # Save results
    df_out = pd.DataFrame({
        "distance_m": profile_df["distance_m"],
        "elevation_m": profile_df["elevation_m"],
        "slope": slope,
        "sediment_transport": transport
    })
    os.makedirs("results", exist_ok=True)
    df_out.to_csv("results/sediment_transport.csv", index=False)
    print("Saved results/sediment_transport.csv")

    plt.figure()
    plt.plot(profile_df["distance_m"], transport)
    plt.xlabel("Distance (m)"); plt.ylabel("Sediment Transport")
    plt.savefig("results/sediment_transport.png")
    plt.close()
    print("Saved results/sediment_transport.png")