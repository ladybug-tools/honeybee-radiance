"""Radiance Tube.

http://radsite.lbl.gov/radiance/refer/ray.html#Tube
"""
from .cylinder import Cylinder


class Tube(Cylinder):
    """Radiance Tube.
    A tube is an inverted cylinder. A cylinder is like a cone, but its starting and
    ending radii are equal.

    .. code-block:: shell

        mod tube id
        0
        0
        7
                x0      y0      z0
                x1      y1      z1
                rad

    Args:
        identifier: Text string for a unique Geometry ID. Must not contain spaces
            or special characters. This will be used to identify the object across
            a model and in the exported Radiance files.
        center_pt_start: Tube start center point as (x, y, z)
            (Default: (0, 0 ,0)).
        center_pt_end: Tube end center point as (x, y, z) (Default: (0, 0 ,10)).
        radius: Tube start radius as a number (Default: 10).
        modifier: Geometry modifier (Default: None).
        dependencies: A list of primitives that this primitive depends on. This
            argument is only useful for defining advanced primitives where the
            primitive is defined based on other primitives. (Default: [])

    Properties:
        * identifier
        * display_name
        * center_pt_start
        * center_pt_end
        * radius
        * values
        * modifier
        * dependencies
    """
    pass
