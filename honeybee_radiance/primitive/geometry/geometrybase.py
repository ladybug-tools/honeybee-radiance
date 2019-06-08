"""Base Radiance Surfaces class (e.g source, sphere, etc.).

http://radsite.lbl.gov/radiance/refer/ray.html#Materials
"""
from honeybee_radiance.primitive.primitivebase import Primitive


class Geometry(Primitive):
    """Base class for Radiance geometries."""

    @property
    def is_radiance_geometry(self):
        """Indicate that this object is a Radiance Geometry."""
        return True
