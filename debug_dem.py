# debug_dem.py
from src.wrr.aoi import AOI
from src.wrr.dem_fetcher import DEMFetcher
import os

def test_dem_workflow():
    print("Starting DEM Fetcher Test...")

    # 1. Define a test Area of Interest (Stuttgart Center)
    # Bounds: min_lon, max_lon, min_lat, max_lat
    print("Creating AOI for Stuttgart...")
    stuttgart_aoi = AOI(9.17, 9.19, 48.77, 48.78)
    
    # 2. Initialize the Fetcher
    fetcher = DEMFetcher(stuttgart_aoi)
    print(f"Fetcher initialized: {fetcher}")

    # 3. Get API Key securely
    api_key = input("\n Please paste your OpenTopography API Key: ").strip()
    if not api_key:
        print("No API Key provided. Exiting.")
        return

    # 4. Run Download
    print("\n Attempting Download...")
    fetcher.download(api_key)

    # 5. Run Clip
    print("\n Attempting Clip...")
    fetcher.clip()

    # 6. Verify Output
    if os.path.exists("data/dem/dem.tif"):
        print("\n SUCCESS: dem.tif exists in data/dem/!")
        print("Your DEMFetcher is working correctly.")
    else:
        print("\n FAIL: No file found.")

if __name__ == "__main__":
    test_dem_workflow()