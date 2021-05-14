"""Radiance Colordata Pattern.

http://radsite.lbl.gov/radiance/refer/ray.html#Colordata
"""
from .patternbase import Pattern


# TODO: Implement the class. It's currently only a generic Radiance Primitive
class Colordata(Pattern):
    """Radiance Colordata Pattern.

    Colordata uses an interpolated data map to modify a material's color. The map is
    n-dimensional, and is stored in three auxiliary files, one for each color. The
    coordinates used to look up and interpolate the data are defined in another auxiliary
    file. The interpolated data values are modified by functions of one or three
    variables. If the functions are of one variable, then they are passed the
    corresponding color component (red or green or blue). If the functions are of three
    variables, then they are passed the original red, green, and blue values as
    parameters.

    .. code-block:: shell

        mod colordata id
        7+n+
                rfunc gfunc bfunc rdatafile gdatafile bdatafile
                funcfile x1 x2 .. xn transform
        0
        m A1 A2 .. Am

    Args:
        identifier: Text string for a unique Material ID. Must not contain spaces
            or special characters. This will be used to identify the object across
            a model and in the exported Radiance files.
        modifier: Modifier. It can be primitive, mixture, texture or pattern.
            (Default: None).
        values: An array 3 arrays for primitive data. Each of the 3 sub-arrays
            refer to a line number in the radiance primitive definitions and the
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
