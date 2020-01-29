"""Radiance Illum Material.

http://radsite.lbl.gov/radiance/refer/ray.html#Illum
"""
from .materialbase import Material


# TODO: Implement the class. It's currently only a generic Radiance Primitive
class Illum(Material):
    """Radiance Illum Material.

    Illum is used for secondary light sources with broad distributions. A secondary light
    source is treated like any other light source, except when viewed directly. It then
    acts like it is made of a different material (indicated by the string argument), or
    becomes invisible (if no string argument is given, or the argument is "void").
    Secondary sources are useful when modeling windows or brightly illuminated surfaces.

        mod illum id
        1 material
        0
        3 red green blue
    """
    __slots__ = ()

    pass
