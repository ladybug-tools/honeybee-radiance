"""Radiance Trans Material.

http://radsite.lbl.gov/radiance/refer/ray.html#Trans
https://radiance-online.org//community/workshops/2010-freiburg/PDF/DavidMead.pdf
"""
from __future__ import division

from .materialbase import Material
import honeybee.typing as typing


class Trans(Material):
    """Radiance translucent material.

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
            are not common in non-metallic materials (Default: 0).
        roughness: Roughness is specified as the rms slope of surface facets. A
            value of 0 corresponds to a perfectly smooth surface, and a value of 1
            would be a very rough surface. Roughness values greater than 0.2 are not
            very realistic. (Default: 0).
        transmitted_diff: The transmitted diffuse component is the fraction of
            transmitted light that is transmitted diffusely in as scattering fashion.
        transmitted_spec: The transmitted specular component is the fraction of
            transmitted light that is not diffusely scattered.
        modifier: Material modifier (Default: None).
        dependencies: A list of primitives that this primitive depends on. This
            argument is only useful for defining advanced primitives where the
            primitive is defined based on other primitives. (Default: None)

    Properties:
        * identifier
        * display_name
        * r_reflectance
        * g_reflectance
        * b_reflectance
        * specularity
        * roughness
        * transmitted_diff
        * transmitted_spec
        * values
        * modifier
        * dependencies
        * is_modifier
        * is_material
    """
    __slots__ = ('_r_reflectance', '_g_reflectance', '_b_reflectance',
                 '_specularity', '_roughness', '_transmitted_diff', '_transmitted_spec')

    def __init__(self, identifier, r_reflectance=0.0, g_reflectance=0.0, b_reflectance=0.0,
                 specularity=0.0, roughness=0.0, transmitted_diff=0.0,
                 transmitted_spec=0.0, modifier=None, dependencies=None):
        """Create trans material."""
        Material.__init__(self, identifier, modifier=modifier,
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

        In most cases specularity fractions greater than 0.1 are not common in
        non-metallic materials (Default: 0).
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

    @classmethod
    def from_reflected_specularity(
            cls, identifier, r_reflectance=0.0, g_reflectance=0.0, b_reflectance=0.0,
            reflected_specularity=0.0, roughness=0.0, transmitted_diff=0.0,
            transmitted_spec=0.0, modifier=None, dependencies=None):
        """Create trans material from reflected specularity.

        Note:
        https://radiance-online.org//community/workshops/2010-freiburg/PDF/DavidMead.pdf

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
            modifier: Material modifier (Default: None).
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

        return cls(identifier, a1, a2, a3, a4, a5, a6, a7, modifier,
                   dependencies=dependencies)

    @classmethod
    def from_single_reflectance(
        cls, identifier, rgb_reflectance=0.0, specularity=0.0, roughness=0.0,
        transmitted_diff=0.0, transmitted_spec=0.0, modifier=None, dependencies=None):
        """Create trans material with single reflectance value.

        Args:
            identifier: Text string for a unique Material ID. Must not contain spaces
                or special characters. This will be used to identify the object across
                a model and in the exported Radiance files.
            rgb_reflectance: Reflectance for red, green and blue. The value should be
                between 0 and 1 (Default: 0).
            specularity: Fraction of specularity. Specularity fractions greater than 0.1
                are not common in non-metallic materials (Default: 0).
            roughness: Roughness is specified as the rms slope of surface facets. A value
                of 0 corresponds to a perfectly smooth surface, and a value of 1 would be
                a very rough surface. Roughness values greater than 0.2 are not very
                realistic. (Default: 0).
            transmitted_diff: The transmitted diffuse component is the fraction of
                transmitted light that is transmitted diffusely in a scattering fashion.
            transmitted_spec: The transmitted specular component is the fraction of
                transmitted light that is not diffusely scattered.
            modifier: Material modifier (Default: None).
            dependencies: A list of primitives that this primitive depends on. This
                argument is only useful for defining advanced primitives where the
                primitive is defined based on other primitives. (Default: [])
        """
        return cls(
            identifier, r_reflectance=rgb_reflectance, g_reflectance=rgb_reflectance,
            b_reflectance=rgb_reflectance, specularity=specularity, roughness=roughness,
            transmitted_diff=transmitted_diff, transmitted_spec=transmitted_spec,
            modifier=modifier, dependencies=dependencies)

    @classmethod
    def from_primitive_dict(cls, primitive_dict):
        """Initialize Trans from a primitive dict.

        Args:
            data: A dictionary in the format below.

        .. code-block:: python

            {
            "modifier": {},  # primitive modifier (Default: None)
            "type": "trans",  # primitive type
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
            r_reflectance=values[0],
            g_reflectance=values[1],
            b_reflectance=values[2],
            specularity=values[3],
            roughness=values[4],
            transmitted_diff=values[5],
            transmitted_spec=values[6],
            modifier=modifier,
            dependencies=dependencies)
        if 'display_name' in primitive_dict and primitive_dict['display_name'] is not None:
            cls_.display_name = primitive_dict['display_name']

        # this might look redundant but it is NOT. see glass for explanation.
        cls_.values = primitive_dict['values']
        return cls_

    @classmethod
    def from_dict(cls, data):
        """Initialize Trans from a dictionary.

        Args:
            data: A dictionary in the format below.

        .. code-block:: python

            {
            "type": "Trans",  # Material type
            "identifier": "", # Material identifier
            "display_name": "",  # Material display name
            "r_reflectance": float,  # Reflectance for red
            "g_reflectance": float,  # Reflectance for green
            "b_reflectance": float,  # Reflectance for blue
            "specularity": float,  # Material specularity
            "roughness": float,  # Material roughness
            "transmitted_diff": float,
            "transmitted_spec": float,
            "dependencies": []
            "modifier": {},  # Material modifier (Default: None)
            }
        """
        cls._dict_type_check(cls.__name__, data)
        modifier, dependencies = cls.filter_dict_input(data)

        new_obj = cls(
            identifier=data["identifier"],
            r_reflectance=data["r_reflectance"],
            g_reflectance=data["g_reflectance"],
            b_reflectance=data["b_reflectance"],
            specularity=data["specularity"],
            roughness=data["roughness"],
            transmitted_diff=data["transmitted_diff"],
            transmitted_spec=data["transmitted_spec"],
            modifier=modifier,
            dependencies=dependencies)
        if 'display_name' in data and data['display_name'] is not None:
            new_obj.display_name = data['display_name']
        return new_obj

    def to_dict(self):
        """Translate this object to a dictionary."""
        base = {
            'modifier': self.modifier.to_dict(),
            'type': 'Trans',
            'identifier': self.identifier,
            'r_reflectance': self.r_reflectance,
            'g_reflectance': self.g_reflectance,
            'b_reflectance': self.b_reflectance,
            'specularity': self.specularity,
            'roughness': self.roughness,
            'transmitted_diff': self.transmitted_diff,
            'transmitted_spec': self.transmitted_spec,
            'dependencies': [dp.to_dict() for dp in self.dependencies]
        }
        if self._display_name is not None:
            base['display_name'] = self.display_name
        return base

    def __copy__(self):
        mod, depend = self._dup_mod_and_depend()
        new_obj = self.__class__(
            self.identifier, self.r_reflectance, self.g_reflectance, self.b_reflectance,
            self.specularity, self.roughness, self.transmitted_diff,
            self.transmitted_spec, mod, depend)
        new_obj._display_name = self._display_name
        return new_obj
