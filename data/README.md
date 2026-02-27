# Sediment Transport Assessment Pipeline

Automated workflow to extract river thalwegs, sample longitudinal profiles, compute slope, and estimate sediment transport along a river channel from a DEM.  

The pipeline is implemented in Python and is fully CLI-driven. Placeholder data is used for demonstration; real DEMs and landcover datasets can be integrated later.

---

## Data Inventory and Provenance

List every dataset used with link, license, CRS, and checksum/size.

-  **Source:** U.S. Geological Survey (USGS) 3D Elevation Program (3DEP)  
https://www.usgs.gov/3d-elevation-program   
- **License:** CC BY 4.0  
- **CRS:** EPSG:25832  
- **Files:**
  - `dem_1m_utm32.tif`, size 2.1 GB, SHA256: `<hash>`  
- **Notes:** DEM includes bridge decks; channel burned using surveyed thalweg.  

- **Notes:** For submission, include actual file hashes or sizes if using real data.*

---

## Setup Python Environment

Make sure you have **Anaconda** installed. Then run:

```powershell
# Create and activate environment
conda create -n wrr-proj python=3.10
conda activate wrr-proj

# Install dependencies
conda env update --file environment.yml