"""Radiance Prism1 Material.

http://radsite.lbl.gov/radiance/refer/ray.html#Prism1
"""
from .materialbase import Material


# TODO: Implement the class. It's currently only a generic Radiance Primitive
class Prism1(Material):
    """Radiance Prism1 Material.

    The prism1 material is for general light redirection from prismatic glazings,
    generating virtual light sources. It can only be used to modify a planar surface
    (i.e., a polygon or disk) and should not result in either light concentration or
    scattering. The new direction of the ray can be on either side of the material, and
    the definitions must have the correct bidirectional properties to work properly with
    virtual light sources. The arguments give the coefficient for the redirected light
    and its direction.

    .. code-block:: shell

        mod prism1 id
        5+ coef dx dy dz funcfile transform
        0
        n A1 A2 .. An

    The new direction variables dx, dy and dz need not produce a normalized vector. For
    convenience, the variables DxA, DyA and DzA are defined as the normalized direction
    to the target light source.

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
