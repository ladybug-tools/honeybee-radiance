"""Base Radiance Modifier class.

A modifier is anything that can be applied to geometry in order to modify its
reflectance, transmittance, etc. It includes Radiance materials as well as
patterns, textures and mixtures of other modifiers.

Modifiers can also be used to modify other modifiers in addition to modifying
geometry. More information on Radiance Modifiers can be found at:

https://floyd.lbl.gov/radiance/refer/ray.html
"""
from ..primitive import Primitive


class Modifier(Primitive):
    """Base class for Radiance modifiers.

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
    def is_modifier(self):
        """Get a boolean indicating whether this object is a Radiance modifier.

        Modifiers include materials, mixtures, textures and patterns.
        """
        return True
