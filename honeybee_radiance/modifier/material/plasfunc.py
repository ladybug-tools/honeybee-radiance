"""Radiance Plasfunc Material.

http://radsite.lbl.gov/radiance/refer/ray.html#Plasfunc
"""
from .materialbase import Material


# TODO: Implement the class. It's currently only a generic Radiance Primitive
class Plasfunc(Material):
    """Radiance Plasfunc Material.

    Plasfunc in used for the procedural definition of plastic-like materials with
    arbitrary bidirectional reflectance distribution functions (BRDF's). The arguments
    to this material include the color and specularity, as well as the function defining
    the specular distribution and the auxiliary file where it may be found.

    .. code-block:: shell

            mod plasfunc id
            2+ refl funcfile transform
            0
            4+ red green blue spec A5 ..

    The function refl takes four arguments, the x, y and z direction towards the incident
    light, and the solid angle subtended by the source. The solid angle is provided to
    facilitate averaging, and is usually ignored. The refl function should integrate to
    1 over the projected hemisphere to maintain energy balance. At least four real
    arguments must be given, and these are made available along with any additional
    values to the reflectance function. Currently, only the contribution from direct
    light sources is considered in the specular calculation. As in most material types,
    the surface normal is always altered to face the incoming ray.

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
