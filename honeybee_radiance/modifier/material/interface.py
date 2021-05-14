"""Radiance Interface Material.

http://radsite.lbl.gov/radiance/refer/ray.html#Interface
"""
from .materialbase import Material


# TODO: Implement the class. It's currently only a generic Radiance Primitive
class Interface(Material):
    """Radiance Interface Material.

    An interface is a boundary between two dielectrics. The first transmission
    coefficient and refractive index are for the inside; the second ones are for the
    outside. Ordinary dielectrics are surrounded by a vacuum (1 1 1 1).

    .. code-block:: shell

        mod interface id
        0
        0
        8 rtn1 gtn1 btn1 n1 rtn2 gtn2 btn2 n2

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
