"""Base Radiance Material class (e.g plastic, glass, etc.).

http://radsite.lbl.gov/radiance/refer/ray.html#Materials
"""
from honeybee_radiance.primitive.primitivebase import Primitive


class Material(Primitive):
    """Base class for Radiance materials."""

    @property
    def is_radiance_material(self):
        """Indicate that this object is a Radiance Material."""
        return True
