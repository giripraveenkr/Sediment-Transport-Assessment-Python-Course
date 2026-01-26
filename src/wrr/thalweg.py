import rasterio
import numpy as np
import geopandas as gpd
from shapely.geometry import LineString
import os


class ThalwegExtractor:
    """
    Extracts the main thalweg (river centerline)
    from a flow accumulation raster.
    """

    def __init__(
        self,
        flow_acc_path: str,
        dem_path: str,
        output_dir: str = "data/thalweg",
        threshold: float = 1000
    ):
        """
        Parameters
        ----------
        flow_acc_path : str
            Path to flow accumulation raster.
        dem_path : str
            Path to projected DEM.
        output_dir : str
            Directory to store thalweg vector.
        threshold : float
            Minimum flow accumulation to define river cells.
        """
        self.flow_acc_path = flow_acc_path
        self.dem_path = dem_path
        self.output_dir = output_dir
        self.threshold = threshold

        os.makedirs(self.output_dir, exist_ok=True)

    def extract(self):
        """
        Extract the main thalweg as a polyline.

        Returns
        -------
        str
            Path to thalweg GeoJSON file.
        """
        print("Extracting thalweg from flow accumulation...")

        with rasterio.open(self.flow_acc_path) as src:
            acc = src.read(1)
            transform = src.transform
            crs = src.crs

        # Select river cells
        river_mask = acc >= self.threshold

        rows, cols = np.where(river_mask)
        if len(rows) < 2:
            raise RuntimeError("Threshold too high: no river cells found.")

        # Convert raster indices to coordinates
        coords = []
        for r, c in zip(rows, cols):
            x, y = rasterio.transform.xy(transform, r, c)
            coords.append((x, y))

        # Sort points by downstream direction (approx: y-coordinate)
        coords = sorted(coords, key=lambda x: x[1], reverse=True)

        thalweg = LineString(coords)

        gdf = gpd.GeoDataFrame(
            {"geometry": [thalweg]},
            crs=crs
        )

        out_path = f"{self.output_dir}/thalweg.geojson"
        gdf.to_file(out_path, driver="GeoJSON")

        print(f"Thalweg saved to {out_path}")
        return out_path

    def __repr__(self):
        return f"ThalwegExtractor(threshold={self.threshold})"
