from dataclasses import dataclass
from shapely.geometry import box

@dataclass
class AOI:
    """
    Represents an Area of Interest (AOI) defined by a bounding box.
    """
    xmin: float
    xmax: float
    ymin: float
    ymax: float
    crs: str = "EPSG:4326"

    def __post_init__(self):
        """
        Validates input and creates derived geometry attributes.
        """
        # Requirement A.2: Reject invalid or inverted boxes
        if self.xmin >= self.xmax:
            raise ValueError(f"Invalid Longitude: West ({self.xmin}) must be less than East ({self.xmax})")
        
        if self.ymin >= self.ymax:
            raise ValueError(f"Invalid Latitude: South ({self.ymin}) must be less than North ({self.ymax})")

        # 1. Create the shapely geometry (for clipping)
        self.geometry = box(self.xmin, self.ymin, self.xmax, self.ymax)
        
        # 2. Create the 'bounds' tuple
        self.bounds = (self.xmin, self.ymin, self.xmax, self.ymax)

    def to_dict(self):
        """Returns the AOI details as a dictionary."""
        return {
            "bounds": self.bounds,
            "crs": self.crs
        }

    def __repr__(self):
        return f"AOI(bounds={self.bounds}, crs='{self.crs}')"