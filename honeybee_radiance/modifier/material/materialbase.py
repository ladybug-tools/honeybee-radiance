"""Base Radiance Material class (e.g plastic, glass, etc.).

More information on Radiance Materials can be found at:

http://radsite.lbl.gov/radiance/refer/ray.html#Materials
"""
from ..modifierbase import Modifier


class Material(Modifier):
    """Base class for Radiance materials."""

    __slots__ = ()

    @property
    def is_material(self):
        """Get a boolean noting whether this object is a material modifier."""
        return True
