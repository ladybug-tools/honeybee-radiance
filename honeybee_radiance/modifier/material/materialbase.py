"""Base Radiance Material class (e.g plastic, glass, etc.).

More information on Radiance Materials can be found at:

http://radsite.lbl.gov/radiance/refer/ray.html#Materials
"""
from ..modifierbase import Modifier


class Material(Modifier):
    """Base class for Radiance materials.

    Properties:
        * identifier
        * display_name
        * values
        * modifier
        * dependencies
        * is_modifier
        * is_material

    """

    __slots__ = ()

    @property
    def is_material(self):
        """Get a boolean noting whether this object is a material modifier."""
        return True
