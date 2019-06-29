"""Radiance Trans Material.

http://radsite.lbl.gov/radiance/refer/ray.html#Trans
https://radiance-online.org//community/workshops/2010-freiburg/PDF/DavidMead.pdf
"""
from __future__ import division
from .materialbase import Material
import honeybee.typing as typing


class Trans(Material):
    """Radiance translucent material."""

    def __init__(self, name, r_reflectance=0.0, g_reflectance=0.0, b_reflectance=0.0,
                 specularity=0.0, roughness=0.0, transmitted_diff=0.0,
                 transmitted_spec=0.0, modifier="void", dependencies=None):
        """Create trans material.

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
            transmitted_diff: The transmitted diffuse component is the fraction of
                transmitted light that is transmitted diffusely in as scattering fashion.
            transmitted_spec: The transmitted specular component is the fraction of
                transmitted light that is not diffusely scattered.
            modifier: Material modifier (Default: "void").
            dependencies: A list of primitives that this primitive depends on. This
                argument is only useful for defining advanced primitives where the
                primitive is defined based on other primitives. (Default: [])
        """
        Material.__init__(self, name, modifier=modifier,
                          dependencies=dependencies)
        self.r_reflectance = r_reflectance
        self.g_reflectance = g_reflectance
        self.b_reflectance = b_reflectance
        self.specularity = specularity
        self.roughness = roughness
        self.transmitted_diff = transmitted_diff
        self.transmitted_spec = transmitted_spec
        self._update_values()

    def _update_values(self):
        "update value dictionaries."
        self._values[2] = [
            self.r_reflectance, self.g_reflectance, self.b_reflectance,
            self.specularity, self.roughness, self.transmitted_diff,
            self.transmitted_spec
        ]

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
    def roughness(self, roughness_value):
        self._roughness = typing.float_in_range(roughness_value, 0, 1, 'roughness')

    @property
    def transmitted_diff(self):
        """Transmitted diffuse.

        The transmitted diffuse component is the fraction of transmitted light that is
        transmitted diffusely in as scattering fashion.
        """
        return self._transmitted_diff

    @transmitted_diff.setter
    def transmitted_diff(self, value):
        self._transmitted_diff = \
            typing.float_in_range(value, 0, 1, 'diffuse transmission')

    @property
    def transmitted_spec(self):
        """Transmitted specular.

        The transmitted specular component is the fraction of transmitted light that is
        not diffusely scattered.
        """
        return self._transmitted_spec

    @transmitted_spec.setter
    def transmitted_spec(self, value):
        self._transmitted_spec = \
            typing.float_in_range(value, 0, 1, 'specular transmission')

    @classmethod
    def from_reflected_specularity(
            cls, name, r_reflectance=0.0, g_reflectance=0.0, b_reflectance=0.0,
            reflected_specularity=0.0, roughness=0.0, transmitted_diff=0.0,
            transmitted_spec=0.0, modifier="void", dependencies=None):
        """Create trans material from reflected specularity.

        Note:
        https://radiance-online.org//community/workshops/2010-freiburg/PDF/DavidMead.pdf

        args:
            name: Material name as a string. Do not use white space or special
                character.
            r_reflectance: Reflectance for red. The value should be between 0 and 1
                (Default: 0).
            g_reflectance: Reflectance for green. The value should be between 0 and 1
                (Default: 0).
            b_reflectance: Reflectance for blue. The value should be between 0 and 1
                (Default: 0).
            reflected_specularity: Fraction of reflected specular. The reflected
                specularity of common uncoated glass is around .06, Matte = min 0,
                Satin = suggested max 0.07 (Default: 0).
            roughness: Roughness is specified as the rms slope of surface facets. A
                value of 0 corresponds to a perfectly smooth surface, and a value of 1
                would be a very rough surface. Roughness values greater than 0.2 are not
                very realistic. (Default: 0).
            transmitted_diff: The transmitted diffuse component is the fraction of
                transmitted light that is transmitted diffusely in as scattering fashion.
            transmitted_spec: The transmitted specular component is the fraction of
                transmitted light that is not diffusely scattered.
            modifier: Material modifier (Default: "void").
            dependencies: A list of primitives that this primitive depends on. This
                argument is only useful for defining advanced primitives where the
                primitive is defined based on other primitives. (Default: [])
        """
        cr, cg, cb, rs, roughness, td, ts = \
            r_reflectance, g_reflectance, b_reflectance, reflected_specularity, \
            roughness, transmitted_diff, transmitted_spec

        rd = (0.265 * cr + 0.670 * cg + 0.065 * cb)

        absorb = 1 - td - ts - rd - rs

        if absorb < 0:
            summ = td + ts + rd + rs
            msg = 'Sum of Diffuse Transmission (%.3f), Specular Transmission (%.3f),' \
                'Specular Reflection (%.3f) and Diffuse Reflection (%.3f) cannot be ' \
                'more than 1 (%.3f).' % (td, ts, rs, rd, summ)
            raise ValueError(msg)

        # calculate the material
        try:
            a7 = ts / (td + ts)
        except ZeroDivisionError:
            a7 = 0
        try:
            a6 = (td + ts) / (rd + td + ts)
        except ZeroDivisionError:
            a6 = 0
        a5 = roughness
        a4 = rs
        a3 = cb / ((1 - rs) * (1 - a6))
        a2 = cg / ((1 - rs) * (1 - a6))
        a1 = cr / ((1 - rs) * (1 - a6))

        if a3 > 1 or a2 > 1 or a1 > 1:
            raise ValueError(
                'This material is physically impossible to create!\n'
                'You need to adjust the inputs for diffuse reflectance values.')

        return cls(name, a1, a2, a3, a4, a5, a6, a7, modifier, dependencies=dependencies)

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
                'Type must be %s not %s.' % (
                    cls.__name__.lower(), values_dict['type'])
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
            transmitted_diff=values[5],
            transmitted_spec=values[6],
            modifier=modifier,
            dependencies=dependencies)

        # this might look redundant but it is NOT. see glass for explanation.
        cls_.values = values_dict['values']
        return cls_

    @classmethod
    def from_dict(cls, input_dict):
        """Make radiance material from dict
        {
            "modifier": {} or void, // Material modifier
            "type": "trans", // Material type
            "name": "", // Material Name
            "r_reflectance": float, // Reflectance for red
            "g_reflectance": float, // Reflectance for green
            "b_reflectance": float, // Reflectance for blue
            "specularity": float, // Material specularity
            "roughness": float, // Material roughness
            "transmitted_diff": float,
            "transmitted_spec": float,
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

        return cls(
            name=input_dict["name"],
            r_reflectance=input_dict["r_reflectance"],
            g_reflectance=input_dict["g_reflectance"],
            b_reflectance=input_dict["b_reflectance"],
            specularity=input_dict["specularity"],
            roughness=input_dict["roughness"],
            transmitted_diff=input_dict["transmitted_diff"],
            transmitted_spec=input_dict["transmitted_spec"],
            modifier=modifier,
            dependencies=dependencies)

    @classmethod
    def from_single_reflectance(
        cls, name, rgb_reflectance=0.0, specularity=0.0, roughness=0.0,
        transmitted_diff=0.0, transmitted_spec=0.0, modifier="void",
            dependencies=None):
        """Create trans material with single reflectance value.

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
            transmitted_diff: The transmitted diffuse component is the fraction of
                transmitted light that is transmitted diffusely in as scattering fashion.
            transmitted_spec: The transmitted specular component is the fraction of
                transmitted light that is not diffusely scattered.
            modifier: Material modifier (Default: "void").
            dependencies: A list of primitives that this primitive depends on. This
                argument is only useful for defining advanced primitives where the
                primitive is defined based on other primitives. (Default: [])
        """
        return cls(name, r_reflectance=rgb_reflectance, g_reflectance=rgb_reflectance,
                   b_reflectance=rgb_reflectance, specularity=specularity,
                   roughness=roughness, transmitted_diff=transmitted_diff,
                   transmitted_spec=transmitted_spec, modifier=modifier,
                   dependencies=dependencies)

    @property
    def average_reflectance(self):
        """Calculate average reflectance of trans material."""
        return (0.265 * self.r_reflectance + 0.670 * self.g_reflectance +
                0.065 * self.b_reflectance) * (1 - self.specularity) + self.specularity

    @property
    def specular_sampling_threshold(self):
        """Suggested specular sampling threshold (-st)."""
        return self.transmitted_diff * self.transmitted_spec * \
            (1 - (0.265 * self.r_reflectance + 0.670 * self.g_reflectance +
                  0.065 * self.b_reflectance)) * self.specularity

    def to_dict(self):
        """Translate radiance material to dict
        {
            "type": "trans", // Material type
            "name": "", // Material Name
            "r_reflectance": float, // Reflectance for red
            "g_reflectance": float, // Reflectance for green
            "b_reflectance": float, // Reflectance for blue
            "specularity": float, // Material specularity
            "roughness": float, // Material roughness
            "transmitted_diff": float,
            "transmitted_spec": float,
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
            'transmitted_diff': self.transmitted_diff,
            'transmitted_spec': self.transmitted_spec,
            'dependencies': [dp.to_dict() for dp in self.dependencies]
        }
