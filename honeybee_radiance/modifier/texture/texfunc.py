"""Radiance Texfunc Texture.

A texture is a perturbation of the surface normal, and is given by either a function or
data.

http://radsite.lbl.gov/radiance/refer/ray.html#Texfunc
"""
from .texturebase import Texture


# TODO: Implement the class. It's currently only a generic Radiance Primitive
class Texfunc(Texture):
    """Radiance Texfunc Material.

    A texfunc uses an auxiliary function file to specify a procedural texture:

    .. code-block:: shell

        mod texfunc id
        4+ xpert ypert zpert funcfile transform
        0
        n A1 A2 .. An
    """
    __slots__ = ()

    pass
