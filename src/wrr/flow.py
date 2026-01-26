"""
Module: flow.py
Description: Computes flow direction and flow accumulation using D8 algorithm.
"""

import os
import numpy as np
import rasterio


class FlowRouter:
    """
    Computes flow direction and flow accumulation from a DEM
    using a simple D8 algorithm.
    """

    def __init__(self, dem_path: str, output_dir: str = "data/flow"):
        """
        Parameters
        ----------
        dem_path : str
            Path to projected DEM (meters).
        output_dir : str
            Directory to store flow rasters.
        """
        self.dem_path = dem_path
        self.output_dir = output_dir

        os.makedirs(self.output_dir, exist_ok=True)

    def compute_flow_direction(self):
        """
        Compute D8 flow direction.

        Returns
        -------
        str
            Path to flow direction raster.
        """
        print("Computing flow direction (D8)...")

        with rasterio.open(self.dem_path) as src:
            dem = src.read(1, masked=True)
            meta = src.meta.copy()

        # D8 direction encoding
        directions = np.array([
            [32, 64, 128],
            [16,  0,   1],
            [8,   4,   2]
        ])

        flow_dir = np.zeros(dem.shape, dtype=np.uint8)

        # Iterate over cells (skipping 1-pixel border)
        for i in range(1, dem.shape[0] - 1):
            for j in range(1, dem.shape[1] - 1):
                window = dem[i - 1:i + 2, j - 1:j + 2]
                
                if np.ma.is_masked(window):
                    continue

                center = dem[i, j]
                diff = center - window
                diff[1, 1] = 0

                max_drop = diff.max()
                
                if max_drop > 0:
                    idx = np.unravel_index(np.argmax(diff), diff.shape)
                    flow_dir[i, j] = directions[idx]

        meta.update({
            "dtype": "uint8",
            "count": 1,
            "nodata": 0
        })

        out_path = os.path.join(self.output_dir, "flow_direction.tif")

        with rasterio.open(out_path, "w", **meta) as dst:
            dst.write(flow_dir, 1)

        print(f"Flow direction raster saved to {out_path}")
        return out_path

    def compute_flow_accumulation(self, flow_dir_path: str):
        """
        Compute flow accumulation from flow direction raster.

        Returns
        -------
        str
            Path to flow accumulation raster.
        """
        print("Computing flow accumulation...")

        with rasterio.open(flow_dir_path) as src:
            flow_dir = src.read(1)
            meta = src.meta.copy()

        # Initialize accumulation with 1
        acc = np.ones(flow_dir.shape, dtype=np.float32)

        # Safety brake to prevent infinite loops
        max_iterations = 200
        iteration = 0
        changed = True

        while changed and iteration < max_iterations:
            changed = False
            iteration += 1
            
            if iteration % 10 == 0:
                print(f"   Iteration {iteration}")

            for i in range(1, flow_dir.shape[0] - 1):
                for j in range(1, flow_dir.shape[1] - 1):
                    code = flow_dir[i, j]
                    
                    if code == 0:
                        continue

                    # Determine downstream neighbor
                    di, dj = 0, 0
                    if code == 1:     di, dj = 0, 1
                    elif code == 2:   di, dj = 1, 1
                    elif code == 4:   di, dj = 1, 0
                    elif code == 8:   di, dj = 1, -1
                    elif code == 16:  di, dj = 0, -1
                    elif code == 32:  di, dj = -1, -1
                    elif code == 64:  di, dj = -1, 0
                    elif code == 128: di, dj = -1, 1

                    ni, nj = i + di, j + dj

                    if 0 <= ni < flow_dir.shape[0] and 0 <= nj < flow_dir.shape[1]:
                        # Push accumulation downstream
                        if acc[ni, nj] < acc[i, j] + 1:
                            acc[ni, nj] = acc[i, j] + 1
                            changed = True

        meta.update({
            "dtype": "float32",
            "count": 1,
            "nodata": 0
        })

        out_path = os.path.join(self.output_dir, "flow_accumulation.tif")

        with rasterio.open(out_path, "w", **meta) as dst:
            dst.write(acc, 1)

        print(f"Flow accumulation raster saved to {out_path}")
        return out_path

    def __repr__(self):
        return f"FlowRouter(DEM='{self.dem_path}')"
