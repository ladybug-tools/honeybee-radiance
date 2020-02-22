"""Radiance Metdata Material.

http://radsite.lbl.gov/radiance/refer/ray.html#Metdata
"""
from .materialbase import Material


# TODO: Implement the class. It's currently only a generic Radiance Primitive
class Metdata(Material):
    """Radiance Metdata Material.

    As metfunc is to plasfunc, metdata is to plasdata. Metdata takes the same arguments
    as plasdata, but the specular component is modified by the given material color.

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
