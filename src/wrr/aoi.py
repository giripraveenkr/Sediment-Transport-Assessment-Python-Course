from dataclasses import dataclass
from shapely.geometry import box


@dataclass
class AOI:
    """
    Represents an Area of Interest (AOI) defined by a bounding box.

    Attributes:
        xmin (float): Minimum X coordinate (longitude).
        xmax (float): Maximum X coordinate (longitude).
        ymin (float): Minimum Y coordinate (latitude).
        ymax (float): Maximum Y coordinate (latitude).
        crs (str): Coordinate Reference System (default: EPSG:4326).
    """
    xmin: float
    xmax: float
    ymin: float
    ymax: float
    crs: str = "EPSG:4326"

    def __post_init__(self):
        """
        Automatically creates a shapely geometry object after initialization.
        This allows the AOI to be used directly in spatial operations.
        """
        self.geometry = box(self.xmin, self.ymin, self.xmax, self.ymax)

    def to_dict(self):
        """
        Returns the AOI details as a dictionary.
        """
        return {
            "bounds": (self.xmin, self.ymin, self.xmax, self.ymax),
            "crs": self.crs
        }

    def __repr__(self):
        """
        Returns a readable string representation of the object.
        """
        return (
            f"AOI(bounds=({self.xmin}, {self.ymin}, "
            f"{self.xmax}, {self.ymax}), crs='{self.crs}')"
        )