"""Radiance Brightdata Texture.

http://radsite.lbl.gov/radiance/refer/ray.html#Brightdata
"""
from .patternbase import Pattern


# TODO: Implement the class. It's currently only a generic Radiance Primitive
class Brightdata(Pattern):
    """Radiance Brightdata Material.

    Brightdata is like colordata, except monochromatic.

        mod brightdata id
        3+n+
                func datafile
                funcfile x1 x2 .. xn transform
        0
        m A1 A2 .. Am
    """
    __slots__ = ()

    pass
