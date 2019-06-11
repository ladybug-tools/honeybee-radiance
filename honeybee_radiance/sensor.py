"""A light version of test points."""
from __future__ import division
import honeybee_radiance.typing as typing


class Sensor(object):
    """A radiance sensor.

    Args:
        location: Location of sensor as (x, y, z) (Default: (0, 0, 0)).
        direction: Direction of sensor as (x, y, z) (Default: (0, 0, 1)).
    """

    __slots__ = ('_loc', '_dir')

    def __init__(self, location=None, direction=None):
        """Create a sensor."""
        self._loc = typing.tuple_with_length(location) if location is not None \
            else (0, 0, 0)
        self._dir = typing.tuple_with_length(direction) if direction is not None \
            else (0, 0, 1)

    @classmethod
    def from_dict(cls, sensor_dict):
        """Create a sensor from dictionary.
            {
                'x': float, 'y': float, 'z': float,
                'dx': float, 'dx': float, 'dz': float
            }
        """
        return cls(
            [sensor_dict['x'], sensor_dict['y'], sensor_dict['z']],
            [sensor_dict['dx'], sensor_dict['dy'], sensor_dict['dz']]
        )

    @classmethod
    def from_raw_values(cls, x=0, y=0, z=0, dx=0, dy=0, dz=1):
        """Create a sensor from 6 values.

        x, y, z are the location of the point and dx, dy and dz is the direction.
        """
        return cls((x, y, z), (dx, dy, dz))

    @property
    def location(self):
        """Location of sensors as (x, y, z)."""
        return self._loc

    @property
    def direction(self):
        """Direction of sensors as (x, y, z)."""
        return self._dir

    def duplicate(self):
        """Duplicate the sensor."""
        return Sensor(self.location, self.direction)

    def ToString(self):
        """Overwrite .NET ToString."""
        return self.__repr__()

    def to_radiance(self):
        """Return Radiance string for a test point."""
        return '%s %s' % (
            ' '.join(str(v) for v in self.location),
            ' '.join(str(v) for v in self.direction)
        )

    def to_dict(self):
        """Get the sensor as a dictionary.
            {
                'x': float, 'y': float, 'z': float,
                'dx': float, 'dx': float, 'dz': float
            }
        """
        return {
            'x': self.location[0], 'y': self.location[1], 'z': self.location[2],
            'dx': self.direction[0], 'dy': self.direction[1], 'dz': self.direction[2]
        }

    def __eq__(self, value):
        if not isinstance(value, Sensor):
            return False
        return self.location == value.location and self.direction == value.direction

    def __ne__(self, value):
        return not self.__eq__(value)

    def __repr__(self):
        """Print a sensor."""
        return self.to_radiance()
