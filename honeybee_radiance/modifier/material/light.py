"""Radiance Light Material.

http://radsite.lbl.gov/radiance/refer/ray.html#Light
"""

from .materialbase import Material
import honeybee.typing as typing


class Light(Material):
    """Radiance Light material.

    Args:
        identifier: Text string for a unique Material ID. Must not contain spaces
            or special characters. This will be used to identify the object across
            a model and in the exported Radiance files.
        r_emittance: A positive value for the Red channel of the light (Default: 0).
        g_emittance: A positive value for the Green channel of the light (Default: 0).
        b_emittance: A positive value for the Blue channel of the light (Default: 0).
        modifier: Material modifier. (Default: None).
        dependencies: A list of primitives that this primitive depends on. This
            argument is only useful for defining advanced primitives where the
            primitive is defined based on other primitives. (Default: [])

    Properties:
        * identifier
        * display_name
        * r_emittance
        * g_emittance
        * b_emittance
        * values
        * modifier
        * dependencies
        * is_modifier
        * is_material
    """

    __slots__ = ('_r_emittance', '_g_emittance', '_b_emittance')

    def __init__(self, identifier, r_emittance=0, g_emittance=0, b_emittance=0,
                 modifier=None, dependencies=None):
        """Radiance Light material."""
        Material.__init__(self, identifier, modifier=modifier,
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
    def from_single_value(cls, identifier, rgb=0, modifier=None, dependencies=None):
        """Create light material with single value.

        Args:
            identifier: Text string for a unique Material ID. Must not contain spaces
                or special characters. This will be used to identify the object across
                a model and in the exported Radiance files.
            rgb: Input for r_emittance, g_emittance and b_emittance. The value should be
                between 0 and 1 (Default: 0).
            modifier: Material modifier (Default: None).
            dependencies: A list of primitives that this primitive depends on. This
                argument is only useful for defining advanced primitives where the
                primitive is defined based on other primitives. (Default: [])

        Usage:

        .. code-block:: python

            sample_light = Light.from_single_value("sample_light", 1)
            print(sample_light)
        """
        return cls(identifier, r_emittance=rgb, g_emittance=rgb, b_emittance=rgb,
                   modifier=modifier, dependencies=dependencies)

    @classmethod
    def from_primitive_dict(cls, primitive_dict):
        """Initialize Light from a primitive dict.

        Args:
            data: A dictionary in the format below.

        .. code-block:: python

            {
            "modifier": {}  # primitive modifier (Default: None)
            "type": "light",  # primitive type
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
            modifier=modifier,
            dependencies=dependencies
        )
        if 'display_name' in primitive_dict and \
                primitive_dict['display_name'] is not None:
            cls_.display_name = primitive_dict['display_name']

        # this might look redundant but it is NOT. see glass for explanation.
        cls_.values = primitive_dict['values']
        return cls_

    @classmethod
    def from_dict(cls, data):
        """Initialize Light from a dictionary.

        Args:
            data: A dictionary in the format below.

        .. code-block:: python

            {
            "type": "Light",  # primitive type
            "identifier": "",  # Material identifier
            "display_name": ""  # Material display name
            "r_emittance": float,  # A positive value for the Red channel of the glow
            "g_emittance": float,  # A positive value for the Green channel of the glow
            "b_emittance": float,  # A positive value for the Blue channel of the glow
            "radius": float,  # Maximum radius for shadow testing
            "dependencies: []
            }
        """
        cls._dict_type_check(cls.__name__, data)
        modifier, dependencies = cls.filter_dict_input(data)

        new_obj = cls(identifier=data["identifier"],
                      r_emittance=data["r_emittance"],
                      g_emittance=data["g_emittance"],
                      b_emittance=data["b_emittance"],
                      modifier=modifier,
                      dependencies=dependencies)
        if 'display_name' in data and data['display_name'] is not None:
            new_obj.display_name = data['display_name']
        return new_obj

    def to_dict(self):
        """Translate this object to a dictionary."""
        base = {
            'modifier': self.modifier.to_dict(),
            'type': 'Light',
            'identifier': self.identifier,
            'r_emittance': self.r_emittance,
            'g_emittance': self.g_emittance,
            'b_emittance': self.b_emittance,
            'dependencies': [dp.to_dict() for dp in self.dependencies]
        }
        if self._display_name is not None:
            base['display_name'] = self.display_name
        return base

    def __copy__(self):
        mod, depend = self._dup_mod_and_depend()
        new_obj = self.__class__(self.identifier, self.r_emittance, self.g_emittance,
                                 self.b_emittance, mod, depend)
        new_obj._display_name = self._display_name
        return new_obj
