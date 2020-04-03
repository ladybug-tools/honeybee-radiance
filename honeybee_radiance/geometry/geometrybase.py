"""Base Radiance Geometry class (e.g polygon, sphere, source, etc.).

Radiance supports a number of native geometry primitives. The one that is most
commonly used to represent planar geometry is a Polygon but many of the other
geometry primitives can be used to specify simple types of curved geometry with
a fraction of the file size, memory, and computational power needed to support
a planar approximation of curved geometry. More information on Radiance geometry
Primitives can be found at:

https://floyd.lbl.gov/radiance/refer/ray.html#Surfaces
"""
from ..primitive import Primitive


class Geometry(Primitive):
    """Base class for Radiance geometries.

    Properties:
        * identifier
        * display_name
        * values
        * modifier
        * dependencies
        * is_geometry
        * is_modifier
        * is_material
        * is_texture
        * is_pattern
        * is_mixture
        * is_opaque
"""
    __slots__ = ()

    @property
    def is_geometry(self):
        """Get a boolean noting whether this object is a Radiance geometry."""
        return True
