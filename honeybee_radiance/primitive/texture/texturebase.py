"""Base Radiance Texture class (Texfunc, Texdata).

http://radsite.lbl.gov/radiance/refer/ray.html#Textures
"""
from honeybee_radiance.primitive.primitivebase import Primitive


class Texture(Primitive):
    """Base class for Radiance texture (Texfunc, Texdata).

    A texture is a perturbation of the surface normal, and is given by either a function
    or data.

    Attributes:
        name: Primitive name as a string. Do not use white space or special character.
        modifier: Modifier. It can be primitive, mixture, texture or pattern.
            (Default: "void").
        values: A dictionary of primitive data. key is line number and item is the list
            of values {0: [], 1: [], 2: ['0.500', '0.500', '0.500', '0.000', '0.050']}
    """

    @property
    def is_radiance_texture(self):
        """Indicate that this object is a Radiance Material."""
        return True
