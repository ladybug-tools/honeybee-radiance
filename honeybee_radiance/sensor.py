"""A light version of test points."""
from __future__ import division
import honeybee.typing as typing


class Sensor(object):
    """A radiance sensor.

    Args:
        position: Position of sensor as (x, y, z) (Default: (0, 0, 0)).
        direction: Direction of sensor as (x, y, z) (Default: (0, 0, 1)).

    Properties:
        * position
        * direction

    """
    __slots__ = ('_pos', '_dir')

    def __init__(self, position=None, direction=None):
        """Create a sensor."""
        self._pos = typing.tuple_with_length(position) if position is not None \
            else (0, 0, 0)
        self._dir = typing.tuple_with_length(direction) if direction is not None \
            else (0, 0, 1)

    @classmethod
    def from_dict(cls, sensor_dict):
        """Create a sensor from dictionary.

        .. code-block:: python

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

        x, y, z are the position of the point and dx, dy and dz is the direction.
        """
        return cls((x, y, z), (dx, dy, dz))

    @property
    def position(self):
        """Position of sensors as (x, y, z)."""
        return self._pos

    @property
    def direction(self):
        """Direction of sensors as (x, y, z)."""
        return self._dir

    def duplicate(self):
        """Duplicate the sensor."""
        return Sensor(self.position, self.direction)

    def ToString(self):
        """Overwrite .NET ToString."""
        return self.__repr__()

    def to_radiance(self):
        """Return Radiance string for a test point."""
        return '%s %s' % (
            ' '.join(str(v) for v in self.position),
            ' '.join(str(v) for v in self.direction)
        )

    def to_dict(self):
        """Get the sensor as a dictionary.

        .. code-block:: python

            {
            'x': float, 'y': float, 'z': float,
            'dx': float, 'dx': float, 'dz': float
            }
        """
        return {
            'x': self.position[0], 'y': self.position[1], 'z': self.position[2],
            'dx': self.direction[0], 'dy': self.direction[1], 'dz': self.direction[2]
        }

    def __eq__(self, value):
        if not isinstance(value, Sensor):
            return False
        return self.position == value.position and self.direction == value.direction

    def __ne__(self, value):
        return not self.__eq__(value)

    def __repr__(self):
        """Print a sensor."""
        return self.to_radiance()
