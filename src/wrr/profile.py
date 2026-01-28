import rasterio
import numpy as np
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
import os


class ProfileSampler:
    """
    Samples elevation along a thalweg polyline
    and computes longitudinal distance.
    """

    def __init__(
        self,
        dem_path: str,
        thalweg_path: str,
        output_dir: str = "data/profile"
    ):
        """
        Parameters
        ----------
        dem_path : str
            Path to projected DEM (meters).
        thalweg_path : str
            Path to thalweg vector (GeoJSON).
        output_dir : str
            Directory to store profile outputs.
        """
        self.dem_path = dem_path
        self.thalweg_path = thalweg_path
        self.output_dir = output_dir

        os.makedirs(self.output_dir, exist_ok=True)

    def sample(self, spacing: float = 30.0):
        """
        Sample elevation along thalweg.
    
        Parameters
        ----------
        spacing : float
            Distance between sample points (meters).
    
        Returns
        -------
        pandas.DataFrame
            Longitudinal profile table.
        """
        print("Sampling longitudinal profile...")
    
        # Load thalweg
        gdf = gpd.read_file(self.thalweg_path)
        line = gdf.geometry.iloc[0]
    
        # Generate points along the line
        distances = np.arange(0, line.length, spacing)
        points = [line.interpolate(d) for d in distances]
    
        elevations = []
    
        # Open DEM ONCE and sample all points
        with rasterio.open(self.dem_path) as src:
            dem = src.read(1)
            for pt in points:
                row, col = src.index(pt.x, pt.y)
                elev = dem[row, col]
                elevations.append(elev)
    
        # Build DataFrame
        df = pd.DataFrame({
            "distance_m": distances,
            "x": [p.x for p in points],
            "y": [p.y for p in points],
            "elevation_m": elevations
        })
    
        out_csv = os.path.join(self.output_dir, "longitudinal_profile.csv")
        df.to_csv(out_csv, index=False)
    
        print(f"Profile CSV saved to {out_csv}")
        return df
    def plot(self, df):
        """
        Plot longitudinal profile.
        """
        import matplotlib.pyplot as plt
        import os
    
        plt.figure(figsize=(10, 4))
        plt.plot(df["distance_m"], df["elevation_m"], lw=2)
        plt.xlabel("Distance along river (m)")
        plt.ylabel("Elevation (m)")
        plt.title("Longitudinal Profile")
        plt.grid(True)
    
        out_fig = os.path.join(self.output_dir, "longitudinal_profile.png")
        plt.savefig(out_fig, dpi=200)
        plt.close()
    
        print(f"Profile plot saved to {out_fig}")

