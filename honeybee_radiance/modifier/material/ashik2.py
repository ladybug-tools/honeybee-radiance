"""Radiance Ashik2 Material.

http://radsite.lbl.gov/radiance/refer/ray.html#Ashik2
"""
from .materialbase import Material


# TODO: Implement the class. It's currently only a generic Radiance Primitive
class Ashik2(Material):
    """Radiance Ashik2 Material.

    Ashik2 is the anisotropic reflectance model by Ashikhmin & Shirley. The string
    arguments are the same as for plastic2, but the real arguments have additional
    flexibility to specify the specular color. Also, rather than roughness, specular
    power is used, which has no physical meaning other than larger numbers are equivalent
    to a smoother surface.

    .. code-block:: shell

        mod ashik2 id
        4+ ux uy uz funcfile transform
        0
        8 dred dgrn dblu sred sgrn sblu u-power v-power

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
