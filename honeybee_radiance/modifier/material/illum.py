"""Radiance Illum Material.

http://radsite.lbl.gov/radiance/refer/ray.html#Illum
"""
from .materialbase import Material


# TODO: Implement the class. It's currently only a generic Radiance Primitive
class Illum(Material):
    """Radiance Illum Material.

    Illum is used for secondary light sources with broad distributions. A secondary light
    source is treated like any other light source, except when viewed directly. It then
    acts like it is made of a different material (indicated by the string argument), or
    becomes invisible (if no string argument is given, or the argument is "void").
    Secondary sources are useful when modeling windows or brightly illuminated surfaces.

    .. code-block:: shell

        mod illum id
        1 material
        0
        3 red green blue

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
