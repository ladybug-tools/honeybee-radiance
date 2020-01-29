"""Radiance Transfunc Material.

http://radsite.lbl.gov/radiance/refer/ray.html#Transfunc
"""
from .materialbase import Material


# TODO: Implement the class. It's currently only a generic Radiance Primitive
class Transfunc(Material):
    """Radiance Transfunc Material.

    Transfunc is similar to plasfunc but with an arbitrary bidirectional transmittance
    distribution as well as a reflectance distribution. Both reflectance and
    transmittance are specified with the same function.

        mod transfunc id
        2+ brtd funcfile transform
        0
        6+ red green blue rspec trans tspec A7 ..

    Where trans is the total light transmitted and tspec is the non-Lambertian fraction
    of transmitted light. The function brtd should integrate to 1 over each projected
    hemisphere.
    """
    __slots__ = ()

    pass
