"""Radiance Mixdata Mixture.

http://radsite.lbl.gov/radiance/refer/ray.html#Mixdata
"""
from .mixturebase import Mixture


# TODO: Implement the class. It's currently only a generic Radiance Primitive
class Mixdata(Mixture):
    """Radiance Mixdata Material.

    Mixdata combines two modifiers using an auxiliary data file:

        mod mixdata id
        5+n+
                foreground background func datafile
                funcfile x1 x2 .. xn transform
        0
        m A1 A2 .. Am

    """
    __slots__ = ()

    pass
