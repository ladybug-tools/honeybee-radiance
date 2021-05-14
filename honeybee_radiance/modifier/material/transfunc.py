"""Radiance Transfunc Material.

http://radsite.lbl.gov/radiance/refer/ray.html#Transfunc
"""
from .materialbase import Material


# TODO: Implement the class. It's currently only a generic Radiance Primitive
class Transfunc(Material):
    """Radiance Transfunc Material.

    Transfunc is similar to plasfunc but with an arbitrary bidirectional transmittance
    distribution as well as a reflectance distribution. Both reflectance and
    transmittance are specified with the same function.

    .. code-block:: shell

        mod transfunc id
        2+ brtd funcfile transform
        0
        6+ red green blue rspec trans tspec A7 ..

    Where trans is the total light transmitted and tspec is the non-Lambertian fraction
    of transmitted light. The function brtd should integrate to 1 over each projected
    hemisphere.

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
