"""Radiance Glow Material.

http://radsite.lbl.gov/radiance/refer/ray.html#Glow
"""
from __future__ import division

from .materialbase import Material
import honeybee.typing as typing


class Glow(Material):
    """Create glow material.

    Args:
        identifier: Text string for a unique Material ID. Must not contain spaces
            or special characters. This will be used to identify the object across
            a model and in the exported Radiance files.
        r_emittance: A positive value for the Red channel of the glow (default: 0).
        g_emittance: A positive value for the Green channel of the glow (default: 0).
        b_emittance: A positive value for the Blue channel of the glow (default: 0).
        max_radius: Maximum radius for shadow testing (default: 0). If maxrad is
            zero, then the surface will never be tested for shadow, although it may
            participate in an interreflection calculation. If maxrad is negative,
            then the surface will never contribute to scene illumination. Glow
            sources will never illuminate objects on the other side of an illum
            surface. This provides a convenient way to illuminate local light fixture
            geometry without overlighting nearby objects.
        modifier: Material modifier (Default: None).
        dependencies: A list of primitives that this primitive depends on. This
            argument is only useful for defining advanced primitives where the
            primitive is defined based on other primitives. (Default: [])

    Properties:
        * identifier
        * display_name
        * r_emittance
        * g_emittance
        * b_emittance
        * max_radius
        * values
        * modifier
        * dependencies
        * is_modifier
        * is_material
    """

    __slots__ = ('_r_emittance', '_g_emittance', '_b_emittance', '_max_radius')

    def __init__(self, identifier, r_emittance=0.0, g_emittance=0.0, b_emittance=0.0,
                 max_radius=0.0, modifier=None, dependencies=None):
        """Init Glow material."""
        Material.__init__(self, identifier, modifier=modifier,
                          dependencies=dependencies)
        self.r_emittance = r_emittance
        self.g_emittance = g_emittance
        self.b_emittance = b_emittance
        self.max_radius = max_radius
        self._update_values()

    def _update_values(self):
        "update value dictionaries."
        self._values[2] = [
            self.r_emittance, self.g_emittance, self.b_emittance, self.max_radius
        ]

    @property
    def r_emittance(self):
        """Get or set a positive value for the Red channel of the glow.

        The value must be positive (Default: 0).
        """
        return self._r_emittance

    @r_emittance.setter
    def r_emittance(self, value):
        self._r_emittance = typing.float_positive(value)

    @property
    def g_emittance(self):
        """Get or set a positive value for the Green channel of the glow.

        The value must be positive (Default: 0).
        """
        return self._g_emittance

    @g_emittance.setter
    def g_emittance(self, value):
        self._g_emittance = typing.float_positive(value)

    @property
    def b_emittance(self):
        """Get or set a positive value for the Blue channel of the glow.

        The value must be positive (Default: 0).
        """
        return self._b_emittance

    @b_emittance.setter
    def b_emittance(self, value):
        self._b_emittance = typing.float_positive(value)

    @property
    def max_radius(self):
        """Get or set the maximum radius for shadow testing. (Default: 0).

        If maxrad is zero, then the surface will never be tested for shadow, although
        it may participate in an interreflection calculation. If maxrad is negative, then
        the surface will never contribute to scene illumination. Glow sources will
        never illuminate objects on the other side of an illum surface. This
        provides a convenient way to illuminate local light fixture geometry without
        overlighting nearby objects.
        """
        return self._max_radius

    @max_radius.setter
    def max_radius(self, value):
        self._max_radius = float(value)

    @classmethod
    def from_single_value(cls, identifier, rgb=0, max_radius=0, modifier=None,
                          dependencies=None):
        """Create glow material with single value.

        Args:
            identifier: Text string for a unique Material ID. Must not contain spaces
            or special characters. This will be used to identify the object across
            a model and in the exported Radiance files.
            rgb: Input for r_emittance, g_emittance and b_emittance. The value should be
                between 0 and 1 (Default: 0).
            modifier: Material modifier (Default: None).
            max_radius: Maximum radius for shadow testing (default: 0). If maxrad is zero,
                then the surface will never be tested for shadow, although it may
                participate in an interreflection calculation. If maxrad is negative, then
                the surface will never contribute to scene illumination. Glow sources will
                never illuminate objects on the other side of an illum surface. This
                provides a convenient way to illuminate local light fixture geometry without
                overlighting nearby objects.
            dependencies: A list of primitives that this primitive depends on. This
                argument is only useful for defining advanced primitives where the
                primitive is defined based on other primitives. (Default: [])

        Usage:

        .. code-block:: python

            sample_glow = Glow.from_single_value("sample_glow", 100)
            print(sample_glow)
        """
        return cls(identifier, r_emittance=rgb, g_emittance=rgb, b_emittance=rgb,
            max_radius=max_radius, modifier=modifier, dependencies=dependencies)

    @classmethod
    def from_primitive_dict(cls, primitive_dict):
        """Initialize Glow from a primitive dict.

        Args:
            data: A dictionary in the format below.

        .. code-block:: python

            {
            "modifier": {}  # primitive modifier (Default: None)
            "type": "glow",  # primitive type
            "identifier": "",  # primitive identifier
            "display_name": "",  # primitive display name
            "values": [],  # values
            "dependencies": []
            }
        """
        cls._dict_type_check(cls.__name__, primitive_dict)
        modifier, dependencies = cls.filter_dict_input(primitive_dict)
        values = primitive_dict['values'][2]

        cls_ = cls(
            identifier=primitive_dict["identifier"],
            r_emittance=values[0],
            g_emittance=values[1],
            b_emittance=values[2],
            max_radius=values[3],
            modifier=modifier,
            dependencies=dependencies
        )
        if 'display_name' in primitive_dict and primitive_dict['display_name'] is not None:
            cls_.display_name = primitive_dict['display_name']

        # this might look redundant but it is NOT. see glass for explanation.
        cls_.values = primitive_dict['values']
        return cls_

    @classmethod
    def from_dict(cls, data):
        """Initialize Glow from a dictionary.

        Args:
            data: A dictionary in the format below.

        .. code-block:: python

            {
            "type": "Glow",  # primitive type
            "identifier": "",  # Material identifier
            "display_name": "",  # Material display name
            "r_emittance": float,  # A positive value for the Red channel of the glow
            "g_emittance": float,  # A positive value for the Green channel of the glow
            "b_emittance": float,  # A positive value for the Blue channel of the glow
            "max_radius": float,  # Maximum radius for shadow testing
            "modifier": {}  # primitive modifier (Default: None)
            "dependencies: []
            }
        """
        cls._dict_type_check(cls.__name__, data)
        modifier, dependencies = cls.filter_dict_input(data)

        new_obj = cls(identifier=data['identifier'],
                      r_emittance=data['r_emittance'],
                      g_emittance=data['g_emittance'],
                      b_emittance=data['b_emittance'],
                      max_radius=data['max_radius'],
                      modifier=modifier,
                      dependencies=dependencies)
        if 'display_name' in data and data['display_name'] is not None:
            new_obj.display_name = data['display_name']
        return new_obj

    def to_dict(self):
        """Translate this object to a dictionary."""
        base = {
            'modifier': self.modifier.to_dict(),
            'type': 'Glow',
            'identifier': self.identifier,
            'r_emittance': self.r_emittance,
            'g_emittance': self.g_emittance,
            'b_emittance': self.b_emittance,
            'max_radius': self.max_radius,
            'dependencies': [dp.to_dict() for dp in self.dependencies]
        }
        if self._display_name is not None:
            base['display_name'] = self.display_name
        return base

    def __copy__(self):
        mod, depend = self._dup_mod_and_depend()
        new_obj = self.__class__(self.identifier, self.r_emittance, self.g_emittance,
                                 self.b_emittance, self.max_radius, mod, depend)
        new_obj._display_name = self._display_name
        return new_obj
