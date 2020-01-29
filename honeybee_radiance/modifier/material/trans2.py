"""Radiance Trans2 Material.

http://radsite.lbl.gov/radiance/refer/ray.html#Trans2
"""
from .materialbase import Material


# TODO: Implement the class. It's currently only a generic Radiance Primitive
class Trans2(Material):
    """Radiance Trans2 Material.

    Trans2 is the anisotropic version of trans. The string arguments are the same as for
    plastic2, and the real arguments are the same as for trans but with an additional
    roughness value.

        mod trans2 id
        4+ ux uy uz funcfile transform
        0
        8 red green blue spec urough vrough trans tspec

    """
    __slots__ = ()

    pass
