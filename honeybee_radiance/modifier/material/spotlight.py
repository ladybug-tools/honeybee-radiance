"""Radiance Spotlight Material.

http://radsite.lbl.gov/radiance/refer/ray.html#Spotlight
"""
from .materialbase import Material


# TODO: Implement the class. It's currently only a generic Radiance Primitive
class Spotlight(Material):
    """Radiance Spotlight Material.

    Spotlight is used for self-luminous surfaces having directed output. As well as
    radiance, the full cone angle (in degrees) and orientation (output direction) vector
    are given. The length of the orientation vector is the distance of the effective
    focus behind the source center (i.e., the focal length).

        mod spotlight id
        0
        0
        7 red green blue angle xdir ydir zdir

    """
    __slots__ = ()

    pass
