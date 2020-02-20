"""Radiance Bubble.

http://radsite.lbl.gov/radiance/refer/ray.html#Bubble
"""
from .sphere import Sphere


class Bubble(Sphere):
    """Radiance Bubble.

    A bubble is simply a sphere whose surface normal points inward.

    .. code-block:: shell

        mod bubble id
        0
        0
        4 xcent ycent zcent radius

    Args:
        name: Geometry name as a string. Do not use white space or special
            character.
        center_pt: Sphere center point as (x, y, z) (Default: (0, 0 ,0)).
        radius: Bubble radius as a number (Default: 10).
        modifier: Geometry modifier (Default: "void").
        dependencies: A list of primitives that this primitive depends on. This
            argument is only useful for defining advanced primitives where the
            primitive is defined based on other primitives. (Default: [])

    Properties:
        * name
        * center_pt
        * radius
        * modifier
        * dependencies
        * values
    """
    __slots__ = ()

    pass
