"""Radiance Metal Material.

http://radsite.lbl.gov/radiance/refer/ray.html#Metal
"""
from __future__ import division

from .plastic import Plastic


class Metal(Plastic):
    """Radiance metal material.

    Args:
        identifier: Text string for a unique Material ID. Must not contain spaces
            or special characters. This will be used to identify the object across
            a model and in the exported Radiance files.
        r_reflectance: Reflectance for red. The value should be between 0 and 1
            (Default: 0).
        g_reflectance: Reflectance for green. The value should be between 0 and 1
            (Default: 0).
        b_reflectance: Reflectance for blue. The value should be between 0 and 1
            (Default: 0).
        specularity: Fraction of specularity. Specularity fractions greater than 0.1
            are not realistic (Default: 0).
        roughness: Roughness is specified as the rms slope of surface facets. A
            value of 0 corresponds to a perfectly smooth surface, and a value of 1
            would be a very rough surface. Roughness values greater than 0.2 are not
            very realistic. (Default: 0).
        modifier: Material modifier (Default: "void").
        dependencies: A list of primitives that this primitive depends on. This
            argument is only useful for defining advanced primitives where the
            primitive is defined based on other primitives. (Default: [])

    Properties:
        * identifier
        * display_name
        * r_reflectance
        * g_reflectance
        * b_reflectance
        * specularity
        * roughness
        * average_reflectance
        * values
        * modifier
        * dependencies
        * is_modifier
        * is_material
    """

    __slots__ = ()

    def _update_values(self):
        "update value dictionaries."
        self._values[2] = [
            self.r_reflectance, self.g_reflectance, self.b_reflectance,
            self.specularity, self.roughness
        ]
        if self.specularity < 0.9:
            print("Warning: Specularity of metals is usually .9 or greater.")
        if self.roughness > 0.2:
            print("Warning: Roughness values above .2 is uncommon.")
