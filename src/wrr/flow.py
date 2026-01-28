"""
Module: flow.py
Description: Computes flow direction (D8) and flow accumulation using topological sort.
"""

import os
import numpy as np
import rasterio

class FlowRouter:
    """
    Computes flow direction and flow accumulation from a DEM
    using a D8 algorithm and topological sorting for speed.
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

        # D8 direction encoding (East=1, SE=2, S=4, SW=8, W=16, NW=32, N=64, NE=128)
        # Note: Array is [row, col]. 
        # Directions are relative to center cell.
        directions = np.array([
            [32, 64, 128],  # NW, N, NE
            [16,  0,   1],  # W, Center, E
            [ 8,  4,   2]   # SW, S, SE
        ])

        flow_dir = np.zeros(dem.shape, dtype=np.uint8)

        # Iterate over cells (skipping 1-pixel border for safety)
        # (For production code, we'd vectorise this, but loops are fine for clarity here)
        rows, cols = dem.shape
        for i in range(1, rows - 1):
            for j in range(1, cols - 1):
                window = dem[i - 1:i + 2, j - 1:j + 2]
                
                # Skip if center or neighbors are NoData
                if np.ma.is_masked(window):
                    continue

                center = dem[i, j]
                
                # Calculate drop: (Center - Neighbor)
                # Positive means water flows FROM center TO neighbor
                diff = center - window
                diff[1, 1] = -9999 # Ignore center cell itself

                # Find steepest descent
                max_drop = diff.max()
                
                if max_drop > 0:
                    # Get index of neighbor with max drop
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
        Compute flow accumulation using Topological Sort (Fast & Accurate).
        Avoids the "max iteration" limits of iterative approaches.

        Returns
        -------
        str
            Path to flow accumulation raster.
        """
        print("Computing flow accumulation (Topological Sort)...")

        with rasterio.open(flow_dir_path) as src:
            fdir = src.read(1)
            meta = src.meta.copy()

        rows, cols = fdir.shape
        
        # 1. Initialize Accumulation Grid (1 unit of rain per cell)
        acc = np.ones((rows, cols), dtype=np.int32)
        
        # 2. Calculate In-Degree (How many upstream neighbors flow into me?)
        # Map D8 codes to (drow, dcol) offset to DOWNSTREAM neighbor
        d8_map = {
            1: (0, 1), 2: (1, 1), 4: (1, 0), 8: (1, -1),
            16: (0, -1), 32: (-1, -1), 64: (-1, 0), 128: (-1, 1)
        }
        
        in_degree = np.zeros((rows, cols), dtype=np.int32)

        # Pass 1: Count inflows
        for r in range(rows):
            for c in range(cols):
                code = fdir[r, c]
                if code in d8_map:
                    dr, dc = d8_map[code]
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < rows and 0 <= nc < cols:
                        in_degree[nr, nc] += 1

        # 3. Identify Headwaters (Cells with 0 inflow)
        # These are the starting points of the river network
        queue = []
        for r in range(rows):
            for c in range(cols):
                if in_degree[r, c] == 0:
                    queue.append((r, c))

        # 4. Process Queue (Push flow downstream)
        processed_count = 0
        head = 0
        
        # We use a list as a queue; 'head' points to the next item to process
        while head < len(queue):
            r, c = queue[head]
            head += 1
            processed_count += 1
            
            # Where does this cell flow?
            code = fdir[r, c]
            if code in d8_map:
                dr, dc = d8_map[code]
                nr, nc = r + dr, c + dc
                
                if 0 <= nr < rows and 0 <= nc < cols:
                    # Push my accumulated water to my downstream neighbor
                    acc[nr, nc] += acc[r, c]
                    
                    # Decrement neighbor's in-degree (I have finished processing myself)
                    in_degree[nr, nc] -= 1
                    
                    # If neighbor has received all its inputs, add it to queue
                    if in_degree[nr, nc] == 0:
                        queue.append((nr, nc))

        print(f"  Processed {processed_count} cells successfully.")

        meta.update({
            "dtype": "int32",
            "count": 1,
            "nodata": -1
        })

        out_path = os.path.join(self.output_dir, "flow_accumulation.tif")

        with rasterio.open(out_path, "w", **meta) as dst:
            dst.write(acc, 1)

        print(f"Flow accumulation raster saved to {out_path}")
        return out_path

    def __repr__(self):
        return f"FlowRouter(DEM='{self.dem_path}')"