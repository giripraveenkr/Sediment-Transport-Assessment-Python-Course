# src/wrr/__init__.py (DEMFetcher part)

class DEMFetcher:
    """
    Placeholder DEM fetcher for pipeline.
    Creates a valid GeoTIFF, clips it, and reprojects it (simulated).
    """

    def __init__(self, aoi):
        self.aoi = aoi
        self.filepath = "data/dem_projected.tif"

    def download(self, api_key=None):
        """
        Placeholder DEM download: creates a valid 50x50 GeoTIFF with random elevations.
        """
        print("   (placeholder DEM download: generating valid GeoTIFF)")

        import numpy as np
        import rasterio
        from rasterio.transform import from_origin
        import os

        os.makedirs("data", exist_ok=True)

        # DEM size and values
        width, height = 50, 50
        min_elev, max_elev = 90.0, 110.0  # meters
        dem_array = np.random.uniform(min_elev, max_elev, (height, width)).astype("float32")

        # Dummy transform: top-left at 0, height, 1 m pixels
        pixel_size = 1.0
        transform = from_origin(0, height, pixel_size, pixel_size)

        # Save GeoTIFF
        with rasterio.open(
            self.filepath,
            "w",
            driver="GTiff",
            height=height,
            width=width,
            count=1,
            dtype="float32",
            crs="EPSG:25832",
            transform=transform,
        ) as dst:
            dst.write(dem_array, 1)

        print(f"   ✓ Placeholder DEM created at {self.filepath}")

    def clip(self):
        """
        Placeholder clip: crops DEM array to simulate AOI clipping.
        """
        import rasterio

        print("   (placeholder DEM clipping)")

        with rasterio.open(self.filepath) as src:
            dem = src.read(1)
            transform = src.transform
            profile = src.profile

        # simulate clipping: take center 40x40 pixels
        dem_clipped = dem[5:45, 5:45]
        new_transform = rasterio.transform.from_origin(
            transform.c + 5 * transform.a,  # shift top-left x
            transform.f - 5 * transform.e,  # shift top-left y
            transform.a,
            transform.e
        )

        profile.update({
            "height": dem_clipped.shape[0],
            "width": dem_clipped.shape[1],
            "transform": new_transform
        })

        with rasterio.open(self.filepath, "w", **profile) as dst:
            dst.write(dem_clipped, 1)

        print(f"   ✓ DEM clipped: {self.filepath}")

    def reproject(self):
        """
        Placeholder reproject: rewrite DEM to simulate reprojection (same CRS).
        """
        import rasterio

        print("   (placeholder DEM reproject)")

        with rasterio.open(self.filepath) as src:
            dem = src.read(1)
            profile = src.profile

        # in placeholder, just rewrite the same array
        with rasterio.open(self.filepath, "w", **profile) as dst:
            dst.write(dem, 1)

        print(f"   ✓ DEM reprojected: {self.filepath}")