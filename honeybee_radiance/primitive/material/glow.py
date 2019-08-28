"""Radiance Glow Material.

http://radsite.lbl.gov/radiance/refer/ray.html#Glow
"""

from .materialbase import Material
import honeybee.typing as typing


class Glow(Material):
    """Create glow material."""

    def __init__(self, name, r_emittance=0.0, g_emittance=0.0, b_emittance=0.0,
                 max_radius=0.0, modifier='void', dependencies=None):
        """Init Glow material.

        args:
            name: Material name as a string. The name should not have whitespaces or
                special characters.
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
            dependencies: A list of primitives that this primitive depends on. This
                argument is only useful for defining advanced primitives where the
                primitive is defined based on other primitives. (Default: [])
        """
        Material.__init__(self, name, modifier=modifier,
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
        """A positive value for the Red channel of the glow.

        The value must be positive (Default: 0).
        """
        return self._r_emittance

    @r_emittance.setter
    def r_emittance(self, value):
        self._r_emittance = typing.float_positive(value)

    @property
    def g_emittance(self):
        """A positive value for the Green channel of the glow.

        The value must be positive (Default: 0).
        """
        return self._g_emittance

    @g_emittance.setter
    def g_emittance(self, value):
        self._g_emittance = typing.float_positive(value)

    @property
    def b_emittance(self):
        """A positive value for the Blue channel of the glow.

        The value must be positive (Default: 0).
        """
        return self._b_emittance

    @b_emittance.setter
    def b_emittance(self, value):
        self._b_emittance = typing.float_positive(value)

    @property
    def max_radius(self):
        """Maximum radius for shadow testing (default: 0).

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
    def from_values(cls, values_dict):
        """Make a radiance primitive from value dict.

        {
            "modifier": "", // primitive modifier (Default: "void")
            "type": "glow", // primitive type
            "name": "", // primitive Name
            "values": {} // values,
            "dependencies": []
        }
        """
        assert 'type' in values_dict, 'Input dictionary is missing "type".'
        if values_dict['type'] != cls.__name__.lower():
            raise ValueError(
                'Type must be %s not %s.' % (
                    cls.__name__.lower(), values_dict['type'])
            )

        modifier, dependencies = cls.filter_dict_input(values_dict)
        values = values_dict['values'][2]

        cls_ = cls(
            name=values_dict["name"],
            r_emittance=values[0],
            g_emittance=values[1],
            b_emittance=values[2],
            max_radius=values[3],
            modifier=modifier,
            dependencies=dependencies
        )

        # this might look r_emittanceundant but it is NOT. see glass for explanation.
        cls_.values = values_dict['values']
        return cls_

    @classmethod
    def from_dict(cls, input_dict):
        """Make radiance material from dict
        {
            "name": "", // Material Name
            "type": "glow", // primitive type
            "r_emittance": float, // A positive value for the Red channel of the glow
            "g_emittance": float, // A positive value for the Green channel of the glow
            "b_emittance": float, // A positive value for the Blue channel of the glow
            "max_radius": float, // Maximum radius for shadow testing
            "dependencies: []
        }
        """
        assert 'type' in input_dict, 'Input dictionary is missing "type".'
        if input_dict['type'] != cls.__name__.lower():
            raise ValueError(
                'Type must be %s not %s.' % (cls.__name__.lower(),
                                             input_dict['type'])
            )
        modifier, dependencies = Material.filter_dict_input(input_dict)

        return cls(name=input_dict['name'],
                   r_emittance=input_dict['r_emittance'],
                   g_emittance=input_dict['g_emittance'],
                   b_emittance=input_dict['b_emittance'],
                   max_radius=input_dict['max_radius'],
                   modifier=modifier,
                   dependencies=dependencies)

    @classmethod
    def from_single_value(cls, name, rgb=0, max_radius=0, modifier='void',
                          dependencies=None):
        """Create glow material with single value.

        args:
            name: Material name as a string. Do not use white space or special
                character.
            rgb: Input for r_emittance, g_emittance and b_emittance. The value should be
                between 0 and 1 (Default: 0).
            modifier: Material modifier (Default: "void").
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
            sample_glow = Glow.from_single_value("sample_glow", 100)
            print(sample_glow)
        """
        return cls(name, r_emittance=rgb, g_emittance=rgb, b_emittance=rgb,
            max_radius=max_radius, modifier=modifier, dependencies=dependencies)

    def to_dict(self):
        """Translate radiance material to dict
        {
            "modifier": modifier,
            "type": "glow", // Material type
            "name": "", // Material Name
            "r_emittance": float, // A positive value for the Red channel of the glow
            "g_emittance": float, // A positive value for the Green channel of the glow
            "b_emittance": float, // A positive value for the Blue channel of the glow
            "dependencies": []
        }
        """
        return {
            'modifier': self.modifier.to_dict(),
            'type': self.__class__.__name__.lower(),
            'name': self.name,
            'r_emittance': self.r_emittance,
            'g_emittance': self.g_emittance,
            'b_emittance': self.b_emittance,
            'max_radius': self.max_radius,
            'dependencies': [dp.to_dict() for dp in self.dependencies]
        }


class WhiteGlow(Glow):
    """A white glow material.

    Use this material for multi-phase daylight studies.
    """

    def __init__(self, name='white_glow'):
        """Create glow material."""
        Glow.__init__(self, name, 1.0, 1.0, 1.0, 0.0)
