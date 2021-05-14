"""Radiance Antimatter Material.

http://radsite.lbl.gov/radiance/refer/ray.html#Antimatter
"""
from .materialbase import Material


# TODO: Implement the class. It's currently only a generic Radiance Primitive
class Antimatter(Material):
    """Radiance Antimatter Material.

    Antimatter is a material that can \'subtract\' volumes from other volumes. A ray
    passing into an antimatter object becomes blind to all the specified modifiers:

    .. code-block:: shell

        mod antimatter id
        N mod1 mod2 .. modN
        0
        0

    The first modifier will also be used to shade the area leaving the antimatter volume
    and entering the regular volume. If mod1 is void, the antimatter volume is completely
    invisible. Antimatter does not work properly with the material type "trans", and
    multiple antimatter surfaces should be disjoint. The viewpoint must be outside all
    volumes concerned for a correct rendering.

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
