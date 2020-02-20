"""Generate sky with certain irradiance."""
from __future__ import division
from ._skybase import Sky
from .hemisphere import Hemisphere
from honeybee_radiance.lightsource.ground import Ground
import honeybee.typing as typing
import ladybug.futil as futil


class CertainIrradiance(Sky):
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
    __slots__ = (
        '_irradiance', '_ground', '_ground_reflectance',
        '_ground_hemisphere', '_sky_hemisphere'
    )

    def __init__(self, irradiance=558.659, ground_reflectance=0.2):
        """Create sky with certain irradiance."""
        Sky.__init__(self)
        self.irradiance = irradiance
        self.ground_reflectance = ground_reflectance
        self._ground_hemisphere = Ground()
        self._sky_hemisphere = Hemisphere()


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
    def ground_hemisphere(self):
        """Sky ground glow source."""
        return self._ground_hemisphere

    @property
    def sky_hemisphere(self):
        """Sky hemisphere glow source."""
        return self._sky_hemisphere

    @property
    def ground_reflectance(self):
        """Ground reflectance value."""
        return self._ground_reflectance

    @ground_reflectance.setter
    def ground_reflectance(self, ground_reflectance):
        self._ground_reflectance = \
            typing.float_in_range(ground_reflectance, 0, 1, 'ground reflectance') \
            if ground_reflectance is not None else 0.2

    @property
    def is_point_in_time(self):
        """Return True if the sky is generated for a single point in time."""
        return False

    @property
    def is_climate_based(self):
        """Return True if the sky is created based on values from weather file."""
        return False

    @classmethod
    def from_dict(cls, input_dict):
        """Create the sky from a dictionary.

        Args:
            input_dict: A python dictionary in the following format

        .. code-block:: python

                {
                'irradiance': 558.659,
                'ground_reflectance': 0.2,
                'ground_hemisphere': {},  # see ground.Ground class [optional],
                'sky_hemisphere': {}  # see hemisphere.Hemisphere class [optional]
                }
        """
        sky = cls(
            input_dict['irradiance'],
            input_dict['ground_reflectance']
        )

        if 'ground_hemisphere' in input_dict:
            sky._ground_hemisphere = Ground.from_dict(input_dict['ground_hemisphere'])

        if 'sky_hemisphere' in input_dict:
            sky._sky_hemisphere = Hemisphere.from_dict(input_dict['sky_hemisphere'])

        return sky

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
            'irradiance': self.irradiance,
            'ground_reflectance': self.ground_reflectance,
            'ground_hemisphere': self.ground_hemisphere.to_dict(),
            'sky_hemisphere': self.sky_hemisphere.to_dict()
        }

    def to_file(self, folder, name=None, mkdir=False):
        """Write sky hemisphere to a sky_hemisphere.rad Radiance file.

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
