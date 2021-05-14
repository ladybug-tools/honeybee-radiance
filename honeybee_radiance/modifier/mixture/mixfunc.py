"""Radiance Mixfunc Mixture.

http://radsite.lbl.gov/radiance/refer/ray.html#Mixfunc
"""
from .mixturebase import Mixture


# TODO: Implement the class. It's currently only a generic Radiance Primitive
class Mixfunc(Mixture):
    """Radiance Mixfunc Material.

    A mixfunc mixes two modifiers procedurally. It is specified as follows:

    .. code-block:: shell

        mod mixfunc id
        4+ foreground background vname funcfile transform
        0
        n A1 A2 .. An

    Foreground and background are modifier names that must be defined earlier in the
    scene description. If one of these is a material, then the modifier of the mixfunc
    must be "void". (Either the foreground or background modifier may be "void", which
    serves as a form of opacity control when used with a material.) Vname is the
    coefficient defined in funcfile that determines the influence of foreground. The
    background coefficient is always (1-vname).

    Args:
        identifier: Text string for a unique Mixture ID. Must not contain spaces
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
