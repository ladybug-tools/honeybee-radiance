"""Radiance Prism2 Material.

http://radsite.lbl.gov/radiance/refer/ray.html#Prism2
"""
from .materialbase import Material


# TODO: Implement the class. It's currently only a generic Radiance Primitive
class Prism2(Material):
    """Radiance Prism2 Material.

    The material prism2 is identical to prism1 except that it provides for two ray
    redirections rather than one.

    .. code-block:: shell

        mod prism2 id
        9+ coef1 dx1 dy1 dz1 coef2 dx2 dy2 dz2 funcfile transform
        0
        n A1 A2 .. An

    Args:
        name: Primitive name as a string. Cannot contain white spaces or special
            characters.
        modifier: Modifier. It can be primitive, mixture, texture or pattern.
            (Default: "void").
        values: An array 3 arrays for primitive data. Each of the 3 sub-arrays
            refer to a line number in the radiance primitve definitions and the
            values in each array correspond to values occurring within each line.
        is_opaque: A boolean to indicate whether this primitive is opaque.
        dependencies: A list of primitives that this primitive depends on. This
            argument is only useful for defining advanced primitives that are
            defined based on other primitives. (Default: []).

    Properties:
        * name
        * values
        * modifier
        * dependencies
        * is_modifier
        * is_material
        * is_opaque
    """
    __slots__ = ()

    pass
