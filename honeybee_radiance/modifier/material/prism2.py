"""Radiance Prism2 Material.

http://radsite.lbl.gov/radiance/refer/ray.html#Prism2
"""
from .materialbase import Material


# TODO: Implement the class. It's currently only a generic Radiance Primitive
class Prism2(Material):
    """Radiance Prism2 Material.

    The material prism2 is identical to prism1 except that it provides for two ray
    redirections rather than one.

        mod prism2 id
        9+ coef1 dx1 dy1 dz1 coef2 dx2 dy2 dz2 funcfile transform
        0
        n A1 A2 .. An

    """
    __slots__ = ()

    pass
