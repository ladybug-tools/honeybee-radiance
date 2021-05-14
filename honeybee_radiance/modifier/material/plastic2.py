"""Radiance Plastic2 Material.

http://radsite.lbl.gov/radiance/refer/ray.html#Plastic2
"""
from .materialbase import Material


# TODO: Implement the class. It's currently only a generic Radiance Primitive
class Plastic2(Material):
    """Radiance Plastic2 Material.

    Plastic2 is similar to plastic, but with anisotropic roughness. This means that
    highlights in the surface will appear elliptical rather than round. The orientation
    of the anisotropy is determined by the unnormalized direction vector ux uy uz. These
    three expressions (separated by white space) are evaluated in the context of the
    function file funcfile. If no function file is required (i.e., no special variables
    or functions are required), a period (\'.\') may be given in its place. (See the
    discussion of Function Files in the Auxiliary Files section). The urough value
    defines the roughness along the u vector given projected onto the surface. The vrough
    value defines the roughness perpendicular to this vector. Note that the highlight
    will be narrower in the direction of the smaller roughness value. Roughness values of
    zero are not allowed for efficiency reasons since the behavior would be the same as
    regular plastic in that case.

    .. code-block:: shell

        mod plastic2 id
        4+ ux uy uz funcfile transform
        0
        6 red green blue spec urough vrough

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
