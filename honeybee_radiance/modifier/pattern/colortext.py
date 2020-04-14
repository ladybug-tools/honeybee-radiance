"""Radiance Colortext Pattern.

http://radsite.lbl.gov/radiance/refer/ray.html#Colortext
"""
from .patternbase import Pattern


# TODO: Implement the class. It's currently only a generic Radiance Primitive
class Colortext(Pattern):
    """Radiance Colortext Pattern.

    Colortext is dichromatic writing in a polygonal font. The font is defined in an
    auxiliary file, such as helvet.fnt. The text itself is also specified in a separate
    file, or can be part of the material arguments. The character size, orientation,
    aspect ratio and slant is determined by right and down motion vectors. The upper left
    origin for the text block as well as the foreground and background colors must also
    be given.

    .. code-block:: shell

        mod colortext id
        2 fontfile textfile
        0
        15+
                Ox Oy Oz
                Rx Ry Rz
                Dx Dy Dz
                rfore gfore bfore
                rback gback bback
                [spacing]

    or:

    .. code-block:: shell

        mod colortext id
        2+N fontfile . This is a line with N words ...
        0
        15+
                Ox Oy Oz
                Rx Ry Rz
                Dx Dy Dz
                rfore gfore bfore
                rback gback bback
                [spacing]

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
