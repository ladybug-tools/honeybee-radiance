"""Radiance Dielectric Material.

http://radsite.lbl.gov/radiance/refer/ray.html#Dielectric
"""
from .materialbase import Material


# TODO: Implement the class. It's currently only a generic Radiance Primitive
class Dielectric(Material):
    """Radiance Dielectric Material.

    A dielectric material is transparent, and it refracts light as well as reflecting it.
    Its behavior is determined by the index of refraction and transmission coefficient in
    each wavelength band per unit length. Common glass has a index of refraction (n)
    around 1.5, and a transmission coefficient of roughly 0.92 over an inch. An
    additional number, the Hartmann constant, describes how the index of refraction
    changes as a function of wavelength. It is usually zero. (A pattern modifies only the
    refracted value.)

    .. code-block:: shell

        mod dielectric id
        0
        0
        5 rtn gtn btn n hc

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
