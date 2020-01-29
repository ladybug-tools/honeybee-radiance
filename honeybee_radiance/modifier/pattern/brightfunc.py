"""Radiance Brightfunc Pattern.

http://radsite.lbl.gov/radiance/refer/ray.html#Brightfunc
"""
from .patternbase import Pattern


# TODO: Implement the class. It's currently only a generic Radiance Primitive
class Brightfunc(Pattern):
    """Radiance Brightfunc Material.

    A brightfunc is the same as a colorfunc, except it is monochromatic.

        mod brightfunc id
        2+ refl funcfile transform
        0
        n A1 A2 .. An
    """
    __slots__ = ()

    pass
