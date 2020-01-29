"""Radiance Metfunc Material.

http://radsite.lbl.gov/radiance/refer/ray.html#Metfunc
"""
from .materialbase import Material


# TODO: Implement the class. It's currently only a generic Radiance Primitive
class Metfunc(Material):
    """Radiance Metfunc Material.

    Metfunc is identical to plasfunc and takes the same arguments, but the specular
    component is multiplied also by the material color.
    """
    __slots__ = ()

    pass
