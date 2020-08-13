"""Generate a point-in-time climate-based sky."""
from __future__ import division
from ._skybase import _PointInTime
from .hemisphere import Hemisphere
from ..ground import Ground
import honeybee.typing as typing
import ladybug.futil as futil
from ladybug.location import Location
from ladybug.sunpath import Sunpath
from ladybug.wea import Wea
from ladybug.epw import EPW
from ladybug.dt import DateTime


class ClimateBased(_PointInTime):
    """Point-in-time Climate-based sky.

    The output of Climatebased sky is similar to using command Radiance's gendaylit
    command. For more information see gendaylit documentation.

    Args:
        altitude: Solar altitude. The altitude is measured in degrees above the horizon.
        azimuth: Solar azimuth. The azimuth is measured in degrees east of North. East is
            90, South is 180 and West is 270. Note that this input is different from
            Radiance convention. In Radiance the azimuth degrees are measured in west of
            South.
        direct_normal_irradiance: Direct normal irradiance (W/m2).
        diffuse_horizontal_irradiance: Diffuse horizontal irradiance (W/m2).
        ground_reflectance: Average ground reflectance (Default: 0.2).

    Properties:
        * altitude
        * azimuth
        * direct_normal_irradiance
        * diffuse_horizontal_irradiance
        * ground_hemisphere
        * sky_hemisphere
        * ground_reflectance
        * is_point_in_time
        * is_climate_based
    """

    __slots__ = (
        '_altitude', '_azimuth', '_diffuse_horizontal_irradiance',
        '_direct_normal_irradiance'
    )

    def __init__(
        self, altitude, azimuth, direct_normal_irradiance, diffuse_horizontal_irradiance,
            ground_reflectance=0.2):
        """Create a climate-based standard sky."""
        _PointInTime.__init__(self, ground_reflectance)
        self.altitude = altitude
        self.azimuth = azimuth
        self.direct_normal_irradiance = direct_normal_irradiance
        self.diffuse_horizontal_irradiance = diffuse_horizontal_irradiance

    @property
    def altitude(self):
        """Get or set a number between -90 and 90 for the solar altitude.

        The altitude is measured in degrees above the horizon.
        """
        return self._altitude

    @altitude.setter
    def altitude(self, value):
        value = typing.float_in_range(value, -90, 90, 'Solar altitude')
        self._altitude = value

    @property
    def azimuth(self):
        """Get or set a number between 0 and 360 for the solar azimuth.

        The azimuth is measured in degrees east of North. East is 90, South is 180 and
        West is 270. Note that this input is different from Radiance convention. In
        Radiance the azimuth degrees are measured in west of South.
        """
        return self._azimuth

    @azimuth.setter
    def azimuth(self, value):
        value = typing.float_in_range(value, 0, 360, 'Solar azimuth')
        self._azimuth = value

    @property
    def direct_normal_irradiance(self):
        """Get and set direct normal irradiance (W/m2).
        """
        return self._direct_normal_irradiance

    @direct_normal_irradiance.setter
    def direct_normal_irradiance(self, value):
        value = typing.int_positive(value, 'Direct normal irradiance')
        self._direct_normal_irradiance = value

    @property
    def diffuse_horizontal_irradiance(self):
        """Get and set diffuse horizontal irradiance (W/m2).
        """
        return self._diffuse_horizontal_irradiance

    @diffuse_horizontal_irradiance.setter
    def diffuse_horizontal_irradiance(self, value):
        value = typing.int_positive(value, 'Diffuse horizontal irradiance')
        self._diffuse_horizontal_irradiance = value

    @property
    def is_climate_based(self):
        """Return True if the sky is created based on values from weather data."""
        return True

    @classmethod
    def from_lat_long(
        cls, latitude, longitude, time_zone, month, day, hour, direct_normal_irradiance,
            diffuse_horizontal_irradiance, north_angle=0, ground_reflectance=0.2):
        """Create sky with certain illuminance.

        Args:
            latitude: Location latitude between -90 and 90.
            longitude:Location longitude between -180 (west) and 180 (east).
            timezone: Time zone between -12 hours (west) and +14 hours (east).
            month: An intger between 1-12 for month.
            day: An intger between 1 to 28-31 depending on the input month.
            hour: A float number larger or equal to 0 and smaller than 24.
            direct_normal_irradiance: Direct normal irradiance (W/m2).
            diffuse_horizontal_irradiance: Diffuse horizontal irradiance (W/m2).
            north_angle: North angle in degrees. A number between -360 and 360 for the
                counterclockwise difference between the North and the positive Y-axis in
                degrees. 90 is West and 270 is East (Default: 0).
            ground_reflectance: Average ground reflectance (Default: 0.2).
        """
        #  calculate altitude and azimuth using ladybug's sunpath
        sp = Sunpath(latitude, longitude, time_zone, north_angle)
        sun = sp.calculate_sun(month, day, hour)
        return cls(
            sun.altitude, sun.azimuth_from_y_axis, direct_normal_irradiance,
            diffuse_horizontal_irradiance, ground_reflectance)

    @classmethod
    def from_location(
        cls, location, month, day, hour, direct_normal_irradiance,
            diffuse_horizontal_irradiance, north_angle=0, ground_reflectance=0.2):
        """Create a standard climate-based sky for a location.

        Args:
            location: A Ladybug location.
            month: An intger between 1-12 for month.
            day: An intger between 1 to 28-31 depending on the input month.
            hour: A float number larger or equal to 0 and smaller than 24.
            direct_normal_irradiance: Direct normal irradiance (W/m2).
            diffuse_horizontal_irradiance: Diffuse horizontal irradiance (W/m2).
            north_angle: North angle in degrees. A number between -360 and 360 for the
                counterclockwise difference between the North and the positive Y-axis in
                degrees. 90 is West and 270 is East (Default: 0).
            ground_reflectance: Average ground reflectance (Default: 0.2).
        """
        assert isinstance(location, Location), \
            'location must be from type Location not {}'.format(type(location))
        return cls.from_lat_long(
            location.latitude, location.longitude, location.time_zone, month, day, hour,
            direct_normal_irradiance, diffuse_horizontal_irradiance, north_angle,
            ground_reflectance)

    @classmethod
    def from_wea(cls, wea, month, day, hour, north_angle=0, ground_reflectance=0.2):
        """Create a standard climate-based sky from a Wea.

        Args:
            wea: A Ladybug wea object.
            month: An intger between 1-12 for month.
            day: An intger between 1 to 28-31 depending on the input month.
            hour: A float number larger or equal to 0 and smaller than 24.
            direct_normal_irradiance: Direct normal irradiance (W/m2).
            diffuse_horizontal_irradiance: Diffuse horizontal irradiance (W/m2).
            north_angle: North angle in degrees. A number between -360 and 360 for the
                counterclockwise difference between the North and the positive Y-axis in
                degrees. 90 is West and 270 is East (Default: 0).
            ground_reflectance: Average ground reflectance (Default: 0.2).
        """
        assert isinstance(wea, Wea), \
            'wea must be from type Wea not {}'.format(type(wea))
        location = wea.location
        direct_normal_irradiance, diffuse_horizontal_irradiance = \
            wea.get_irradiance_value(month, day, hour)
        return cls.from_lat_long(
            location.latitude, location.longitude, location.time_zone, month, day, hour,
            direct_normal_irradiance, diffuse_horizontal_irradiance, north_angle,
            ground_reflectance)

    @classmethod
    def from_epw(cls, epw, month, day, hour, north_angle=0, ground_reflectance=0.2):
        """Create a standard climate-based sky from a EPW.

        Args:
            epw: A Ladybug EPW objects.
            month: An intger between 1-12 for month.
            day: An intger between 1 to 28-31 depending on the input month.
            hour: A float number larger or equal to 0 and smaller than 24.
            direct_normal_irradiance: Direct normal irradiance (W/m2).
            diffuse_horizontal_irradiance: Diffuse horizontal irradiance (W/m2).
            north_angle: North angle in degrees. A number between -360 and 360 for the
                counterclockwise difference between the North and the positive Y-axis in
                degrees. 90 is West and 270 is East (Default: 0).
            ground_reflectance: Average ground reflectance (Default: 0.2).
        """
        assert isinstance(epw, EPW), \
            'epw must be from type EPW not {}'.format(type(epw))
        location = epw.location
        hoy = int(DateTime(month, day, hour).hoy)
        direct_normal_irradiance = epw.direct_normal_radiation[hoy]
        diffuse_horizontal_irradiance = epw.diffuse_horizontal_radiation[hoy]

        return cls.from_lat_long(
            location.latitude, location.longitude, location.time_zone, month, day, hour,
            direct_normal_irradiance, diffuse_horizontal_irradiance, north_angle,
            ground_reflectance)

    @classmethod
    def from_dict(cls, data):
        """Create the sky from a dictionary.

        Args:
            data: A python dictionary in the following format

        .. code-block:: python

            {
                'type': 'ClimateBased',
                'altitude': 0.0,
                'azimuth': 0.0,
                'direct_normal_irradiance': 0,
                'diffuse_horizontal_irradiance': 0,
                'ground_reflectance': 0.2,
                'ground_hemisphere': {},  # see ground.Ground class [optional],
                'sky_hemisphere': {}  # see hemisphere.Hemisphere class [optional]
            }

        """
        assert 'type' in data, \
            'Input dict is missing type. Not a valid ClimateBased dictionary.'
        assert data['type'] == 'ClimateBased', \
            'Input type must be ClimateBased not %s' % data['type']

        sky = cls(
            data['altitude'],
            data['azimuth'],
            data['direct_normal_irradiance'],
            data['diffuse_horizontal_irradiance'],
            data['ground_reflectance']
        )

        if 'ground_hemisphere' in data and data['ground_hemisphere'] is not None:
            sky._ground_hemisphere = Ground.from_dict(data['ground_hemisphere'])

        if 'sky_hemisphere' in data and data['sky_hemisphere'] is not None:
            sky._sky_hemisphere = Hemisphere.from_dict(data['sky_hemisphere'])

        return sky

    # TODO: add support for additional parameters
    # TODO: add gendaylit to radiance-command and use it for validating inputs
    def to_radiance(self, output_type=0):
        """Return Radiance description of the sky.

        Args:
            output_type: An integer between 0 to 2 for output type.
                * 0 = output in W/m2/sr visible (default)
                * 1 = output in W/m2/sr solar
                * 2 = outputin lm/m2/sr luminance
        """
        output = typing.int_in_range(output_type, 0, 2, 'Sky output type')
        command = '!gendaylit -ang %.6f %.6f -O%d -W %d %d -g %.3f' % (
            self.altitude, self.azimuth - 180.0, output, self.direct_normal_irradiance,
            self._diffuse_horizontal_irradiance, self.ground_reflectance
        )

        return '%s\n\n%s\n\n%s\n' % (
            command, self.sky_hemisphere, self.ground_hemisphere
        )

    def to_dict(self):
        """Translate sky to a dictionary."""
        return {
            'type': 'ClimateBased',
            'altitude': self.altitude,
            'azimuth': self.azimuth,
            'direct_normal_irradiance': self.direct_normal_irradiance,
            'diffuse_horizontal_irradiance': self.diffuse_horizontal_irradiance,
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
            else '%.3f_%.3f_%d_%d.sky' % (
                self.altitude, self.azimuth,
                self.direct_normal_irradiance, self.diffuse_horizontal_irradiance
        )
        return futil.write_to_file_by_name(folder, name, content, mkdir)

    def __eq__(self, value):
        if type(value) != type(self) \
            or value.altitude != self.altitude \
            or value.azimuth != self.azimuth \
            or value.direct_normal_irradiance != self.direct_normal_irradiance \
            or value.diffuse_horizontal_irradiance != \
            self.diffuse_horizontal_irradiance \
            or self.ground_reflectance != value.ground_reflectance \
            or self.ground_hemisphere != value.ground_hemisphere \
                or self.sky_hemisphere != value.sky_hemisphere:
            return False
        return True

    def __ne__(self, value):
        return not self.__eq__(value)
