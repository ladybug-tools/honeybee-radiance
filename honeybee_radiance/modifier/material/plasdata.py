"""Radiance Plasdata Material.

http://radsite.lbl.gov/radiance/refer/ray.html#Plasdata
"""
from .materialbase import Material


# TODO: Implement the class. It's currently only a generic Radiance Primitive
class Plasdata(Material):
    """Radiance Plasdata Material.

    Plasdata is used for arbitrary BRDF's that are most conveniently given as
    interpolated data. The arguments to this material are the data file and coordinate
    index functions, as well as a function to optionally modify the data values.

    .. code-block:: shell

        mod plasdata id
        3+n+
                func datafile
                funcfile x1 x2 .. xn transform
        0
        4+ red green blue spec A5 ..

    The coordinate indices (x1, x2, etc.) are themselves functions of the x, y and z
    direction to the incident light, plus the solid angle subtended by the light source
    (usually ignored). The data function (func) takes five variables, the interpolated
    value from the n-dimensional data file, followed by the x, y and z direction to the
    incident light and the solid angle of the source. The light source direction and
    size may of course be ignored by the function.

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
