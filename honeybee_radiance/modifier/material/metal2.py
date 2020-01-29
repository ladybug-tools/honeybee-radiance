"""Radiance Metal2 Material.

http://radsite.lbl.gov/radiance/refer/ray.html#Metal2
"""
from .materialbase import Material


# TODO: Implement the class. It's currently only a generic Radiance Primitive
class Metal2(Material):
    """Radiance Metal2 Material.

    Metal2 is the same as plastic2, except that the highlights are modified by the
    material color.

    """
    __slots__ = ()

    pass
