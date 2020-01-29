"""Radiance Metdata Material.

http://radsite.lbl.gov/radiance/refer/ray.html#Metdata
"""
from .materialbase import Material


# TODO: Implement the class. It's currently only a generic Radiance Primitive
class Metdata(Material):
    """Radiance Metdata Material.

    As metfunc is to plasfunc, metdata is to plasdata. Metdata takes the same arguments
    as plasdata, but the specular component is modified by the given material color.
    """
    __slots__ = ()

    pass
