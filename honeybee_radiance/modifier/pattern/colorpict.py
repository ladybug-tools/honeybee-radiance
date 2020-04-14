"""Radiance Colorpict Pattern.

http://radsite.lbl.gov/radiance/refer/ray.html#Colorpict
"""
from .patternbase import Pattern


# TODO: Implement the class. It's currently only a generic Radiance Primitive
class Colorpict(Pattern):
    """Radiance Colorpict Pattern.

    Colorpict is a special case of colordata, where the pattern is a two-dimensional
    image stored in the RADIANCE picture format. The dimensions of the image data are
    determined by the picture such that the smaller dimension is always 1, and the
    other is the ratio between the larger and the smaller. For example, a 500x338
    picture would have coordinates (u,v) in the rectangle between (0,0) and (1.48,1).

    .. code-block:: shell

        mod colorpict id
        7+
                rfunc gfunc bfunc pictfile
                funcfile u v transform
        0
        m A1 A2 .. Am

    Args:
        identifier: Text string for a unique Material ID. Must not contain spaces
            or special characters. This will be used to identify the object across
            a model and in the exported Radiance files.
        modifier: Modifier. It can be primitive, mixture, texture or pattern.
            (Default: None).
        values: An array 3 arrays for primitive data. Each of the 3 sub-arrays
            refer to a line number in the radiance primitve definitions and the
            values in each array correspond to values occurring within each line.
        is_opaque: A boolean to indicate whether this primitive is opaque.
        dependencies: A list of primitives that this primitive depends on. This
            argument is only useful for defining advanced primitives that are
            defined based on other primitives. (Default: []).

    Properties:
        * identifier
        * display_name
        * values
        * modifier
        * dependencies
        * is_modifier
        * is_material
        * is_opaque

    """
    __slots__ = ()

    pass
