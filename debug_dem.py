# debug_dem.py
from src.wrr.aoi import AOI
from src.wrr.dem_fetcher import DEMFetcher
from src.wrr.flow import FlowRouter
import os

def test_dem_workflow():
    print("Starting DEM Fetcher and Flow Routing Test for Upper Isar...")

    # 1. Define Area of Interest: Upper Isar (Sylvenstein Reservoir area)
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

    # 6. Run Reprojection
    print("\nAttempting Reprojection to UTM...")
    fetcher.reproject()

    # 7. Verify Projected DEM exists
    projected_dem = "data/dem/dem_projected.tif"
    
    if os.path.exists(projected_dem):
        print("\nSUCCESS: dem_projected.tif exists in data/dem/!")
    else:
        print("\nFAIL: No projected file found. Cannot proceed to flow routing.")
        return

    # 8. Run Flow Routing
    print("\nInitializing Flow Router...")
    # We use the projected DEM path
    router = FlowRouter(dem_path=projected_dem)

    print("Computing Flow Direction...")
    flow_dir_path = router.compute_flow_direction()

    print("Computing Flow Accumulation...")
    flow_acc_path = router.compute_flow_accumulation(flow_dir_path)

    # 9. Final Verification
    if os.path.exists(flow_acc_path):
        print(f"\nSUCCESS: Flow Accumulation saved at: {flow_acc_path}")
        print("Your Upper Isar Data is ready for analysis.")
    else:
        print("\nFAIL: Flow accumulation file missing.")

if __name__ == "__main__":
    test_dem_workflow()