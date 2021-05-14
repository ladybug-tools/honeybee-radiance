"""Radiance Spotlight Material.

http://radsite.lbl.gov/radiance/refer/ray.html#Spotlight
"""
from .materialbase import Material


# TODO: Implement the class. It's currently only a generic Radiance Primitive
class Spotlight(Material):
    """Radiance Spotlight Material.

    Spotlight is used for self-luminous surfaces having directed output. As well as
    radiance, the full cone angle (in degrees) and orientation (output direction) vector
    are given. The length of the orientation vector is the distance of the effective
    focus behind the source center (i.e., the focal length).

    .. code-block:: shell

        mod spotlight id
        0
        0
        7 red green blue angle xdir ydir zdir

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
