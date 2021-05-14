"""Radiance Mixdata Mixture.

http://radsite.lbl.gov/radiance/refer/ray.html#Mixdata
"""
from .mixturebase import Mixture


# TODO: Implement the class. It's currently only a generic Radiance Primitive
class Mixdata(Mixture):
    """Radiance Mixdata Material.

    Mixdata combines two modifiers using an auxiliary data file:

    .. code-block:: shell

        mod mixdata id
        5+n+
                foreground background func datafile
                funcfile x1 x2 .. xn transform
        0
        m A1 A2 .. Am

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
