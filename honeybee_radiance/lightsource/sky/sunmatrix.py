"""Generate a point-in-time climate-based sky."""
from __future__ import division
import honeybee.typing as typing
import ladybug.futil as futil
from ladybug.wea import Wea
from ladybug_geometry.geometry2d.pointvector import Vector2D

import os
import math


class SunMatrix(object):
    """Annual Climate-based Sun matrix.

    The output of SkyMatrix is similar to using command Radiance's gendaymtx command with
    ``-n -D`` options. The options are available in Radiance 5.3 and after that. For more
    information see gendaymtx documentation.

    https://www.radiance-online.org/learning/documentation/manual-pages/pdfs/gendaymtx.pdf

    Args:
        wea: A Ladybug wea object.
        north: A number between -360 and 360 for the counterclockwise difference between
            the North and the positive Y-axis in degrees. 90 is West and 270 is East
            (Default: 0)

    Properties:
        * wea
        * location
        * north
        * is_point_in_time
        * is_climate_based
    """

    __slots__ = ('_wea', '_north')

    def __init__(self, wea, north=0):
        """Create a climate-based sun matrix."""
        self.wea = wea
        self.north = north

    @property
    def wea(self):
        """Get and set wea."""
        return self._wea

    @wea.setter
    def wea(self, value):
        assert isinstance(value, Wea), \
            'wea must be from type Wea not {}'.format(type(value))
        self._wea = value

    @property
    def north(self):
        """Get and set north direction.

        A number between -360 and 360 for the counterclockwise difference between
        the North and the positive Y-axis in degrees. 90 is West and 270 is East.
        """
        return self._north

    @north.setter
    def north(self, value):
        value = typing.float_in_range(value, -360, +360, 'Skymatrix north')
        self._north = value

    @property
    def is_climate_based(self):
        """Return True if the sky is created based on values from weather data."""
        return True

    @property
    def is_point_in_time(self):
        """Return True if the sky is generated for a single point in time."""
        return False

    @property
    def location(self):
        """Location information for sky matrix."""
        return self.wea.location

    def north_from_vector(self, north_vector):
        """Automatically set the north property using a Vector2D.

        Args:
            north_vector: A ladybug_geometry Vector2D for the north direction
        """
        self._north = math.degrees(north_vector.angle_clockwise(Vector2D(0, 1)))

    @classmethod
    def from_dict(cls, input_dict):
        """Create the sky from a dictionary.

        Args:
            input_dict: A python dictionary in the following format

        .. code-block:: python

            {
                'type': 'SunMatrix',
                'wea': {},
                'north': 0.0  # optional
            }
        """
        if 'type' not in input_dict or input_dict['type'] != 'SunMatrix':
            raise ValueError('Input dict "type" must be "SunMatrix".')
        if 'north' in input_dict:
            sky = cls(Wea.from_dict(input_dict['wea']), input_dict['north'])
        else:
            sky = cls(input_dict['wea'])

        return sky

    # TODO: add support for additional parameters
    # TODO: add gendaymtx to radiance-command and use it for validating inputs
    def to_radiance(self, output_type=1, wea_file=None, output_name=None):
        """Return Radiance command to generate the sky.

        Note that you need to write the wea to a file (in.wea) before running this
        command.

        Alternatively you can use write method which will write the wea data to a file.

        Args:
            output_type: An integer between 0 to 1 for output type.
                * 0 = output in W/m2/sr visible
                * 1 = output in W/m2/sr solar (default)
            wea_file: Path to wea file (default: in.wea).
            output_name: A name for output files (default: suns).
        """
        output_type = typing.int_in_range(output_type, 0, 1, 'SunMatrix output type')
        wea_file = wea_file or 'in.wea'
        output_name = output_name or 'suns'
        if self.north == 0:
            command = 'gendaymtx -n -D {0}.mtx -M {0}.mod -O{1} {2}'.format(
                output_name, output_type, wea_file
            )
        else:
            command = 'gendaymtx -n -D {0}.mtx -M {0}.mod -O{1} -r {3} {2}'.format(
                output_name, output_type, wea_file, self.north
            )

        return command

    def to_dict(self):
        """Translate this matrix to a dictionary."""

        return {
            'type': 'SunMatrix',
            'wea': self.wea.to_dict(),
            'north': self.north
        }

    def write_wea(self, folder='.', name=None, hoys=None):
        """Write wea to a file.

        Args:
            folder: Path to target folder (Default: '.').
            name: Optional name for the wea file (Default: in.wea)
            hoys: Optional list of hoys to filter the hours of the wea. If None,
                this object's wea will be used as-is. Note that you may not want
                to use this input if this object's wea is not annual since an
                exception will be raised if a given hoy is not found in the
                wea. (Default: None).

        Returns:
            Path to wea file.
        """
        name = name or 'in.wea'
        file_path = os.path.join(folder, name)
        wea_obj = self.wea if hoys is None else self.wea.filter_by_hoys(hoys)
        return wea_obj.write(file_path=file_path)

    def to_file(self, folder, name=None, hoys=None, mkdir=False):
        """Write matrix to a Radiance file.

        This method also writes the wea information to a .wea file.

        Args:
            folder: Target folder.
            name: File name.
            hoys: Optional list of hoys to filter the hours of the wea. If None,
                this object's wea will be used as-is. Note that you may not want
                to use this input if this object's wea is not annual since an
                exception will be raised if a given hoy is not found in the
                wea. (Default: None).
            mkdir: A boolean to note if the directory should be created if doesn't
                exist (default: False).

        Returns:
            Full path to the newly created file.
        """
        name = typing.valid_string(name) if name \
            else '%s.rad' % self.__class__.__name__.lower()
        # write wea file first
        wea_file = self.write_wea(folder, hoys=hoys)
        content = self.to_radiance(wea_file=os.path.split(wea_file)[-1])
        return futil.write_to_file_by_name(folder, name, '!' + content, mkdir)

    def __eq__(self, value):
        if not isinstance(value, self.__class__) \
            or value.wea != self.wea \
                or value.north != self.north:
            return False
        return True

    def __ne__(self, value):
        return not self.__eq__(value)

    def __repr__(self):
        """Matrix representation."""
        return '%s: %s' % (self.__class__.__name__, self.wea.location.city)
