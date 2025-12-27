# GDAL notes

Record the exact commands or Python calls you used and why their parameters make sense. Include resampling method, nodata handling, and target resolution.

Example:
- Built VRT from tiles:
  gdalbuildvrt -resolution highest dem.vrt tiles/*.tif
- Warped to project grid (1 m):
  gdalwarp -t_srs EPSG:25832 -tr 1 1 -r bilinear -dstnodata -9999 dem.vrt dem_1m.tif
