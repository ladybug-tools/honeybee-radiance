"""Radiance Metal Material.

http://radsite.lbl.gov/radiance/refer/ray.html#Metal
"""
from __future__ import division

from .plastic import Plastic


class Metal(Plastic):
    """Radiance metal material."""

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
