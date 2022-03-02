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
        * average_reflectance
        * average_absorption
        * average_transmittance
        * diffuse_reflectance
        * diffuse_transmittance
        * specular_transmittance
        * specular_sampling_threshold
        * values
        * modifier
        * dependencies
        * is_modifier
        * is_material
    """
    __slots__ = ('_r_reflectance', '_g_reflectance', '_b_reflectance',
                 '_specularity', '_roughness', '_transmitted_diff', '_transmitted_spec')

    def __init__(
        self, identifier, r_reflectance=0.0, g_reflectance=0.0, b_reflectance=0.0,
        specularity=0.0, roughness=0.0, transmitted_diff=0.0,
        transmitted_spec=0.0, modifier=None, dependencies=None
    ):
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
        """Get or set the reflectance for red channel.

        The value should be between 0 and 1 (Default: 0).
        """
        return self._r_reflectance

    @r_reflectance.setter
    def r_reflectance(self, reflectance):
        self._r_reflectance = \
            typing.float_in_range(reflectance, 0, 1, 'red reflectance')

    @property
    def g_reflectance(self):
        """Get or set the reflectance for green channel.

        The value should be between 0 and 1 (Default: 0).
        """
        return self._g_reflectance

    @g_reflectance.setter
    def g_reflectance(self, reflectance):
        self._g_reflectance = \
            typing.float_in_range(reflectance, 0, 1, 'green reflectance')

    @property
    def b_reflectance(self):
        """Get or set the reflectance for blue channel.

        The value should be between 0 and 1 (Default: 0).
        """
        return self._b_reflectance

    @b_reflectance.setter
    def b_reflectance(self, reflectance):
        self._b_reflectance = \
            typing.float_in_range(reflectance, 0, 1, 'blue reflectance')

    @property
    def specularity(self):
        """Get or set the fraction of specularity.

        In most cases specularity fractions greater than 0.1 are not common in
        non-metallic materials (Default: 0).
        """
        return self._specularity

    @specularity.setter
    def specularity(self, spec_value):
        self._specularity = typing.float_in_range(spec_value, 0, 1, 'specularity')

    @property
    def roughness(self):
        """Get or set the roughness as the rms slope of surface facets.

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
        """Get or set the transmitted diffuse.

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
        """Get or set the transmitted specular.

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
        """Get the average reflectance of over the RGB values of the material."""
        col_ref = 0.265 * self.r_reflectance + 0.670 * self.g_reflectance + \
            0.065 * self.b_reflectance
        dif_ref = (1 - self._specularity) * col_ref * (1 - self._transmitted_diff)
        return self._specularity + dif_ref

    @property
    def average_absorption(self):
        """Get the average absorption of over the RGB values of the material."""
        return (1 - (0.265 * self.r_reflectance + 0.670 * self.g_reflectance +
                0.065 * self.b_reflectance)) * (1 - self._specularity)

    @property
    def average_transmittance(self):
        """Get the total transmittance over the material."""
        return (1 - self._specularity) * self._transmitted_diff * \
            (0.265 * self.r_reflectance + 0.670 * self.g_reflectance + 0.065 *
             self.b_reflectance)

    @property
    def diffuse_reflectance(self):
        """Get the average diffuse reflectance of over the RGB values of the material."""
        col_ref = 0.265 * self.r_reflectance + 0.670 * self.g_reflectance + \
            0.065 * self.b_reflectance
        return (1 - self._specularity) * col_ref * (1 - self._transmitted_diff)

    @property
    def diffuse_transmittance(self):
        """Get the total transmitted diffuse component."""
        return self.average_transmittance * (1 - self._transmitted_spec)

    @property
    def specular_transmittance(self):
        """Get the total transmitted specular component."""
        return self.average_transmittance * self._transmitted_spec

    @property
    def specular_sampling_threshold(self):
        """Get the suggested specular sampling threshold (-st)."""
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
        transmitted_diff=0.0, transmitted_spec=0.0, modifier=None, dependencies=None
    ):
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
    def from_average_properties(
        cls, identifier, average_reflectance=0.0, average_transmittance=0.0,
        is_specular=False, is_diffusing=True, roughness=0.0,
        modifier=None, dependencies=None
    ):
        """Create trans material from average reflectance and transmittance.

        The sum of average_reflectance and average_transmittance must be less than
        one and any energy not transmitted or reflected is assumed to be absorbed.
        The resulting material will always be grey with equivalent red, green and
        blue channels.

        Args:
            identifier: Text string for a unique Material ID. Must not contain spaces
                or special characters. This will be used to identify the object across
                a model and in the exported Radiance files.
            average_reflectance: The average reflectance of the material. The value
                should be between 0 and 1 (Default: 0).
            average_transmittance: The average transmittance of the material. The value
                should be between 0 and 1 (Default: 0).
            is_specular: Boolean to note if the reflected component is specular (True)
                or diffuse (False). (Default: False).
            is_diffusing: Boolean to note if the tranmitted component is diffused (True)
                instead of specular like glass (False). (Default: True).
            roughness: Roughness is specified as the rms slope of surface facets. A value
                of 0 corresponds to a perfectly smooth surface, and a value of 1 would be
                a very rough surface. Roughness values greater than 0.2 are not very
                realistic. (Default: 0).
            modifier: Material modifier (Default: None).
            dependencies: A list of primitives that this primitive depends on. This
                argument is only useful for defining advanced primitives where the
                primitive is defined based on other primitives. (Default: [])
        """
        # check to be sure the input values are valid
        absorb = 1 - average_reflectance - average_transmittance
        assert absorb >= 0, 'Sum of average_reflectance and average_transmittance ' \
            'must be less than or equal to one. Got {}.'.format(
                average_reflectance + average_transmittance)
        # determine the reflectance values
        if is_specular:
            spec_ref = average_reflectance
            diff_ref = average_transmittance / (1 - average_reflectance)
            total_trans = 1
        else:
            spec_ref, total_ref = 0, 1 - absorb
            diff_ref = total_ref
            total_trans = average_transmittance / total_ref if total_ref != 0 else 0
        # determine the transmittance values
        if is_diffusing:
            diff_trans, spec_trans = total_trans, 0
        else:
            diff_trans, spec_trans = total_trans, 1
        # create the modifier
        return cls.from_single_reflectance(
            identifier, rgb_reflectance=diff_ref, specularity=spec_ref,
            transmitted_diff=diff_trans, transmitted_spec=spec_trans,
            roughness=roughness, modifier=modifier, dependencies=dependencies)

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
        if 'display_name' in primitive_dict and \
                primitive_dict['display_name'] is not None:
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
