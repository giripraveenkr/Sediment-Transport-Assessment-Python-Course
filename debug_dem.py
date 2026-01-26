# debug_dem.py
from src.wrr.aoi import AOI
from src.wrr.dem_fetcher import DEMFetcher
import os

def test_dem_workflow():
    print("Starting DEM Fetcher Test for Upper Isar...")

    # 1. Define Area of Interest: Upper Isar (Sylvenstein Reservoir area)
    # Coordinates: min_lon, max_lon, min_lat, max_lat
    print("Creating AOI for Upper Isar River...")
    isar_aoi = AOI(11.50, 11.65, 47.54, 47.62)
    
    # 2. Initialize the Fetcher
    fetcher = DEMFetcher(isar_aoi)
    print(f"Fetcher initialized: {fetcher}")

    # 3. Get API Key securely
    api_key = input("\nPlease paste your OpenTopography API Key: ").strip()
    if not api_key:
        print("No API Key provided. Exiting.")
        return

    # 4. Run Download
    print("\nAttempting Download...")
    fetcher.download(api_key)

    # 5. Run Clip
    print("\nAttempting Clip...")
    fetcher.clip()

    # 6. Run Reprojection (Critical for next steps)
    print("\nAttempting Reprojection to UTM...")
    fetcher.reproject()

    # 7. Verify Output
    if os.path.exists("data/dem/dem_projected.tif"):
        print("\nSUCCESS: dem_projected.tif exists in data/dem/!")
        print("Your Upper Isar Data is ready for analysis.")
    else:
        print("\nFAIL: No projected file found.")

if __name__ == "__main__":
    test_dem_workflow()