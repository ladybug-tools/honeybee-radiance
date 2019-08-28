"""Radiance Glass Material.

http://radsite.lbl.gov/radiance/refer/ray.html#Glass
"""
import math
from .materialbase import Material
import honeybee.typing as typing


class Glass(Material):
    """Radiance glass material."""

    def __init__(self, name, r_transmissivity=0.0, g_transmissivity=0.0,
                 b_transmissivity=0.0, refraction_index=None, modifier="void",
                 dependencies=None
                 ):
        """Create glass material.

        args:
            name: Material name as a string. Do not use white space or special character
            r_transmissivity: Transmissivity for red. The value should be between 0 and 1
                (Default: 0).
            g_transmissivity: Transmissivity for green. The value should be between 0
                and 1 (Default: 0).
            b_transmissivity: Transmissivity for blue. The value should be between 0 and
                1 (Default: 0).
            refraction: Index of refraction. 1.52 for glass and 1.4 for ETFE
                (Default: 1.52).
            modifier: Material modifier (Default: "void").
            dependencies: A list of primitives that this primitive depends on. This
                argument is only useful for defining advanced primitives where the
                primitive is defined based on other primitives. (Default: [])

        Usage:

            glass_material = Glass("generic_glass", .65, .65, .65)
            print(glass_material)
        """
        Material.__init__(self, name, modifier=modifier,
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
        """Transmissivity for red channel.

        The value should be between 0 and 1 (Default: 0).
        """
        return self._r_transmissivity

    @r_transmissivity.setter
    def r_transmissivity(self, transmissivity):
        self._r_transmissivity = \
            typing.float_in_range(transmissivity, 0, 1, 'red transmissivity')

    @property
    def g_transmissivity(self):
        """Transmissivity for green channel.

        The value should be between 0 and 1 (Default: 0).
        """
        return self._g_transmissivity

    @g_transmissivity.setter
    def g_transmissivity(self, transmissivity):
        self._g_transmissivity = \
            typing.float_in_range(transmissivity, 0, 1, 'green transmissivity')

    @property
    def b_transmissivity(self):
        """Transmissivity for blue channel.

        The value should be between 0 and 1 (Default: 0).
        """
        return self._b_transmissivity

    @b_transmissivity.setter
    def b_transmissivity(self, transmissivity):
        self._b_transmissivity = \
            typing.float_in_range(transmissivity, 0, 1, 'blue transmissivity')

    @property
    def refraction_index(self):
        """Index of refraction. 1.52 for glass and 1.4 for ETFE (Default: 1.52)."""
        return self._refraction_index

    @refraction_index.setter
    def refraction_index(self, value):
        self._refraction_index = typing.float_positive(value) if value is not None \
             else None

    @property
    def average_transmissivity(self):
        """Calculate average transmittance.

        The value is calculated by multiplying the r, g, b values by v-lambda.
        """
        return 0.265 * self.r_transmissivity + \
            0.670 * self.g_transmissivity + 0.065 * self.b_transmissivity

    @classmethod
    def from_transmittance(cls, name, r_transmittance=0.0, g_transmittance=0.0,
                           b_transmittance=0.0, refraction_index=None, modifier="void",
                           dependencies=None):
        """Create glass material from transmittance values.

        Radiance uses transmissivity values while glass manufactures provide the value
        for transmittance. This method does the conversion from transmittance to
        transmissivity.

        args:
            name: Material name as a string. Do not use white space or special character
            r_transmittance: Transmittance for red. The value should be between 0 and 1
                (Default: 0).
            g_transmittance: Transmittance for green. The value should be between 0 and 1
                (Default: 0).
            b_transmittance: Transmittance for blue. The value should be between 0 and 1
                (Default: 0).
            refraction: Index of refraction. 1.52 for glass and 1.4 for ETFE
                (Default: 1.52).
            modifier: Material modifier (Default: "void").
            dependencies: A list of primitives that this primitive depends on. This
                argument is only useful for defining advanced primitives where the
                primitive is defined based on other primitives. (Default: [])

        Usage:

            glass_material = Glass.from_transmittance("generic_glass", .60, .60, .60)
            print(glass_material)
        """
        rt = cls.get_transmissivity(r_transmittance)
        gt = cls.get_transmissivity(g_transmittance)
        bt = cls.get_transmissivity(b_transmittance)
        return cls(name, rt, gt, bt, refraction_index, modifier, dependencies=dependencies)

    @classmethod
    def from_single_transmissivity(cls, name, rgb_transmissivity=0,
                                   refraction_index=None, modifier="void",
                                   dependencies=None):
        """Create glass material with single transmissivity value.

        Attributes:
            name: Material name as a string. Do not use white space or special
                character.
            rgb_transmissivity: Transmissivity for red, green and blue. The value should
                be between 0 and 1 (Default: 0).
            refraction: Index of refraction. 1.52 for glass and 1.4 for ETFE
                (Default: 1.52).
            modifier: Material modifier (Default: "void").
            dependencies: A list of primitives that this primitive depends on. This
                argument is only useful for defining advanced primitives where the
                primitive is defined based on other primitives. (Default: [])            

        Usage:
            glassMaterial = Glass.by_single_trans_value("generic glass", .65)
            print(glassMaterial)
        """
        return cls(
            name, r_transmissivity=rgb_transmissivity, g_transmissivity=rgb_transmissivity,
            b_transmissivity=rgb_transmissivity, refraction_index=refraction_index,
            modifier=modifier, dependencies=dependencies)

    @classmethod
    def from_single_transmittance(cls, name, rgb_transmittance=0,
                                  refraction_index=None, modifier="void", dependencies=None):
        """Create glass material with single transmittance value.

        Attributes:
            name: Material name as a string. Do not use white space or special
                character.
            rgb_transmissivity: Transmissivity for red, green and blue. The value should
                be between 0 and 1 (Default: 0).
            refraction: Index of refraction. 1.52 for glass and 1.4 for ETFE
                (Default: 1.52).
            modifier: Material modifier (Default: "void").
            dependencies: A list of primitives that this primitive depends on. This
                argument is only useful for defining advanced primitives where the
                primitive is defined based on other primitives. (Default: [])

        Usage:
            glassMaterial = Glass.by_single_trans_value("generic glass", .65)
            print(glassMaterial)
        """
        rgb_transmissivity = cls.get_transmissivity(rgb_transmittance)
        return cls(
            name,
            r_transmissivity=rgb_transmissivity, g_transmissivity=rgb_transmissivity,
            b_transmissivity=rgb_transmissivity, refraction_index=refraction_index,
            modifier=modifier, dependencies=dependencies)

    @classmethod
    def from_values(cls, values_dict):
        """Make a radiance primitive from value dict.

        {
            "modifier": "", // primitive modifier (Default: "void")
            "type": "", // primitive type
            "name": "", // primitive Name
            "values": {} // values,
            "dependencies": []
        }
        """
        assert 'type' in values_dict, 'Input dictionary is missing "type".'
        if values_dict['type'] != 'glass':
            raise ValueError('Type must be glass not %s.' % values_dict['type'])

        modifier, dependencies = cls.filter_dict_input(values_dict)
        values = values_dict['values'][2]
        refraction_index = values[3] if len(values) == 4 else None
        cls_ = cls(
            name=values_dict['name'],
            r_transmissivity=values[0],
            g_transmissivity=values[1],
            b_transmissivity=values[2],
            refraction_index=refraction_index,
            modifier=modifier,
            dependencies=dependencies)
        # update the values from values dictionary.
        # this might look redundant but it is to ensure any strange input like inputs in
        # strings line are updated and will be the same as input in cases that user uses
        # from_string classmethod
        cls_.values = values_dict['values']
        return cls_

    @classmethod
    def from_dict(cls, input_dict):
        """Make radiance glass from a dictionary.
        {
            "name": "", // Material Name
            "type": "glass",
            "r_transmissivity": float, // Transmissivity for red
            "g_transmissivity": float, // Transmissivity for green
            "b_transmissivity": float, // Transmissivity for blue
            "refraction_index": float, // Index of refraction
            "modifier": "", // material modifier (Default: "void")
            "dependencies": []
        }
        """
        assert 'type' in input_dict, 'Input dictionary is missing "type".'
        if input_dict['type'] != 'glass':
            raise ValueError('Type must be glass not %s.' % input_dict['type'])

        modifier, dependencies = Material.filter_dict_input(input_dict)

        return cls(name=input_dict["name"],
                   r_transmissivity=input_dict["r_transmissivity"],
                   g_transmissivity=input_dict["g_transmissivity"],
                   b_transmissivity=input_dict["b_transmissivity"],
                   refraction_index=input_dict["refraction_index"],
                   modifier=modifier,
                   dependencies=dependencies)

    def to_dict(self):
        """Translate radiance material to json
        {
            "type": "glass", // Material type
            "name": "", // Material Name
            "r_transmissivity": float, // Transmissivity for red
            "g_transmissivity": float, // Transmissivity for green
            "b_transmissivity": float, // Transmissivity for blue
            "refraction_index": float, // Index of refraction
            "modifier": "", // material modifier (Default: "void")
            "dependencies": []
        }
        """
        return {
            "modifier": self.modifier.to_dict(),
            "type": "glass",
            "name": self.name,
            "r_transmissivity": self.r_transmissivity,
            "g_transmissivity": self.g_transmissivity,
            "b_transmissivity": self.b_transmissivity,
            "refraction_index": self.refraction_index,
            "dependencies": [dp.to_dict() for dp in self.dependencies]
        }

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
