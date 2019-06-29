"""Radiance Plastic Material.

http://radsite.lbl.gov/radiance/refer/ray.html#Plastic
"""
from .materialbase import Material
import honeybee.typing as typing


class Plastic(Material):
    """Radiance plastic material."""

    def __init__(self, name, r_reflectance=0.0, g_reflectance=0.0, b_reflectance=0.0,
                 specularity=0.0, roughness=0.0, modifier="void", dependencies=None):
        """Create plastic material.

        args:
            name: Material name as a string. Do not use white space or special
                character.
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

        Usage:
            wall_material = Plastic("generic_wall", .55, .65, .75)
            print(wall_material)
        """
        Material.__init__(self, name, modifier=modifier,
                          dependencies=dependencies)
        self.r_reflectance = r_reflectance
        self.g_reflectance = g_reflectance
        self.b_reflectance = b_reflectance
        self.specularity = specularity
        self.roughness = roughness

        self._update_values()

    def _update_values(self):
        "update value dictionaries."
        self._values[2] = [
            self.r_reflectance, self.g_reflectance, self.b_reflectance,
            self.specularity, self.roughness
        ]

        if self.specularity > 0.1:
            print("Warning: Specularity values above .1 is uncommon for plastic.")
        if self.roughness > 0.2:
            print("Warning: Roughness values above .2 is uncommon.")

    @property
    def r_reflectance(self):
        """Reflectance for red channel.

        The value should be between 0 and 1 (Default: 0).
        """
        return self._r_reflectance

    @r_reflectance.setter
    def r_reflectance(self, reflectance):
        self._r_reflectance = \
            typing.float_in_range(reflectance, 0, 1, 'red reflectance')

    @property
    def g_reflectance(self):
        """Reflectance for green channel.

        The value should be between 0 and 1 (Default: 0).
        """
        return self._g_reflectance

    @g_reflectance.setter
    def g_reflectance(self, reflectance):
        self._g_reflectance = \
            typing.float_in_range(reflectance, 0, 1, 'green reflectance')

    @property
    def b_reflectance(self):
        """Reflectance for blue channel.

        The value should be between 0 and 1 (Default: 0).
        """
        return self._b_reflectance

    @b_reflectance.setter
    def b_reflectance(self, reflectance):
        self._b_reflectance = \
            typing.float_in_range(reflectance, 0, 1, 'blue reflectance')

    @property
    def specularity(self):
        """Fraction of specularity.

        In most cases specularity fractions greater than 0.1 are not realistic
        (Default: 0).
        """
        return self._specularity

    @specularity.setter
    def specularity(self, spec_value):
        self._specularity = typing.float_in_range(spec_value, 0, 1, 'specularity')

    @property
    def roughness(self):
        """Roughness is specified as the rms slope of surface facets.

        A value of 0 corresponds to a perfectly smooth surface, and a value of 1
        would be a very rough surface. Roughness values greater than 0.2 are not
        very realistic. (Default: 0).
        """
        return self._roughness

    @roughness.setter
    def roughness(self, roughness_values):
        self._roughness = typing.float_in_range(roughness_values, 0, 1, 'roughness')

    @property
    def average_reflectance(self):
        """Calculate average reflectance of plastic material."""
        return (0.265 * self.r_reflectance + 0.670 * self.g_reflectance +
                0.065 * self.b_reflectance) * (1 - self.specularity) + self.specularity

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
        if values_dict['type'] != cls.__name__.lower():
            raise ValueError(
                'Type must be %s not %s.' % (cls.__name__.lower(), values_dict['type'])
            )

        modifier, dependencies = cls.filter_dict_input(values_dict)
        values = values_dict['values'][2]
        cls_ = cls(
            name=values_dict["name"],
            r_reflectance=values[0],
            g_reflectance=values[1],
            b_reflectance=values[2],
            specularity=values[3],
            roughness=values[4],
            modifier=modifier,
            dependencies=dependencies
        )

        # this might look redundant but it is NOT. see glass for explanation.
        cls_.values = values_dict['values']
        return cls_

    @classmethod
    def from_dict(cls, input_dict):
        """Make radiance material from dict
        {
            "modifier": {} or void, // Material modifier
            "type": "plastic", // Material type
            "name": "", // Material Name
            "r_reflectance": float, // Reflectance for red
            "g_reflectance": float, // Reflectance for green
            "b_reflectance": float, // Reflectance for blue
            "specularity": float, // Material specularity
            "roughness": float, // Material roughness
            "dependencies": []
        }
        """
        assert 'type' in input_dict, 'Input dictionary is missing "type".'
        if input_dict['type'] != cls.__name__.lower():
            raise ValueError(
                'Type must be %s not %s.' % (cls.__name__.lower(),
                    input_dict['type'])
            )
        modifier, dependencies = Material.filter_dict_input(input_dict)

        return cls(name=input_dict["name"],
                   r_reflectance=input_dict["r_reflectance"],
                   g_reflectance=input_dict["g_reflectance"],
                   b_reflectance=input_dict["b_reflectance"],
                   specularity=input_dict["specularity"],
                   roughness=input_dict["roughness"],
                   modifier=modifier,
                   dependencies=dependencies)

    @classmethod
    def from_single_reflectance(
        cls, name, rgb_reflectance=0.0, specularity=0.0, roughness=0.0, modifier="void",
            dependencies=None):
        """Create plastic material with single reflectance value.

        args:
            name: Material name as a string. Do not use white space or special character
            rgb_reflectance: Reflectance for red, green and blue. The value should be
                between 0 and 1 (Default: 0).
            specularity: Fraction of specularity. Specularity fractions greater than 0.1
                are not realistic (Default: 0).
            roughness: Roughness is specified as the rms slope of surface facets. A value
                of 0 corresponds to a perfectly smooth surface, and a value of 1 would be
                a very rough surface. Roughness values greater than 0.2 are not very
                realistic. (Default: 0).
            modifier: Material modifier (Default: "void").
            dependencies: A list of primitives that this primitive depends on. This
                argument is only useful for defining advanced primitives where the
                primitive is defined based on other primitives. (Default: [])

        Usage:
            wall_material = Plastic.by_single_reflect_value("generic_wall", .55)
            print(wall_material)
        """
        return cls(name, r_reflectance=rgb_reflectance, g_reflectance=rgb_reflectance,
                   b_reflectance=rgb_reflectance, specularity=specularity,
                   roughness=roughness, modifier=modifier, dependencies=dependencies)

    def to_dict(self):
        """Translate radiance material to dict
        {
            "type": "plastic", // Material type
            "name": "", // Material Name
            "r_reflectance": float, // Reflectance for red
            "g_reflectance": float, // Reflectance for green
            "b_reflectance": float, // Reflectance for blue
            "specularity": float, // Material specularity
            "roughness": float, // Material roughness
            "dependencies": []
        }
        """
        return {
            'modifier': self.modifier.to_dict(),
            'type': self.__class__.__name__.lower(),
            'name': self.name,
            'r_reflectance': self.r_reflectance,
            'g_reflectance': self.g_reflectance,
            'b_reflectance': self.b_reflectance,
            'specularity': self.specularity,
            'roughness': self.roughness,
            'dependencies': [dp.to_dict() for dp in self.dependencies]
        }


# should move to library and be a single instance
class BlackMaterial(Plastic):
    """Radiance black plastic material."""

    def __init__(self, name='black', r_reflectance=0.0, g_reflectance=0.0,
                 b_reflectance=0.0, specularity=0.0, roughness=0.0, modifier="void"):
        Plastic.__init__(self, name)
