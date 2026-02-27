# DEM Preprocessing (GDAL Commands & Notes)

# 1. Build a VRT mosaic from all DEM tiles
gdalbuildvrt -resolution highest dem.vrt tiles/*.tif
# -resolution highest: keeps the finest resolution among input tiles
# dem.vrt: virtual raster referencing all tiles (no actual data copied)
# tiles/*.tif: input DEM tiles to be mosaicked
# Notes: Using a VRT allows fast testing and avoids creating huge intermediate files.

# 2. Warp to project CRS and target resolution (1 m)
gdalwarp -t_srs EPSG:25832 -tr 1 1 -r bilinear -dstnodata -9999 dem.vrt dem_1m.tif
# -t_srs EPSG:25832: reproject to metric UTM CRS (meters)
# -tr 1 1: resample to uniform 1x1 m grid
# -r bilinear: smooth resampling suitable for continuous elevation data
# -dstnodata -9999: assign nodata value to masked/missing pixels
# dem.vrt -> dem_1m.tif: input VRT and output raster
# Notes: Consistent CRS and resolution are required for flow routing, slope, and sediment transport calculations.

# 3. Optional: clip to Area of Interest (AOI)
gdalwarp -te minx miny maxx maxy -t_srs EPSG:25832 -tr 1 1 -r bilinear -dstnodata -9999 dem_1m.tif dem_clip.tif
# -te minx miny maxx maxy: bounding box coordinates of AOI
# Notes: Reduces file size, focuses analysis on the river corridor, and prevents unnecessary processing outside study area.

# Additional Notes:
# - Bilinear resampling preserves smooth terrain; nearest-neighbor should only be used for categorical rasters.
# - dstnodata ensures that invalid pixels are ignored in downstream computations (flow accumulation, slope, sediment transport).
# - Matching resolution (-tr) to project grid ensures accurate distance, slope, and hydraulic calculations.