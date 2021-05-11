"""Generate sky with certain irradiance."""
from __future__ import division
import argparse
import shlex

import honeybee.typing as typing
import ladybug.futil as futil

from ._skybase import _PointInTime
from .hemisphere import Hemisphere
from honeybee_radiance.lightsource.ground import Ground


class CertainIrradiance(_PointInTime):
    """sky with certain irradiance.

    The output of CertainIrradiance sky is similar to using command below::

        gensky -c -B desired_irradiance

    You can also generate the sky with certain illuminance using ``from_illuminance``
    classmethod. The method converts the illuminance value to irradiance by dividing it
    by 179.0::

        gensky -c -B [desired_illuminance / 179.0]

    It also includes ground glow source. Ground reflectance is set to %20 by default
    which is gensky's default value. Use `ground_reflectance` property to adjust this
    value.

    Note:

    The conversion factor in the Radiance system for luminous efficacy is fixed at
    KR= 179 lumens/watt (lm/w). This should not be confused with the more usual
    daylighting value, which can be anywhere between 50 and 150 lm/w depending on the
    type of sky or light considered.

    For more information see links below on the Radiance forum:

    * https://discourse.radiance-online.org/t/coefficient-179/547
    * https://discourse.radiance-online.org/t/luminous-efficacy/1400

    Default value is set to 558.659 which corresponds to a sky with 100,000 lux
    horizontal illuminance.

    Args:
        irradiance: Desired horizontal diffuse irradiance value in watts/meter2
            (Default: 558.659).
        ground_reflectance: Average ground reflectance (Default: 0.2).

    Properties:
        * irradiance
        * illuminance
        * ground_hemisphere
        * sky_hemisphere
        * ground_reflectance
        * is_point_in_time
        * is_climate_based
    """
    __slots__ = ('_irradiance',)

    def __init__(self, irradiance=558.659, ground_reflectance=0.2):
        """Create sky with certain irradiance."""
        _PointInTime.__init__(self, ground_reflectance)
        self.irradiance = irradiance

    @classmethod
    def from_illuminance(cls, illuminance=100000, ground_reflectance=0.2):
        """Create sky with certain illuminance.

        Args:
            illuminance: Desired horizontal illuminance value in lux (Default: 100000).
            ground_reflectance: Average ground reflectance (Default: 0.2).
        """
        return cls(illuminance / 179.0, ground_reflectance)

    @property
    def irradiance(self):
        """Sky irradiance value."""
        return self._irradiance

    @irradiance.setter
    def irradiance(self, irradiance):
        self._irradiance = typing.float_positive(irradiance) \
            if irradiance is not None else 558.659

    @property
    def illuminance(self):
        """Sky illuminance value."""
        return round(self._irradiance * 179.0, 2)

    @property
    def is_point_in_time(self):
        """Return True if the sky is generated for a single point in time."""
        return False

    @classmethod
    def from_dict(cls, data):
        """Create the sky from a dictionary.

        Args:
            data: A python dictionary in the following format

        .. code-block:: python

            {
                'type': 'CertainIrradiance',
                'irradiance': 558.659,
                'ground_reflectance': 0.2,
                'ground_hemisphere': {},  # see ground.Ground class [optional],
                'sky_hemisphere': {}  # see hemisphere.Hemisphere class [optional]
            }
        """
        assert 'type' in data, \
            'Input dict is missing type. Not a valid CertainIrradiance dictionary.'
        assert data['type'] == 'CertainIrradiance', \
            'Input type must be CertainIrradiance not %s' % data['type']

        sky = cls(
            data['irradiance'],
            data['ground_reflectance']
        )

        if 'ground_hemisphere' in data and data['ground_hemisphere'] is not None:
            sky._ground_hemisphere = Ground.from_dict(data['ground_hemisphere'])

        if 'sky_hemisphere' in data and data['sky_hemisphere'] is not None:
            sky._sky_hemisphere = Hemisphere.from_dict(data['sky_hemisphere'])

        return sky

    @classmethod
    def from_string(cls, sky_string):
        """Create a CertainIrradiance sky from a string.

        Args:
            sky_string: A text string representing a CertainIrradiance sky. This
                can be either a string with a certain irradiance (eg.
                "irradiance 558.659") or with a certain illuminance (eg.
                "illuminance 100000"). Any sky string can optionally
                have a "-g" property of a fractional number, which sets the
                reflectance of the ground. If unspecified, the ground will have
                a reflectance of 0.2.

        Usage:

        .. code-block:: python

            # irradiance string representation of the sky
            sky_string = "irradiance 558.659"
            sky = CertainIrradiance.from_string(sky_string)

            # illuminance string representation of the sky
            sky_string = "illuminance 100000 -g 0.3"
            sky = CertainIrradiance.from_string(sky_string)
        """
        # check the input
        lower_str = sky_string.lower()
        assert lower_str.startswith(('irradiance', 'illuminance')), \
            'Expected string representation of CertainIrradiance sky "{}" to ' \
            'start with "irradiance" or "illuminance".'.format(sky_string)
        split_str = shlex.split(lower_str)
        # make a parser for all of the other sky properties
        pars = argparse.ArgumentParser()
        pars.add_argument('value', action='store', type=float)
        pars.add_argument('-g', action='store', dest='g', type=float, default=0.2)
        props = pars.parse_args(split_str[1:])

        # create the sky object
        if split_str[0] == 'irradiance':
            return cls(props.value, props.g)
        else:
            return cls.from_illuminance(props.value, props.g)

    def to_radiance(self):
        """Return radiance definition as a string."""
        command = '!gensky -ang 45 0 -c -B %.6f -g %.3f' % (
            self.irradiance, self.ground_reflectance
        )

        return '%s\n\n%s\n\n%s\n' % (
            command, self.sky_hemisphere, self.ground_hemisphere
        )

    def to_dict(self):
        """Translate sky to a dictionary."""
        return {
            'type': 'CertainIrradiance',
            'irradiance': self.irradiance,
            'ground_reflectance': self.ground_reflectance,
            'ground_hemisphere': self.ground_hemisphere.to_dict(),
            'sky_hemisphere': self.sky_hemisphere.to_dict()
        }

    def to_file(self, folder, name=None, mkdir=False):
        """Write sky hemisphere to a sky_hemisphere.rad Radiance file.

        Args:
            folder: Target folder.
            name: File name.
            mkdir: A boolean to note if the directory should be created if doesn't
                exist (default: False).

        Returns:
            Full path to the newly created file.
        """
        content = self.to_radiance()
        name = typing.valid_string(name) if name \
            else '%d_lux.sky' % int(self.illuminance)
        return futil.write_to_file_by_name(folder, name, content, mkdir)

    def __eq__(self, value):
        if type(value) != type(self) \
            or value.irradiance != self.irradiance \
            or self.ground_reflectance != value.ground_reflectance \
            or self.ground_hemisphere != value.ground_hemisphere \
                or self.sky_hemisphere != value.sky_hemisphere:
            return False
        return True

    def __ne__(self, value):
        return not self.__eq__(value)

    def __repr__(self):
        """Sky representation."""
        return 'irradiance {} -g {}'.format(self.irradiance, self.ground_reflectance)
