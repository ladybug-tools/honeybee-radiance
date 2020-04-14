"""Radiance Transdata Material.

http://radsite.lbl.gov/radiance/refer/ray.html#Transdata
"""
from .materialbase import Material


# TODO: Implement the class. It's currently only a generic Radiance Primitive
class Transdata(Material):
    """Radiance Transdata Material.

    Transdata is like plasdata but the specification includes transmittance as well as
    reflectance. The parameters are as follows.

    .. code-block:: shell

        mod transdata id
        3+n+
                func datafile
                funcfile x1 x2 .. xn transform
        0
        6+ red green blue rspec trans tspec A7 ..

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
