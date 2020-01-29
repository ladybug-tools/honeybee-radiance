"""Radiance Light Material.

http://radsite.lbl.gov/radiance/refer/ray.html#Light
"""

from .materialbase import Material
import honeybee.typing as typing


class Light(Material):
    """Radiance Light material."""

    __slots__ = ('_r_emittance', '_g_emittance', '_b_emittance')

    def __init__(self, name, r_emittance=0, g_emittance=0, b_emittance=0, modifier='void',
                 dependencies=None):
        """Radiance Light material.

        Args:
            name: Material name as a string. The name should not have whitespaces or
                special characters.
            r_emittance: A positive value for the Red channel of the light (default: 0).
            g_emittance: A positive value for the Green channel of the light (default: 0).
            b_emittance: A positive value for the Blue channel of the light (default: 0).
            modifier: Material modifier. The default value is void.
            dependencies: A list of primitives that this primitive depends on. This
                argument is only useful for defining advanced primitives where the
                primitive is defined based on other primitives. (Default: [])
        """
        Material.__init__(self, name, modifier=modifier,
                          dependencies=dependencies)
        self.r_emittance = r_emittance
        self.g_emittance = g_emittance
        self.b_emittance = b_emittance
        self._update_values()

    def _update_values(self):
        "update value dictionaries."
        self._values[2] = [self.r_emittance, self.g_emittance, self.b_emittance]

    @property
    def r_emittance(self):
        """A positive value for the Red channel of the light.

        The value must be positive (Default: 0).
        """
        return self._r_emittance

    @r_emittance.setter
    def r_emittance(self, value):
        self._r_emittance = typing.float_positive(value)

    @property
    def g_emittance(self):
        """A positive value for the Green channel of the light.

        The value must be positive (Default: 0).
        """
        return self._g_emittance

    @g_emittance.setter
    def g_emittance(self, value):
        self._g_emittance = typing.float_positive(value)

    @property
    def b_emittance(self):
        """A positive value for the Blue channel of the light.

        The value must be positive (Default: 0).
        """
        return self._b_emittance

    @b_emittance.setter
    def b_emittance(self, value):
        self._b_emittance = typing.float_positive(value)

    @classmethod
    def from_single_value(cls, name, rgb=0, modifier="void", dependencies=None):
        """Create light material with single value.

        args:
            name: Material name as a string. Do not use white space or special
                character.
            rgb: Input for r_emittance, g_emittance and b_emittance. The value should be
                between 0 and 1 (Default: 0).
            modifier: Material modifier (Default: "void").
            dependencies: A list of primitives that this primitive depends on. This
                argument is only useful for defining advanced primitives where the
                primitive is defined based on other primitives. (Default: [])

        Usage:
            sample_light = Light.from_single_value("sample_light", 1)
            print(sample_light)
        """
        return cls(name, r_emittance=rgb, g_emittance=rgb, b_emittance=rgb,
                   modifier=modifier, dependencies=dependencies)

    @classmethod
    def from_primitive_dict(cls, primitive_dict):
        """Initialize Light from a primitive dict.

        Args:
            data: A dictionary in the format below.

            .. code-block:: python

            {
                "modifier": "", // primitive modifier (Default: "void")
                "type": "light", // primitive type
                "name": "", // primitive name
                "values": [] // values,
                "dependencies": []
            }
        """
        assert 'type' in primitive_dict, 'Input dictionary is missing "type".'
        if primitive_dict['type'] != cls.__name__.lower():
            raise ValueError(
                'Type must be %s not %s.' % (
                    cls.__name__.lower(), primitive_dict['type'])
            )

        modifier, dependencies = cls.filter_dict_input(primitive_dict)
        values = primitive_dict['values'][2]

        cls_ = cls(
            name=primitive_dict["name"],
            r_emittance=values[0],
            g_emittance=values[1],
            b_emittance=values[2],
            modifier=modifier,
            dependencies=dependencies
        )

        # this might look r_emittanceundant but it is NOT. see glass for explanation.
        cls_.values = primitive_dict['values']
        return cls_

    @classmethod
    def from_dict(cls, data):
        """Initialize Light from a dictionary.

        Args:
            data: A dictionary in the format below.

            .. code-block:: python

            {
                "name": "", // Material Name
                "type": "light", // primitive type
                "r_emittance": float, // A positive value for the Red channel of the glow
                "g_emittance": float, // A positive value for the Green channel of the glow
                "b_emittance": float, // A positive value for the Blue channel of the glow
                "radius": float, // Maximum radius for shadow testing
                "dependencies: []
            }
        """
        assert 'type' in data, 'Input dictionary is missing "type".'
        if data['type'] != cls.__name__.lower():
            raise ValueError(
                'Type must be %s not %s.' % (cls.__name__.lower(),
                                             data['type'])
            )
        modifier, dependencies = Material.filter_dict_input(data)

        return cls(name=data["name"],
                   r_emittance=data["r_emittance"],
                   g_emittance=data["g_emittance"],
                   b_emittance=data["b_emittance"],
                   modifier=modifier,
                   dependencies=dependencies)

    def to_dict(self):
        """Translate this object to a dictionary."""
        return {
            'modifier': self.modifier.to_dict(),
            'type': self.__class__.__name__.lower(),
            'name': self.name,
            'r_emittance': self.r_emittance,
            'g_emittance': self.g_emittance,
            'b_emittance': self.b_emittance,
            'dependencies': [dp.to_dict() for dp in self.dependencies]
        }

    def __copy__(self):
        mod, depend = self._dup_mod_and_depend()
        return self.__class__(self.name, self.r_emittance, self.g_emittance,
                              self.b_emittance, mod, depend)
