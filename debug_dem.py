"""
debug_pipeline.py

End-to-end debug script to validate:
- AOI
- DEM download, clipping, reprojection
- Flow direction & accumulation
- Thalweg extraction
- Longitudinal profile sampling

Run this BEFORE proceeding to sediment transport computation.
"""

import sys
import os

# Make src/ discoverable for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from wrr import AOI, DEMFetcher, FlowRouter, ThalwegExtractor
from wrr.profile import ProfileSampler


def debug_pipeline():
    print("\n=== STARTING FULL PIPELINE DEBUG ===\n")

    # ------------------------------------------------------------------
    # 1. DEFINE AOI
    # ------------------------------------------------------------------
    print("1) Creating AOI...")
    aoi = AOI(
        xmin=11.85,
        xmax=12.00,
        ymin=48.40,
        ymax=48.55
    )
    print(f"   AOI created: {aoi}")

    # ------------------------------------------------------------------
    # 2. DEM FETCHING & PREPROCESSING
    # ------------------------------------------------------------------
    print("\n2) Initializing DEMFetcher...")
    dem_fetcher = DEMFetcher(aoi)
    print(f"   DEMFetcher: {dem_fetcher}")

    api_key = input("\nPaste OpenTopography API key: ").strip()
    if not api_key:
        raise RuntimeError("API key required to continue.")

    print("   Downloading DEM...")
    dem_fetcher.download(api_key)

    print("   Clipping DEM to AOI...")
    dem_fetcher.clip()

    print("   Reprojecting DEM to metric CRS...")
    dem_fetcher.reproject()

    dem_path = dem_fetcher.filepath
    if not os.path.exists(dem_path):
        raise RuntimeError("Projected DEM not found. Stopping pipeline.")

    print(f"   ✓ Projected DEM ready: {dem_path}")

    # ------------------------------------------------------------------
    # 3. FLOW ROUTING
    # ------------------------------------------------------------------
    print("\n3) Running flow routing...")
    router = FlowRouter(dem_path)

    print("   Computing flow direction...")
    flow_dir_path = router.compute_flow_direction()

    print("   Computing flow accumulation...")
    flow_acc_path = router.compute_flow_accumulation(flow_dir_path)

    if not os.path.exists(flow_acc_path):
        raise RuntimeError("Flow accumulation raster missing.")

    print(f"   ✓ Flow accumulation ready: {flow_acc_path}")

    # ------------------------------------------------------------------
    # 4. THALWEG EXTRACTION
    # ------------------------------------------------------------------
    print("\n4) Extracting thalweg...")
    thalweg_extractor = ThalwegExtractor(
        flow_acc_path=flow_acc_path,
        dem_path=dem_path,
        threshold=100
    )

    thalweg_path = thalweg_extractor.extract()

    if not os.path.exists(thalweg_path):
        raise RuntimeError("Thalweg extraction failed.")

    print(f"   ✓ Thalweg extracted: {thalweg_path}")

    # ------------------------------------------------------------------
    # 5. LONGITUDINAL PROFILE SAMPLING
    # ------------------------------------------------------------------
    print("\n5) Sampling longitudinal profile...")

    sampler = ProfileSampler(
        dem_path=dem_path,
        thalweg_path=thalweg_path
    )

    profile_df = sampler.sample(spacing=30)
    sampler.plot(profile_df)

    profile_dir = "data/profile"
    print(f"   ✓ Profile CSV and plot saved in: {profile_dir}")

    # ------------------------------------------------------------------
    # FINAL SUMMARY
    # ------------------------------------------------------------------
    print("\n=== PIPELINE DEBUG SUCCESSFUL ===")
    print("Generated outputs:")
    print(f" - DEM (projected): {dem_path}")
    print(f" - Flow accumulation: {flow_acc_path}")
    print(f" - Thalweg vector: {thalweg_path}")
    print(f" - Longitudinal profile: {profile_dir}")
    print("\nYou are READY to proceed to sediment transport computation.")


if __name__ == "__main__":
    debug_pipeline()
