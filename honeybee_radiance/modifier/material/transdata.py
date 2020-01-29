"""Radiance Transdata Material.

http://radsite.lbl.gov/radiance/refer/ray.html#Transdata
"""
from .materialbase import Material


# TODO: Implement the class. It's currently only a generic Radiance Primitive
class Transdata(Material):
    """Radiance Transdata Material.

    Transdata is like plasdata but the specification includes transmittance as well as
    reflectance. The parameters are as follows.

        mod transdata id
        3+n+
                func datafile
                funcfile x1 x2 .. xn transform
        0
        6+ red green blue rspec trans tspec A7 ..

    """
    __slots__ = ()

    pass
