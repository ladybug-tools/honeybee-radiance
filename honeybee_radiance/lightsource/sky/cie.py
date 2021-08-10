"""Generate CIE standard sky."""
from __future__ import division
import argparse
import shlex

import ladybug.futil as futil
from ladybug.dt import DateTime
from ladybug.location import Location
from ladybug.sunpath import Sunpath
import honeybee.typing as typing

from ._skybase import _PointInTime


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
            latitude: Location latitude between -90 (south) and 90 (north).
            longitude: Location longitude between -180 (west) and 180 (east).
            time_zone: Time zone between -12 hours (west) and +14 hours (east). If
                None, the time will be interpreted as solar time at the given longitude.
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
                'sky_type': 0,  # optional integer for sky type
                'ground_reflectance': 0.2  # optional fraction for ground reflectance
            }

        """
        assert 'type' in data, \
            'Input dict is missing type. Not a valid CIE dictionary.'
        assert data['type'] == 'CIE', \
            'Input type must be CIE not %s' % data['type']

        st = data['sky_type'] if 'sky_type' in data else 0
        gr = data['ground_reflectance'] if 'ground_reflectance' in data else 0.2
        return cls(data['altitude'], data['azimuth'], st, gr)

    @classmethod
    def from_string(cls, sky_string):
        """Create a CIE sky from a string.

        Args:
            sky_string: A text string representing a CIE sky. This can be a minimal
                representation of the sky (eg. "cie -alt 71.6 -az 185.2 -type 0").
                Or it can be a detailed specification of time and location (eg.
                "cie 21 Jun 12:00 -lat 41.78 -lon -87.75 -type 0"). The "-type"
                property of CIE skies is optional and, if unspecified, it
                defaults to 0 (Sunny with Sun).
                Any sky string can optionally have a "-g" property of a fractional
                number, which sets the reflectance of the ground. If unspecified,
                the ground will have a reflectance of 0.2. The detailed string can
                optionally have a "-tz" property with an integer between -12 and +14
                to denote the time zone. If unspecified, the time will be interpreted
                as solar time at the given longitude. The detailed string can also
                have a "-n" property between 0 and 360 to set the counterclockwise
                difference between the North and the positive Y-axis in degrees.
                All other properties specified in the string are required.

        Usage:

        .. code-block:: python

            # minimal string representation of the sky
            sky_string = "cie -alt 71.6 -az 185.2 -type 2"
            sky = CIE.from_string(sky_string)

            # detailed location-specific representation of the sky
            sky_string = "cie 21 Jun 12:00 -lat 41.78 -lon -87.75 -tz -6"
            sky = CIE.from_string(sky_string)
        """
        # check the input and parse the datetime if it exists
        lower_str = sky_string.lower()
        assert lower_str.startswith('cie'), 'Expected string representation ' \
            'of CIE sky "{}" to start with "cie".'.format(sky_string)
        split_str = shlex.split(lower_str)
        try:
            dtime = DateTime.from_date_time_string(' '.join(split_str[1:4]))
        except (ValueError, IndexError):  # simpler sky representation
            dtime = None

        # make a parser for all of the other sky properties
        pars = argparse.ArgumentParser()
        pars.add_argument('-type', action='store', dest='type', type=int, default=0)
        pars.add_argument('-g', action='store', dest='g', type=float, default=0.2)

        # create the sky object
        if dtime is None:
            pars.add_argument('-alt', action='store', dest='alt', type=float, default=90)
            pars.add_argument('-az', action='store', dest='az', type=float, default=0)
            props = pars.parse_args(split_str[1:])
            return cls(props.alt, props.az, props.type, props.g)
        else:
            pars.add_argument('-lat', action='store', dest='lat', type=float, default=0)
            pars.add_argument('-lon', action='store', dest='lon', type=float, default=0)
            pars.add_argument('-tz', action='store', dest='tz', type=int, default=0)
            pars.add_argument('-n', action='store', dest='n', type=float, default=0)
            props = pars.parse_args(split_str[4:])
            return cls.from_lat_long(
                props.lat, props.lon, props.tz, dtime.month, dtime.day,
                dtime.float_hour, props.type, props.n, props.g)

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
            'ground_reflectance': self.ground_reflectance
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

    def __repr__(self):
        """Sky representation."""
        return 'cie -alt {} -az {} -type {} -g {}'.format(
            self.altitude, self.azimuth, self.sky_type, self.ground_reflectance)
