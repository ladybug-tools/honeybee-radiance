"""Base Radiance Mixture class.

A mixture is a blend of one or more materials or textures and patterns. Blended
materials should not be light source types or virtual source types.
More information on Radiance Mixtures can be found at:

http://radsite.lbl.gov/radiance/refer/ray.html#Mixtures
"""
from ..modifierbase import Modifier


class Mixture(Modifier):
    """Base class for Radiance mixtures.

    Properties:
        * identifier
        * display_name
        * values
        * modifier
        * dependencies
        * is_mixture
    """
    __slots__ = ()

    @property
    def is_mixture(self):
        """Get a boolean noting whether this object is a mixture modifier."""
        return True
