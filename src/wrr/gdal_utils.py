from __future__ import annotations
from pathlib import Path
from typing import Iterable
import numpy as np
import rasterio
from rasterio import features
from shapely.geometry import LineString, mapping

def build_vrt(tile_paths: Iterable[str], vrt_path: str) -> None:
    """Build a VRT from GeoTIFF tiles using rasterio.vrt.WarpedVRT if needed."""
    # Placeholder: In production, prefer gdalbuildvrt CLI; here we simply document paths.
    Path(vrt_path).write_text("\n".join(str(p) for p in tile_paths))

def warp_resample(src_path: str, dst_path: str, dst_crs: str, res: float, resampling="bilinear") -> None:
    """Thin wrapper for gdalwarp-like behavior using rasterio.reproject (left to student)."""
    # Intentionally minimal to encourage students to fill in with their AOI and parameters.
    with rasterio.open(src_path) as src:
        transform = src.transform * src.transform.scale(src.res[0]/res, src.res[1]/res)
        profile = src.profile
        profile.update(crs=dst_crs, transform=transform, height=int(src.height * src.res[0]/res), width=int(src.width * src.res[1]/res))
        data = src.read(1, out_shape=(profile['height'], profile['width']))
        with rasterio.open(dst_path, 'w', **profile) as dst:
            dst.write(data, 1)

def rasterize_polygons(polygons, values, template_path: str, out_path: str) -> None:
    """Rasterize value-coded polygons to the grid of a template raster."""
    with rasterio.open(template_path) as src:
        profile = src.profile
        shape = (src.height, src.width)
        transform = src.transform
    out = features.rasterize(
        [(mapping(geom), val) for geom, val in zip(polygons, values)],
        out_shape=shape, transform=transform, fill=0, dtype="int16")
    with rasterio.open(out_path, 'w', **profile) as dst:
        dst.write(out, 1)

def sample_profile_from_raster(raster_path: str, line: LineString, npts: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Sample elevations along a line; returns s, x, z arrays."""
    xs = np.linspace(0, 1, npts)
    coords = [line.interpolate(d, normalized=True).coords[0] for d in xs]
    with rasterio.open(raster_path) as src:
        zs = [v[0] for v in src.sample(coords)]
    s = xs * line.length
    xy = np.asarray(coords)
    z = np.asarray(zs)
    return s, xy, z
