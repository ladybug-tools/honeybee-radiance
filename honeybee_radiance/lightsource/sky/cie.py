"""Generate CIE standard sky."""
from __future__ import division
from ._skybase import _PointInTime
from .hemisphere import Hemisphere
from ..ground import Ground
import honeybee.typing as typing
import ladybug.futil as futil
from ladybug.location import Location
from ladybug.sunpath import Sunpath


class CIE(_PointInTime):
    """CIE sky.

    The output of CIE sky is similar to using Radiance's gensky command. For more
    information see gensky documentation.

    Args:
        altitude: Solar altitude. The altitude is measured in degrees above the horizon.
        azimuth: Solar azimuth. The azimuth is measured in degrees east of North. East is
            90, South is 180 and West is 270. Note that this input is different from
            Radiance convention. In Radiance the azimuth degrees are measured in west of
            South.
        sky_type: An integer between 0..5 to indicate CIE Sky Type.
            * 0 = Sunny with sun. Sunny sky with sun. In addition to the sky distribution
            function, a source description of the sun is generated.
            * 1 = Sunny without sun. Sunny sky without sun. The sky distribution will
            correspond to a standard CIE clear day.
            * 2 = Intermediate with sun. In addition to the sky distribution, a (somewhat
            subdued) sun is generated.
            * 3 = Intermediate without sun. The sky will correspond to a standard CIE
            intermediate day.
            * 4 = Cloudy sky. The sky distribution will correspond to a standard CIE
            overcast day.
            * 5 = Uniform cloudy sky. The sky distribution will be completely uniform.
        ground_reflectance: Average ground reflectance (Default: 0.2).

    Properties:
        * altitude
        * azimuth
        * sky_type
        * sky_type_radiance
        * sky_type_human_readable
        * ground_hemisphere
        * sky_hemisphere
        * ground_reflectance
        * is_point_in_time
        * is_climate_based
    """

    SKYTYPES = {
        0: ('+s', 'Sunny sky with sun'),
        1: ('-s', 'Sunny sky without sun'),
        2: ('+i', 'intermediate sky with sun'),
        3: ('-i', 'intermediate sky without sun'),
        4: ('-c', 'Cloudy sky'),
        5: ('-u', 'Uniform cloudy sky')
    }

    __slots__ = ('_altitude', '_azimuth', '_sky_type')

    def __init__(self, altitude, azimuth, sky_type=0, ground_reflectance=0.2):
        """Create a CIE standard sky."""
        _PointInTime.__init__(self, ground_reflectance)
        self.altitude = altitude
        self.azimuth = azimuth
        self.sky_type = sky_type

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
    def sky_type(self):
        """Get and set sky type.

        An integer between 0 and 5 to indicate CIE Sky Type.

        * 0 = Sunny with sun. Sunny sky with sun. In addition to the sky distribution
        function, a source description of the sun is generated.
        * 1 = Sunny without sun. Sunny sky without sun. The sky distribution will
        correspond to a standard CIE clear day.
        * 2 = Intermediate with sun. In addition to the sky distribution, a (somewhat
        subdued) sun is generated.
        * 3 = Intermediate without sun. The sky will correspond to a standard CIE
        intermediate day.
        * 4 = Cloudy sky. The sky distribution will correspond to a standard CIE
        overcast day.
        * 5 = Uniform cloudy sky. The sky distribution will be completely uniform.
        """
        return self._sky_type

    @sky_type.setter
    def sky_type(self, value):
        value = typing.int_in_range(value, 0, 5, 'CIE sky type')
        self._sky_type = value

    @property
    def sky_type_human_readable(self):
        """A human readable description of sky type."""
        return self.SKYTYPES[self.sky_type][1]

    @property
    def sky_type_radiance(self):
        """Sky type in Radiance format.

        * +s = Sunny with sun. Sunny sky with sun. In addition to the sky distribution
        function, a source description of the sun is generated.
        * -s = Sunny without sun. Sunny sky without sun. The sky distribution will
        correspond to a standard CIE clear day.
        * +i = Intermediate with sun. In addition to the sky distribution, a (somewhat
        subdued) sun is generated.
        * -i = Intermediate without sun. The sky will correspond to a standard CIE
        intermediate day.
        * -c = Cloudy sky. The sky distribution will correspond to a standard CIE
        overcast day.
        * -u = Uniform cloudy sky. The sky distribution will be completely uniform.
        """
        return self.SKYTYPES[self.sky_type][0]

    @classmethod
    def from_lat_long(
        cls, latitude, longitude, time_zone, month, day, hour, sky_type=0,
            north_angle=0, ground_reflectance=0.2):
        """Create sky with certain illuminance.

        Args:
            latitude: Location latitude between -90 and 90.
            longitude:Location longitude between -180 (west) and 180 (east).
            timezone: Time zone between -12 hours (west) and +14 hours (east).
            month: An intger between 1-12 for month.
            day: An intger between 1 to 28-31 depending on the input month.
            hour: A float number larger or equal to 0 and smaller than 24.
            sky_type: An integer between 0..5 to indicate CIE Sky Type.
                * 0 = Sunny with sun. Sunny sky with sun. In addition to the sky
                    distribution function, a source description of the sun is generated.
                * 1 = Sunny without sun. Sunny sky without sun. The sky distribution will
                    correspond to a standard CIE clear day.
                * 2 = Intermediate with sun. In addition to the sky distribution, a
                    (somewhat subdued) sun is generated.
                * 3 = Intermediate without sun. The sky will correspond to a standard CIE
                    intermediate day.
                * 4 = Cloudy sky. The sky distribution will correspond to a standard CIE
                    overcast day.
                * 5 = Uniform cloudy sky. The sky distribution will be completely
                    uniform.
            north_angle: North angle in degrees. A number between -360 and 360 for the
                counterclockwise difference between the North and the positive Y-axis in
                degrees. 90 is West and 270 is East (Default: 0).
            ground_reflectance: Average ground reflectance (Default: 0.2).
        """
        #  calculate altitude and azimuth using ladybug's sunpath
        sp = Sunpath(latitude, longitude, time_zone, north_angle)
        sun = sp.calculate_sun(month, day, hour)
        return cls(sun.altitude, sun.azimuth_from_y_axis, sky_type, ground_reflectance)

    @classmethod
    def from_location(cls, location, month, day, hour, sky_type=0,
                      north_angle=0, ground_reflectance=0.2):
        """Create a standard CIE sky for a location.

        Args:
            location: A Ladybug location.
            month: An intger between 1-12 for month.
            day: An intger between 1 to 28-31 depending on the input month.
            hour: A float number larger or equal to 0 and smaller than 24.
            sky_type: An integer between 0..5 to indicate CIE Sky Type.
                * 0 = Sunny with sun. Sunny sky with sun. In addition to the sky
                    distribution function, a source description of the sun is generated.
                * 1 = Sunny without sun. Sunny sky without sun. The sky distribution will
                    correspond to a standard CIE clear day.
                * 2 = Intermediate with sun. In addition to the sky distribution, a
                    (somewhat subdued) sun is generated.
                * 3 = Intermediate without sun. The sky will correspond to a standard CIE
                    intermediate day.
                * 4 = Cloudy sky. The sky distribution will correspond to a standard CIE
                    overcast day.
                * 5 = Uniform cloudy sky. The sky distribution will be completely
                    uniform.
            north_angle: North angle in degrees. A number between -360 and 360 for the
                counterclockwise difference between the North and the positive Y-axis in
                degrees. 90 is West and 270 is East (Default: 0).
            ground_reflectance: Average ground reflectance (Default: 0.2).
        """
        assert isinstance(location, Location), \
            'location must be from type Location not {}'.format(type(location))
        return cls.from_lat_long(
            location.latitude, location.longitude, location.time_zone, month, day, hour,
            sky_type, north_angle, ground_reflectance)

    @classmethod
    def from_dict(cls, data):
        """Create the sky from a dictionary.

        Args:
            data: A python dictionary in the following format

        .. code-block:: python

            {
                'type': 'CIE',
                'altitude': 0.0,
                'azimuth': 0.0,
                'sky_type': 0,
                'ground_reflectance': 0.2,
                'ground_hemisphere': {},  # see ground.Ground class [optional],
                'sky_hemisphere': {}  # see hemisphere.Hemisphere class [optional]
            }

        """
        assert 'type' in data, \
            'Input dict is missing type. Not a valid CIE dictionary.'
        assert data['type'] == 'CIE', \
            'Input type must be CIE not %s' % data['type']

        sky = cls(
            data['altitude'],
            data['azimuth'],
            data['sky_type'],
            data['ground_reflectance']
        )

        if 'ground_hemisphere' in data and data['ground_hemisphere'] is not None:
            sky._ground_hemisphere = Ground.from_dict(data['ground_hemisphere'])

        if 'sky_hemisphere' in data and data['sky_hemisphere'] is not None:
            sky._sky_hemisphere = Hemisphere.from_dict(data['sky_hemisphere'])

        return sky

    # TODO: add support for additional parameters
    # TODO: add gensky to radiance-command and use it for validating inputs
    def to_radiance(self):
        """Return radiance definition as a string."""
        command = '!gensky -ang %.6f %.6f %s -g %.3f' % (
            self.altitude, self.azimuth - 180.0, self.sky_type_radiance,
            self.ground_reflectance
        )

        return '%s\n\n%s\n\n%s\n' % (
            command, self.sky_hemisphere, self.ground_hemisphere
        )

    def to_dict(self):
        """Translate sky to a dictionary."""
        return {
            'type': 'CIE',
            'altitude': self.altitude,
            'azimuth': self.azimuth,
            'sky_type': self.sky_type,
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
            else '%.3f_%.3f_%s.sky' % (
                self.altitude, self.azimuth,
                self.sky_type_human_readable.replace(' ', '_').lower()
        )
        return futil.write_to_file_by_name(folder, name, content, mkdir)

    def __eq__(self, value):
        if type(value) != type(self) \
            or value.altitude != self.altitude \
            or value.azimuth != self.azimuth \
            or value.sky_type != self.sky_type \
            or self.ground_reflectance != value.ground_reflectance \
            or self.ground_hemisphere != value.ground_hemisphere \
                or self.sky_hemisphere != value.sky_hemisphere:
            return False
        return True

    def __ne__(self, value):
        return not self.__eq__(value)
