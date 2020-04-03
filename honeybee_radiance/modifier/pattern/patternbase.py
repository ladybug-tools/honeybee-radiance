"""Base Radiance Pattern class.

Patterns are used to modify the reflectance of materials.
More information on Radiance Patterns can be found at:

http://radsite.lbl.gov/radiance/refer/ray.html#Patterns
"""
from ..modifierbase import Modifier


class Pattern(Modifier):
    """Base class for Radiance patterns.

    Patterns are used to modify the reflectance of materials.

    Properties:
        * identifier
        * display_name
        * values
        * modifier
        * dependencies
        * is_modifier
        * is_material
        * is_texture
        * is_pattern
        * is_mixture
        * is_opaque
    """
    __slots__ = ()

    @property
    def is_pattern(self):
        """Get a boolean noting whether this object is a pattern modifier."""
        return True
