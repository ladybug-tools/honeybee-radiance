"""Base Radiance Texture class (Texfunc, Texdata).

A texture is a perturbation of the surface normal, and is given by either a
function or a data set. More information on Radiance Textures can be found at:

http://radsite.lbl.gov/radiance/refer/ray.html#Textures
"""
from ..modifierbase import Modifier


class Texture(Modifier):
    """Base class for Radiance texture (Texfunc, Texdata).

    Properties:
        * name
        * values
        * modifier
        * dependencies
        * is_modifier
        * is_texture
    """
    __slots__ = ()

    @property
    def is_texture(self):
        """Get a boolean noting whether this object is a texture modifier."""
        return True
