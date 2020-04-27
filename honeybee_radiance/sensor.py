"""A light version of test points."""
from __future__ import division
import honeybee.typing as typing


class Sensor(object):
    """A radiance sensor.

    Args:
        pos: Position of sensor as (x, y, z) (Default: (0, 0, 0)).
        dir: Direction of sensor as (x, y, z) (Default: (0, 0, 1)).

    Properties:
        * pos
        * dir

    """
    __slots__ = ('_pos', '_dir')

    def __init__(self, pos=None, dir=None):
        """Create a sensor."""
        self._pos = typing.tuple_with_length(pos) if pos is not None \
            else (0, 0, 0)
        self._dir = typing.tuple_with_length(dir) if dir is not None \
            else (0, 0, 1)

    @classmethod
    def from_dict(cls, sensor_dict):
        """Create a sensor from dictionary.

        .. code-block:: python

            {
            'pos': [0, 0, 0],  # array of 3 numbers for the sensor position
            'dir': [0, 0, 1]  # array of 3 numbers for the sensor direction
            }
        """
        pos = sensor_dict['pos'] if 'pos' in sensor_dict else None
        direct = sensor_dict['dir'] if 'dir' in sensor_dict else None
        return cls(pos, direct)

    @classmethod
    def from_raw_values(cls, x=0, y=0, z=0, dx=0, dy=0, dz=1):
        """Create a sensor from 6 values.

        x, y, z are the position of the point and dx, dy and dz is the direction.
        """
        return cls((x, y, z), (dx, dy, dz))

    @property
    def pos(self):
        """Get the position of the sensor as a tuple of 3 (x, y, z) numbers."""
        return self._pos

    @property
    def dir(self):
        """Get the dir of the sensor as a tuple of 3 (x, y, z) numbers."""
        return self._dir

    def duplicate(self):
        """Duplicate the sensor."""
        return Sensor(self.pos, self.dir)

    def ToString(self):
        """Overwrite .NET ToString."""
        return self.__repr__()

    def to_radiance(self):
        """Return Radiance string for a test point."""
        return '%s %s' % (
            ' '.join(str(v) for v in self.pos),
            ' '.join(str(v) for v in self.dir)
        )

    def to_dict(self):
        """Get the sensor as a dictionary.

        .. code-block:: python

            {
            'pos': [0, 0, 0],  # array of 3 numbers for the sensor position
            'dir': [0, 0, 1]  # array of 3 numbers for the sensor direction
            }
        """
        return {'pos': self.pos, 'dir': self.dir}

    def __eq__(self, value):
        if not isinstance(value, Sensor):
            return False
        return self.pos == value.pos and self.dir == value.dir

    def __ne__(self, value):
        return not self.__eq__(value)

    def ToString(self):
        return self.__repr__()

    def __repr__(self):
        """Get the string representation of the sensor grid."""
        return self.to_radiance()
