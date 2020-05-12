"""Radiance Glass Material.

http://radsite.lbl.gov/radiance/refer/ray.html#Glass
"""
from __future__ import division

import math
from .materialbase import Material
import honeybee.typing as typing


class Glass(Material):
    """Radiance glass material.

    Args:
        identifier: Text string for a unique Material ID. Must not contain spaces
            or special characters. This will be used to identify the object across
            a model and in the exported Radiance files.
        r_transmissivity: Transmissivity for red. The value should be between 0 and 1
            (Default: 0).
        g_transmissivity: Transmissivity for green. The value should be between 0
            and 1 (Default: 0).
        b_transmissivity: Transmissivity for blue. The value should be between 0 and
            1 (Default: 0).
        refraction_index: Index of refraction. Typical values are 1.52 for float
            glass and 1.4 for ETFE. If None, Radiance will default to using 1.52
            for glass (Default: None).
        modifier: Material modifier (Default: None).
        dependencies: A list of primitives that this primitive depends on. This
            argument is only useful for defining advanced primitives where the
            primitive is defined based on other primitives. (Default: [])

    Properties:
        * identifier
        * display_name
        * r_transmissivity
        * g_transmissivity
        * b_transmissivity
        * refraction_index
        * average_transmissivity
        * values
        * modifier
        * dependencies
        * is_modifier
        * is_material

    Usage:

    .. code-block:: python

        glass_material = Glass("generic_glass", .65, .65, .65)
        print(glass_material)
    """
    __slots__ = ('_r_transmissivity', '_g_transmissivity', '_b_transmissivity',
                 '_refraction_index')

    def __init__(self, identifier, r_transmissivity=0.0, g_transmissivity=0.0,
                 b_transmissivity=0.0, refraction_index=None, modifier=None,
                 dependencies=None):
        """Create glass material."""
        Material.__init__(self, identifier, modifier=modifier,
                          dependencies=dependencies)
        self.r_transmissivity = r_transmissivity
        self.g_transmissivity = g_transmissivity
        self.b_transmissivity = b_transmissivity
        self.refraction_index = refraction_index
        self._update_values()

    def _update_values(self):
        """Populate dictionary values."""
        if self.refraction_index:
            self._values[2] = [
                self.r_transmissivity, self.g_transmissivity, self.b_transmissivity,
                self.refraction_index
            ]
        else:
            self._values[2] = [
                self.r_transmissivity, self.g_transmissivity, self.b_transmissivity
            ]

    @property
    def r_transmissivity(self):
        """Get or set the transmissivity for red channel.

        The value should be between 0 and 1 (Default: 0).
        """
        return self._r_transmissivity

    @r_transmissivity.setter
    def r_transmissivity(self, transmissivity):
        self._r_transmissivity = \
            typing.float_in_range(transmissivity, 0, 1, 'red transmissivity')

    @property
    def g_transmissivity(self):
        """Get or set the transmissivity for green channel.

        The value should be between 0 and 1 (Default: 0).
        """
        return self._g_transmissivity

    @g_transmissivity.setter
    def g_transmissivity(self, transmissivity):
        self._g_transmissivity = \
            typing.float_in_range(transmissivity, 0, 1, 'green transmissivity')

    @property
    def b_transmissivity(self):
        """get or set the transmissivity for blue channel.

        The value should be between 0 and 1 (Default: 0).
        """
        return self._b_transmissivity

    @b_transmissivity.setter
    def b_transmissivity(self, transmissivity):
        self._b_transmissivity = \
            typing.float_in_range(transmissivity, 0, 1, 'blue transmissivity')

    @property
    def refraction_index(self):
        """Get or set the index of refraction.
        
        Typical values are 1.52 for float glass and 1.4 for ETFE. If None, Radiance
        will default to using 1.52 for glass.
        """
        return self._refraction_index

    @refraction_index.setter
    def refraction_index(self, value):
        self._refraction_index = typing.float_positive(value) if value is not None \
            else None

    @property
    def average_transmissivity(self):
        """Get the average transmissivity.

        The value is calculated by multiplying the r, g, b values by v-lambda.
        """
        return 0.265 * self.r_transmissivity + \
            0.670 * self.g_transmissivity + 0.065 * self.b_transmissivity

    @classmethod
    def from_transmittance(cls, identifier, r_transmittance=0.0, g_transmittance=0.0,
                           b_transmittance=0.0, refraction_index=None, modifier=None,
                           dependencies=None):
        """Create glass material from transmittance values.

        Radiance uses transmissivity values while glass manufactures provide the value
        for transmittance. This method does the conversion from transmittance to
        transmissivity.

        Args:
            identifier: Text string for a unique Material ID. Must not contain spaces
                or special characters. This will be used to identify the object across
                a model and in the exported Radiance files.
            r_transmittance: Transmittance for red. The value should be between 0 and 1
                (Default: 0).
            g_transmittance: Transmittance for green. The value should be between 0 and 1
                (Default: 0).
            b_transmittance: Transmittance for blue. The value should be between 0 and 1
                (Default: 0).
            refraction_index: Index of refraction. Typical values are 1.52 for float
                glass and 1.4 for ETFE. If None, Radiance will default to using 1.52
                for glass (Default: None).
            modifier: Material modifier (Default: None).
            dependencies: A list of primitives that this primitive depends on. This
                argument is only useful for defining advanced primitives where the
                primitive is defined based on other primitives. (Default: [])

        Usage:

        .. code-block:: python

            glass_material = Glass.from_transmittance("generic_glass", .60, .60, .60)
            print(glass_material)
        """
        rt = cls.get_transmissivity(r_transmittance)
        gt = cls.get_transmissivity(g_transmittance)
        bt = cls.get_transmissivity(b_transmittance)
        return cls(identifier, rt, gt, bt, refraction_index, modifier,
                   dependencies=dependencies)

    @classmethod
    def from_single_transmissivity(cls, identifier, rgb_transmissivity=0,
                                   refraction_index=None, modifier=None,
                                   dependencies=None):
        """Create glass material with single transmissivity value.

        Args:
            identifier: Text string for a unique Material ID. Must not contain spaces
                or special characters. This will be used to identify the object across
                a model and in the exported Radiance files.
            rgb_transmissivity: Transmissivity for red, green and blue. The value should
                be between 0 and 1 (Default: 0).
            refraction_index: Index of refraction. Typical values are 1.52 for float
                glass and 1.4 for ETFE. If None, Radiance will default to using 1.52
                for glass (Default: None).
            modifier: Material modifier (Default: None).
            dependencies: A list of primitives that this primitive depends on. This
                argument is only useful for defining advanced primitives where the
                primitive is defined based on other primitives. (Default: [])

        Usage:

        .. code-block:: python

            glassMaterial = Glass.from_single_transmissivity("generic glass", .65)
            print(glassMaterial)
        """
        return cls(
            identifier, r_transmissivity=rgb_transmissivity,
            g_transmissivity=rgb_transmissivity, b_transmissivity=rgb_transmissivity,
            refraction_index=refraction_index,
            modifier=modifier, dependencies=dependencies)

    @classmethod
    def from_single_transmittance(cls, identifier, rgb_transmittance=0,
                                  refraction_index=None, modifier=None,
                                  dependencies=None):
        """Create glass material with single transmittance value.

        Args:
            identifier: Text string for a unique Material ID. Must not contain spaces
                or special characters. This will be used to identify the object across
                a model and in the exported Radiance files.
            rgb_transmittance: Transmittance for red, green and blue. The value should
                be between 0 and 1 (Default: 0).
            refraction_index: Index of refraction. Typical values are 1.52 for float
                glass and 1.4 for ETFE. If None, Radiance will default to using 1.52
                for glass (Default: None).
            modifier: Material modifier (Default: None).
            dependencies: A list of primitives that this primitive depends on. This
                argument is only useful for defining advanced primitives where the
                primitive is defined based on other primitives. (Default: [])

        Usage:

        .. code-block:: python

            glassMaterial = Glass.from_single_transmittance("generic glass", .65)
            print(glassMaterial)
        """
        rgb_transmissivity = cls.get_transmissivity(rgb_transmittance)
        return cls(
            identifier,
            r_transmissivity=rgb_transmissivity, g_transmissivity=rgb_transmissivity,
            b_transmissivity=rgb_transmissivity, refraction_index=refraction_index,
            modifier=modifier, dependencies=dependencies)

    @classmethod
    def from_primitive_dict(cls, primitive_dict):
        """Initialize Glass from a primitive dict.

        Args:
            data: A dictionary in the format below.

        .. code-block:: python

            {
            "modifier": {},  # primitive modifier (Default: None)
            "type": "glass",  # primitive type
            "identifier": "",  # primitive identifier
            "display_name": "",  # primitive display name
            "values": [] , # values
            "dependencies": []
            }
        """
        assert 'type' in primitive_dict, 'Input dictionary is missing "type".'
        if primitive_dict['type'] != 'glass':
            raise ValueError('Type must be glass not %s.' % primitive_dict['type'])

        modifier, dependencies = cls.filter_dict_input(primitive_dict)
        values = primitive_dict['values'][2]
        refraction_index = values[3] if len(values) == 4 else None
        cls_ = cls(
            identifier=primitive_dict['identifier'],
            r_transmissivity=values[0],
            g_transmissivity=values[1],
            b_transmissivity=values[2],
            refraction_index=refraction_index,
            modifier=modifier,
            dependencies=dependencies)
        if 'display_name' in primitive_dict and primitive_dict['display_name'] is not None:
            cls_.display_name = primitive_dict['display_name']

        # update the values from values dictionary.
        # this might look redundant but it is to ensure any strange input like inputs in
        # strings line are updated and will be the same as input in cases that user uses
        # from_string classmethod
        cls_.values = primitive_dict['values']
        return cls_

    @classmethod
    def from_dict(cls, data):
        """Initialize Glass from a dictionary.

        Args:
            data: A dictionary in the format below.

        .. code-block:: python

            {
            "type": "glass",
            "identifier": "",  # Material identifier
            "display_name": string  # Material display name
            "r_transmissivity": float,  # Transmissivity for red
            "g_transmissivity": float,  # Transmissivity for green
            "b_transmissivity": float,  # Transmissivity for blue
            "refraction_index": float,  # Index of refraction
            "modifier": {},  # material modifier (Default: None)
            "dependencies": []
            }
        """
        assert 'type' in data, 'Input dictionary is missing "type".'
        if data['type'] != 'glass':
            raise ValueError('Type must be glass not %s.' % data['type'])

        modifier, dependencies = Material.filter_dict_input(data)

        new_obj = cls(identifier=data["identifier"],
                      r_transmissivity=data["r_transmissivity"],
                      g_transmissivity=data["g_transmissivity"],
                      b_transmissivity=data["b_transmissivity"],
                      refraction_index=data["refraction_index"],
                      modifier=modifier,
                      dependencies=dependencies)
        if 'display_name' in data and data['display_name'] is not None:
            new_obj.display_name = data['display_name']
        return new_obj

    def to_dict(self):
        """Translate this object to a dictionary."""
        base = {
            "modifier": self.modifier.to_dict(),
            "type": "glass",
            "identifier": self.identifier,
            "r_transmissivity": self.r_transmissivity,
            "g_transmissivity": self.g_transmissivity,
            "b_transmissivity": self.b_transmissivity,
            "refraction_index": self.refraction_index,
            "dependencies": [dp.to_dict() for dp in self.dependencies]
        }
        if self._display_name is not None:
            base['display_name'] = self.display_name
        return base

    @staticmethod
    def get_transmissivity(transmittance):
        """Calculate transmissivity based on transmittance value.

        "Transmissivity is the amount of light not absorbed in one traversal of
        the material. Transmittance -- the value usually measured - is the total
        light transmitted through the pane including multiple reflections."
        """
        transmittance = float(transmittance)
        if transmittance == 0:
            return 0
        return (math.sqrt(0.8402528435 + 0.0072522239 * (transmittance ** 2)) -
                0.9166530661) / 0.0036261119 / transmittance

    def __copy__(self):
        mod, depend = self._dup_mod_and_depend()
        new_obj = self.__class__(
            self.identifier, self.r_transmissivity, self.g_transmissivity,
            self.b_transmissivity, self.refraction_index, mod, depend)
        new_obj._display_name = self._display_name
        return new_obj
