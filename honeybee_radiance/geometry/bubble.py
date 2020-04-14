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
        identifier: Text string for a unique Geometry ID. Must not contain spaces
            or special characters. This will be used to identify the object across
            a model and in the exported Radiance files.
        center_pt: Sphere center point as (x, y, z) (Default: (0, 0 ,0)).
        radius: Bubble radius as a number (Default: 10).
        modifier: Geometry modifier (Default: None).
        dependencies: A list of primitives that this primitive depends on. This
            argument is only useful for defining advanced primitives where the
            primitive is defined based on other primitives. (Default: [])

    Properties:
        * identifier
        * display_name
        * center_pt
        * radius
        * modifier
        * dependencies
        * values
    """
    __slots__ = ()

    pass
