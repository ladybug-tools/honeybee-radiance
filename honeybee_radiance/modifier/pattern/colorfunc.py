"""Radiance Colorfunc Texture.

http://radsite.lbl.gov/radiance/refer/ray.html#Colorfunc
"""
from .patternbase import Pattern


# TODO: Implement the class. It's currently only a generic Radiance Primitive
class Colorfunc(Pattern):
    """Radiance Colorfunc Material.

    A colorfunc is a procedurally defined color pattern. It is specified as follows:

        mod colorfunc id
        4+ red green blue funcfile transform
        0
        n A1 A2 .. An

    """
    __slots__ = ()

    pass
