import numpy as np
import rasterio
from rasterio.transform import from_origin
import os
import shutil

# Ensure the folder exists
os.makedirs("data", exist_ok=True)

# Larger DEM for smoother profile, fast enough for <1 min runtime
width, height = 100, 100
resolution = 1.0  # meters per pixel
dem_array = 100 + np.linspace(0, 1, width*height).reshape((height, width))  # simple slope

# Define a transform (origin at top-left corner)
transform = from_origin(0, 50, resolution, resolution)

# Output paths
dem_1m_path = "data/dem_1m.tif"
dem_projected_path = "data/dem_projected.tif"

# Write dem_1m.tif
with rasterio.open(
    dem_1m_path, "w",
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

# Immediately copy to dem_projected.tif so pipeline always finds it
shutil.copy(dem_1m_path, dem_projected_path)

print(f"Dummy DEMs created at {dem_1m_path} and {dem_projected_path}")