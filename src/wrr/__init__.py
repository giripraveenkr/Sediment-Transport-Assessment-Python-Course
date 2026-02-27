# src/wrr/__init__.py

# ======= Placeholder classes for debug pipeline =======

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
    def download(self, api_key):
        print("   (placeholder DEM download)")
        # ensure data folder exists
        import os
        os.makedirs("data", exist_ok=True)
        with open(self.filepath, "w") as f:
            f.write("dummy DEM")
    def clip(self):
        print("   (placeholder DEM clip)")
    def reproject(self):
        print("   (placeholder DEM reproject)")

class FlowRouter:
    def __init__(self, dem_path):
        self.dem_path = dem_path
    def compute_flow_direction(self):
        print("   (placeholder flow direction)")
        return "data/flow_direction.tif"
    def compute_flow_accumulation(self, flow_dir_path):
        print("   (placeholder flow accumulation)")
        return "data/flow_accumulation.tif"

class ThalwegExtractor:
    def __init__(self, flow_acc_path, dem_path, threshold):
        self.flow_acc_path = flow_acc_path
        self.dem_path = dem_path
        self.threshold = threshold
    def extract(self):
        print("   (placeholder thalweg)")
        return "data/thalweg.shp"