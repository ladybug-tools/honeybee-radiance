"""A Radiance-based sunpath.

A Radiance-based sunpath is a list of light sources with radius of 0.533


A sunpath can be climate-based or non-climate-based. In non climate-based sunpath
irradiance values are set to 1e6 for red, green and blue channels.

Use the climate-based sunpath for direct solar radiation studies and use the
non climate-based sunpath for solaraccess studies.

"""

from ..modifier.material import Light
from ..geometry import Source
from ._gendaylit import gendaylit

from ladybug.sunpath import Sunpath as LBSunpath
from ladybug.location import Location
from ladybug.wea import Wea

import os
import warnings

try:
    from itertools import izip as zip
    writemode = 'wb'
except ImportError:
    # python 3
    writemode = 'w'


class Sunpath(object):
    """A Radiance-based sun-path.

    Args:
        location: A Ladybug location.
        north: Sunpath north angle.

    Properties:
        * location
        * north
    """
    __slots__ = ('_location', '_north')

    def __init__(self, location, north=0):
        self.location = location
        self.north = north

    @property
    def location(self):
        """Sunpath location."""
        return self._location

    @location.setter
    def location(self, loc):
        assert isinstance(loc, Location), \
            'Location must be a Ladybug Location not %s' % type(loc)
        self._location = loc

    @property
    def north(self):
        """Sunpath north angle."""
        return self._north

    @north.setter
    def north(self, n):
        assert isinstance(n, (int, float)), 'north must be a numerical value.'
        self._north = n

    def _solar_calc(self, hoys, wea, output_type, leap_year=False,
                    reverse_vectors=False):
        """Calculate ."""
        solar_calc = LBSunpath.from_location(self.location, self.north)
        solar_calc.is_leap_year = leap_year

        if not hoys:
            # set hours to an annual hourly sunpath
            hoys = range(8760) if not leap_year else range(8760 + 24)

        sun_up_hours = []
        sun_vectors = []
        radiance_values = []
        altitudes = []
        for hour in hoys:
            sun = solar_calc.calculate_sun_from_hoy(hour)
            if sun.altitude < 0:
                continue
            sun_vectors.append(sun.sun_vector)
            sun_up_hours.append(hour)
            altitudes.append(sun.altitude)
        # calculate irradiance value
        if wea:
            # this is a climate_based sunpath. Get the values from wea
            assert isinstance(wea, Wea), 'Expected Wea not %s' % type(wea)

            for altitude, hoy in zip(altitudes, sun_up_hours):
                dnr, dhr = wea.get_irradiance_value_for_hoy(hoy)
                if dnr == 0:
                    radiance_value = 0
                else:
                    radiance_value = gendaylit(
                        altitude, hoy, dnr, dhr, output_type, leap_year)
                radiance_values.append(int(radiance_value))
        else:
            radiance_values = [1e6] * len(sun_up_hours)

        if reverse_vectors:
            sun_vectors = [v.reverse() for v in sun_vectors]

        return sun_vectors, sun_up_hours, radiance_values

    def to_file(self, folder='.', file_name='sunpath', hoys=None, wea=None,
                output_type=0, leap_year=False, reverse_vectors=False,
                split_mod_files=True):
        r"""Write sunpath to file.

        This method will generate a sunpath file and one or several files for sun
        modifiers.

        In sunpath file each sun is defined as a radiance source in a separate line. The
        naming is based on the minute of the year.

        void light {sol_moy} 0 0 3 {irr} {irr} {irr} {sol_moy} source {sun_moy} 0 0 4 x y z 0.533

        This method also generate a mod file which includes all the modifiers in sunpath.
        mod file is usually used with rcontrib command to indicate the list of modifiers.
        Since rcontrib command has a hard limit of 10,000 modifiers in a single run you
        can use split_mod_files to split the modifier files not to exceed 10,000
        modifiers.

        Args:
            folder: Target folder to write the sunpath files (default: '.')
            file_name: Optional file name for generated files. By default files will be
                named as sunpath.rad and sunpath.mod.
            hoys: An optional list of hoys to be included in sunpath. By default sunpath
                includes all the sun up hours during the year.
            wea: A Ladybug wea. If wea is provided a climate-based sunpath will be
                generated otherwise all suns will be assigned the same value of 1e6.
            output_type: An integer between 0-2. 0=output in W/m^2/sr visible,
                1=output in W/m^2/sr solar, 2=output in candela/m^2 (default: 0).
            leap_year: Set to True if hoys are for a leap year (default: False).
            reverse_vector: Set to True to reverse the vector direction of suns. By
                default sun vectors are coming from sun towards the ground. This option
                will reverse the direction of the vectors. Reversed sunpath is mainly
                useful for radiation studies (default: False).
            split_mod_files: A boolean to split the modifer file into multiple files to
                ensure none of them includes more than 10,000 modifiers.

        Returns:
            dict -- A dictionary with with two keys for sunpath and suns. sunpath returns
            the path to the sunpath file and suns returns a list of path to modifier
            files.
        """
        sun_vectors, sun_up_hours, radiance_values = \
            self._solar_calc(hoys, wea, output_type, leap_year, reverse_vectors)

        if not os.path.isdir(folder):
            os.makedirs(folder)

        file_name = file_name or 'sunpath'
        # write them to files
        fp = os.path.join(folder, file_name + '.rad')
        if not wea:
            if output_type != 0:
                warnings.warn(
                    'Output type will not affect a non climate-base sunpath.'
                    ' To create a climate-based sunpath you must provide the weather'
                    ' data.'
                )

        suns = []
        with open(fp, writemode) as outf:
            for vector, hoy, irr in zip(sun_vectors, sun_up_hours, radiance_values):
                # use minute of the year to name sun positions
                moy = int(round(hoy * 60))
                mat = Light('sol_%06d' % moy, irr, irr, irr)
                sun = Source('sun_%06d' % moy, vector, 0.533, mat)
                outf.write(sun.to_radiance(True).replace('\n', ' ') + '\n')
                suns.append('sol_%06d' % moy)

        file_count = int(len(suns) / 10000) + 1 if split_mod_files else 1

        if file_count != 1:
            length = int(round(len(suns) / file_count))
            sun_files = [
                os.path.join(folder, '%s_%d.mod' % (file_name, count))
                for count in range(file_count)
            ]
        else:
            length = len(suns)
            sun_files = [os.path.join(folder, '%s.mod' % file_name)]

        open_files = [open(sfp, 'w') for sfp in sun_files]

        try:
            for count, sun in enumerate(suns):
                file_index = min(int(count / length), file_count - 1)
                open_files[file_index].write(sun + '\n')
        except Exception as e:
            raise ValueError(e)
        finally:
            for f in open_files:
                f.close()

        return {'sunpath': fp, 'suns': sun_files}

    def to_dict(self):
        """Convert this sunpath to a dictionary.

        Args:
            input_dict: A python dictionary in the following format

        .. code-block:: python

            {
            'type': 'Sunpath',
            'location': {}  # Location dictionary,
            'north': 0,
            }
        """
        return {
            'type': 'Sunpath',
            'location': self.location.to_dict(),
            'north': self.north
        }

    @classmethod
    def from_dict(cls, data):
        """Create a sunpath from a dictionary.

        Dictionary keys are type, location and north.
        """
        assert 'type' in data, 'type key is missing.'
        assert data['type'] == 'Sunpath', 'Expected type Sunpath not %s' % data['type']

        assert 'location' in data, 'location key is missing.'
        location = Location.from_dict(data['location'])
        north = dict.get('north')
        return cls(location, north)

    def ToString(self):
        """Overwrite .NET ToString method."""
        return self.__repr__()

    def __repr__(self):
        """Sunpath representation."""
        return "Sunpath: %s" % self.location.city
