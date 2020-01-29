"""Radiance Interface Material.

http://radsite.lbl.gov/radiance/refer/ray.html#Interface
"""
from .materialbase import Material


# TODO: Implement the class. It's currently only a generic Radiance Primitive
class Interface(Material):
    """Radiance Interface Material.

    An interface is a boundary between two dielectrics. The first transmission
    coefficient and refractive index are for the inside; the second ones are for the
    outside. Ordinary dielectrics are surrounded by a vacuum (1 1 1 1).

        mod interface id
        0
        0
        8 rtn1 gtn1 btn1 n1 rtn2 gtn2 btn2 n2

    """
    __slots__ = ()

    pass
