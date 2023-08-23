"""Generate a point-in-time climate-based sky."""
from __future__ import division
import argparse
import shlex

import ladybug.futil as futil
from ladybug.dt import DateTime
from ladybug.analysisperiod import AnalysisPeriod
from ladybug.location import Location
from ladybug.sunpath import Sunpath
from ladybug.wea import Wea
from ladybug.epw import EPW
import honeybee.typing as typing

from ._skybase import _PointInTime


class ClimateBased(_PointInTime):
    """Point-in-time Climate-based sky.

    The output of Climatebased sky is similar to using command Radiance's gendaylit
    command. For more information see gendaylit documentation.

    Args:
        altitude: Solar altitude. The altitude is measured in degrees above the horizon.
        azimuth: Solar azimuth. The azimuth is measured in degrees east of North.
            East is 90, South is 180 and West is 270. Note that this input is
            different from the Radiance convention. In Radiance the azimuth degrees
            are measured in west of South.
        direct_normal_irradiance: Direct normal irradiance (W/m2).
        diffuse_horizontal_irradiance: Diffuse horizontal irradiance (W/m2).
        ground_reflectance: Average ground reflectance (Default: 0.2).
        is_colored: Boolean to note whether the sky will be rendered in full
            color (True) or it will simple be a grey sky with the same average
            value as the colored sky (False). (Default: False).

    Properties:
        * altitude
        * azimuth
        * direct_normal_irradiance
        * diffuse_horizontal_irradiance
        * ground_hemisphere
        * sky_hemisphere
        * ground_reflectance
        * is_colored
        * is_point_in_time
        * is_climate_based
    """

    __slots__ = (
        '_altitude', '_azimuth', '_diffuse_horizontal_irradiance',
        '_direct_normal_irradiance', '_is_colored'
    )

    def __init__(
            self, altitude, azimuth,
            direct_normal_irradiance, diffuse_horizontal_irradiance,
            ground_reflectance=0.2, is_colored=False
        ):
        """Create a climate-based standard sky."""
        _PointInTime.__init__(self, ground_reflectance)
        self.altitude = altitude
        self.azimuth = azimuth
        self.direct_normal_irradiance = direct_normal_irradiance
        self.diffuse_horizontal_irradiance = diffuse_horizontal_irradiance
        self.is_colored = is_colored

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
        """Get or set direct normal irradiance (W/m2).
        """
        return self._direct_normal_irradiance

    @direct_normal_irradiance.setter
    def direct_normal_irradiance(self, value):
        value = typing.int_positive(value, 'Direct normal irradiance')
        self._direct_normal_irradiance = value

    @property
    def diffuse_horizontal_irradiance(self):
        """Get or set diffuse horizontal irradiance (W/m2).
        """
        return self._diffuse_horizontal_irradiance

    @diffuse_horizontal_irradiance.setter
    def diffuse_horizontal_irradiance(self, value):
        value = typing.int_positive(value, 'Diffuse horizontal irradiance')
        self._diffuse_horizontal_irradiance = value

    @property
    def is_colored(self):
        """Get or set a boolean for whether the sky is rendered in full color."""
        return self._is_colored

    @is_colored.setter
    def is_colored(self, value):
        self._is_colored = bool(value)

    @property
    def is_climate_based(self):
        """Return True if the sky is created based on values from weather data."""
        return True

    @classmethod
    def from_lat_long(
        cls, latitude, longitude, time_zone, month, day, hour,
        direct_normal_irradiance, diffuse_horizontal_irradiance,
        north_angle=0, ground_reflectance=0.2, is_colored=False
    ):
        """Create a climate based sky from latitude, longitude and a date/time.

        Args:
            latitude: Location latitude between -90 and 90.
            longitude: Location longitude between -180 (west) and 180 (east).
            time_zone: Time zone between -12 hours (west) and +14 hours (east). If
                None, the time will be interpreted as solar time at the given longitude.
            month: An integer between 1-12 for month.
            day: An integer between 1 to 28-31 depending on the input month.
            hour: A float number larger or equal to 0 and smaller than 24.
            direct_normal_irradiance: Direct normal irradiance (W/m2).
            diffuse_horizontal_irradiance: Diffuse horizontal irradiance (W/m2).
            north_angle: North angle in degrees. A number between -360 and 360 for the
                counterclockwise difference between the North and the positive Y-axis in
                degrees. 90 is West and 270 is East (Default: 0).
            ground_reflectance: Average ground reflectance (Default: 0.2).
            is_colored: Boolean to note whether the sky will be rendered in full
                color (True) or it will simple be a grey sky with the same average
                value as the colored sky (False). (Default: False).
        """
        #  calculate altitude and azimuth using ladybug's sunpath
        sp = Sunpath(latitude, longitude, time_zone, north_angle)
        sun = sp.calculate_sun(month, day, hour)
        return cls(
            sun.altitude, sun.azimuth_from_y_axis,
            direct_normal_irradiance, diffuse_horizontal_irradiance,
            ground_reflectance, is_colored
        )

    @classmethod
    def from_location(
        cls, location, month, day, hour,
        direct_normal_irradiance, diffuse_horizontal_irradiance,
        north_angle=0, ground_reflectance=0.2, is_colored=False
    ):
        """Create a standard climate-based sky for a location.

        Args:
            location: A Ladybug location.
            month: An integer between 1-12 for month.
            day: An integer between 1 to 28-31 depending on the input month.
            hour: A float number larger or equal to 0 and smaller than 24.
            direct_normal_irradiance: Direct normal irradiance (W/m2).
            diffuse_horizontal_irradiance: Diffuse horizontal irradiance (W/m2).
            north_angle: North angle in degrees. A number between -360 and 360 for the
                counterclockwise difference between the North and the positive Y-axis in
                degrees. 90 is West and 270 is East (Default: 0).
            ground_reflectance: Average ground reflectance (Default: 0.2).
            is_colored: Boolean to note whether the sky will be rendered in full
                color (True) or it will simple be a grey sky with the same average
                value as the colored sky (False). (Default: False).
        """
        assert isinstance(location, Location), \
            'location must be from type Location not {}'.format(type(location))
        return cls.from_lat_long(
            location.latitude, location.longitude, location.time_zone, month, day, hour,
            direct_normal_irradiance, diffuse_horizontal_irradiance, north_angle,
            ground_reflectance, is_colored)

    @classmethod
    def from_wea(
        cls, wea, month, day, hour, north_angle=0,
        ground_reflectance=0.2, is_colored=False
    ):
        """Create a standard climate-based sky from a Wea.

        Args:
            wea: A Ladybug wea object.
            month: An integer between 1-12 for month.
            day: An integer between 1 to 28-31 depending on the input month.
            hour: A float number larger or equal to 0 and smaller than 24.
            north_angle: North angle in degrees. A number between -360 and 360 for the
                counterclockwise difference between the North and the positive Y-axis in
                degrees. 90 is West and 270 is East (Default: 0).
            ground_reflectance: Average ground reflectance (Default: 0.2).
            is_colored: Boolean to note whether the sky will be rendered in full
                color (True) or it will simple be a grey sky with the same average
                value as the colored sky (False). (Default: False).
        """
        assert isinstance(wea, Wea), \
            'wea must be from type Wea not {}'.format(type(wea))
        location = wea.location
        direct_normal_irradiance, diffuse_horizontal_irradiance = \
            wea.get_irradiance_value(month, day, hour)
        return cls.from_lat_long(
            location.latitude, location.longitude, location.time_zone, month, day, hour,
            direct_normal_irradiance, diffuse_horizontal_irradiance, north_angle,
            ground_reflectance, is_colored)

    @classmethod
    def from_wea_monthly_average(
        cls, wea, month, hour, north_angle=0, ground_reflectance=0.2, is_colored=False
    ):
        """Create a monthly averaged climate-based sky from a Wea and a hour of the day.

        Args:
            wea: A Ladybug wea object.
            month: An integer between 1-12 for month.
            hour: A float number larger or equal to 0 and smaller than 24.
            north_angle: North angle in degrees. A number between -360 and 360 for the
                counterclockwise difference between the North and the positive Y-axis in
                degrees. 90 is West and 270 is East (Default: 0).
            ground_reflectance: Average ground reflectance (Default: 0.2).
            is_colored: Boolean to note whether the sky will be rendered in full
                color (True) or it will simple be a grey sky with the same average
                value as the colored sky (False). (Default: False).
        """
        assert isinstance(wea, Wea), \
            'wea must be from type Wea not {}'.format(type(wea))
        a_period = AnalysisPeriod(
            st_month=month, st_hour=hour, end_month=month, end_hour=hour,
            timestep=wea.timestep, is_leap_year=wea.is_leap_year)
        filtered_wea = wea.filter_by_analysis_period(a_period)
        location = wea.location
        dir_normal_irradiance = filtered_wea.direct_normal_irradiance.average
        dif_horizontal_irradiance = filtered_wea.diffuse_horizontal_irradiance.average
        return cls.from_lat_long(
            location.latitude, location.longitude, location.time_zone, month, 15, hour,
            dir_normal_irradiance, dif_horizontal_irradiance, north_angle,
            ground_reflectance, is_colored)

    @classmethod
    def from_epw(
        cls, epw, month, day, hour, north_angle=0,
        ground_reflectance=0.2, is_colored=False
    ):
        """Create a standard climate-based sky from a EPW.

        Args:
            epw: A Ladybug EPW objects.
            month: An integer between 1-12 for month.
            day: An integer between 1 to 28-31 depending on the input month.
            hour: A float number larger or equal to 0 and smaller than 24.
            north_angle: North angle in degrees. A number between -360 and 360 for the
                counterclockwise difference between the North and the positive Y-axis in
                degrees. 90 is West and 270 is East (Default: 0).
            ground_reflectance: Average ground reflectance (Default: 0.2).
            is_colored: Boolean to note whether the sky will be rendered in full
                color (True) or it will simple be a grey sky with the same average
                value as the colored sky (False). (Default: False).
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
            ground_reflectance, is_colored)

    @classmethod
    def from_epw_monthly_average(
        cls, epw, month, hour, north_angle=0, ground_reflectance=0.2, is_colored=False
    ):
        """Create a monthly averaged climate-based sky from an EPW and a hour of the day.

        Args:
            epw: A Ladybug EPW objects.
            month: An integer between 1-12 for month.
            hour: A float number larger or equal to 0 and smaller than 24.
            north_angle: North angle in degrees. A number between -360 and 360 for the
                counterclockwise difference between the North and the positive Y-axis in
                degrees. 90 is West and 270 is East (Default: 0).
            ground_reflectance: Average ground reflectance (Default: 0.2).
            is_colored: Boolean to note whether the sky will be rendered in full
                color (True) or it will simple be a grey sky with the same average
                value as the colored sky (False). (Default: False).
        """
        assert isinstance(epw, EPW), \
            'epw must be from type EPW not {}'.format(type(epw))
        location = epw.location
        a_period = AnalysisPeriod(
            st_month=month, st_hour=hour, end_month=month, end_hour=hour,
            is_leap_year=epw.is_leap_year)
        dn = epw.direct_normal_radiation.filter_by_analysis_period(a_period).average
        dh = epw.diffuse_horizontal_radiation.filter_by_analysis_period(a_period).average
        return cls.from_lat_long(
            location.latitude, location.longitude, location.time_zone, month, 15, hour,
            dn, dh, north_angle, ground_reflectance, is_colored)

    @classmethod
    def from_dict(cls, data):
        """Create a ClimateBased sky from a dictionary.

        Args:
            data: A python dictionary in the following format

        .. code-block:: python

            {
                'type': 'ClimateBased',
                'altitude': 0.0,
                'azimuth': 0.0,
                'direct_normal_irradiance': 800,
                'diffuse_horizontal_irradiance': 120,
                'ground_reflectance': 0.2,  # optional float for ground reflectance
                'is_colored': True  # boolean for whether the sky is colored
            }

        """
        assert 'type' in data, \
            'Input dict is missing type. Not a valid ClimateBased dictionary.'
        assert data['type'] == 'ClimateBased', \
            'Input type must be ClimateBased not %s' % data['type']

        gr = data['ground_reflectance'] if 'ground_reflectance' in data else 0.2
        ic = data['is_colored'] if 'is_colored' in data else False
        return cls(
            data['altitude'], data['azimuth'],
            data['direct_normal_irradiance'], data['diffuse_horizontal_irradiance'],
            gr, ic
        )

    @classmethod
    def from_string(cls, sky_string):
        """Create a ClimateBased sky from a string.

        Args:
            sky_string: A text string representing a ClimateBased sky. This can
                either be a minimal string representation of the sky (eg.
                "climate-based -alt 71.6 -az 185.2 -dni 800 -dhi 120").
                Or it can be a detailed specification of time and location (eg.
                "climate-based 21 Jun 12:00 -lat 41.78 -lon -87.75 -dni 800 -dhi 120").
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
            sky_string = "climate-based -alt 71.6 -az 185.2 -dni 800 -dhi 120"
            sky = ClimateBased.from_string(sky_string)

            # detailed location-specific representation of the sky
            sky_string = "climate-based 21 Jun 12:00 -lat 41.78 -lon -87.75 -tz -6 " \
                " -dni 800 -dhi 120 -n 0 -g 0.2"
            sky = ClimateBased.from_string(sky_string)
        """
        # check the input and parse the datetime if it exists
        lower_str = sky_string.lower()
        assert lower_str.startswith('climate-based'), 'Expected string representation ' \
            'of ClimateBased sky "{}" to start with "climate-based".'.format(sky_string)
        split_str = shlex.split(lower_str)
        try:
            dtime = DateTime.from_date_time_string(' '.join(split_str[1:4]))
        except (ValueError, IndexError):  # simpler sky representation
            dtime = None

        # make a parser for all of the other sky properties
        pars = argparse.ArgumentParser()
        pars.add_argument('-dni', action='store', dest='dni', type=float, default=0)
        pars.add_argument('-dhi', action='store', dest='dhi', type=float, default=0)
        pars.add_argument('-g', action='store', dest='g', type=float, default=0.2)
        pars.add_argument('-c', action='store_true', dest='c', default=False)

        # create the sky object
        if dtime is None:
            pars.add_argument('-alt', action='store', dest='alt', type=float, default=90)
            pars.add_argument('-az', action='store', dest='az', type=float, default=0)
            props = pars.parse_args(split_str[1:])
            return cls(props.alt, props.az, props.dni, props.dhi, props.g, props.c)
        else:
            pars.add_argument('-lat', action='store', dest='lat', type=float, default=0)
            pars.add_argument('-lon', action='store', dest='lon', type=float, default=0)
            pars.add_argument('-tz', action='store', dest='tz', type=int, default=0)
            pars.add_argument('-n', action='store', dest='n', type=float, default=0)
            props = pars.parse_args(split_str[4:])
            return cls.from_lat_long(
                props.lat, props.lon, props.tz, dtime.month, dtime.day,
                dtime.float_hour, props.dni, props.dhi, props.n, props.g, props.c)

    # TODO: add support for additional parameters
    # TODO: add gendaylit to radiance-command and use it for validating inputs
    def to_radiance(self, output_type=0):
        """Return Radiance description of the sky.

        Args:
            output_type: An integer between 0 to 2 for output type.
                * 0 = output in W/m2/sr visible (default)
                * 1 = output in W/m2/sr solar
                * 2 = output in lm/m2/sr luminance
        """
        full_color = ' -C' if self.is_colored else ''
        output = typing.int_in_range(output_type, 0, 2, 'Sky output type')
        command = '!gendaylit -ang %.6f %.6f -O %d -W %d %d -g %.3f%s' % (
            self.altitude, self.azimuth - 180.0, output, self.direct_normal_irradiance,
            self._diffuse_horizontal_irradiance, self.ground_reflectance, full_color
        )

        return '%s\n\n%s\n\n%s\n' % (
            command, self.sky_hemisphere, self.ground_hemisphere
        )

    def to_dict(self):
        """Translate sky to a dictionary."""
        base = {
            'type': 'ClimateBased',
            'altitude': self.altitude,
            'azimuth': self.azimuth,
            'direct_normal_irradiance': self.direct_normal_irradiance,
            'diffuse_horizontal_irradiance': self.diffuse_horizontal_irradiance,
            'ground_reflectance': self.ground_reflectance,
            'ground_hemisphere': self.ground_hemisphere.to_dict(),
            'sky_hemisphere': self.sky_hemisphere.to_dict()
        }
        if self.is_colored:
            base['is_colored'] = True
        return base

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
            or self.is_colored != value.is_colored \
            or self.ground_hemisphere != value.ground_hemisphere \
                or self.sky_hemisphere != value.sky_hemisphere:
            return False
        return True

    def __ne__(self, value):
        return not self.__eq__(value)

    def __repr__(self):
        """Sky representation."""
        is_colored = ' -c' if self.is_colored else ''
        return 'climate-based -alt {} -az {} -dni {} -dhi {} -g {}{}'.format(
            self.altitude, self.azimuth,
            self.direct_normal_irradiance, self.diffuse_horizontal_irradiance,
            self.ground_reflectance, is_colored
        )
