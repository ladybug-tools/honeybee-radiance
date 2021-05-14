"""Radiance Metfunc Material.

http://radsite.lbl.gov/radiance/refer/ray.html#Metfunc
"""
from .materialbase import Material


# TODO: Implement the class. It's currently only a generic Radiance Primitive
class Metfunc(Material):
    """Radiance Metfunc Material.

    Metfunc is identical to plasfunc and takes the same arguments, but the specular
    component is multiplied also by the material color.

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
