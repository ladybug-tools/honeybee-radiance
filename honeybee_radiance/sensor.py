"""A light version of test points."""
from __future__ import division
import honeybee.typing as typing

import ladybug_geometry.geometry3d.pointvector as pv

import math


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
        self.pos = pos
        self.dir = dir

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
        """Get or set the position of the sensor as a tuple of 3 (x, y, z) numbers."""
        return self._pos

    @pos.setter
    def pos(self, value):
        self._pos = typing.tuple_with_length(value) if value is not None else (0, 0, 0)

    @property
    def dir(self):
        """Get or set the dir of the sensor as a tuple of 3 (x, y, z) numbers."""
        return self._dir

    @dir.setter
    def dir(self, value):
        self._dir = typing.tuple_with_length(value) if value is not None else (0, 0, 1)

    def move(self, moving_vec):
        """Move this sensor along a vector.

        Args:
            moving_vec: A ladybug_geometry Vector3D with the direction and distance
                to move the sensor.
        """
        self.pos = tuple(pv.Point3D(*self.pos).move(moving_vec))

    def rotate(self, axis, angle, origin):
        """Rotate this sensor by a certain angle around an axis and origin.

        Args:
            axis: Rotation axis as a Vector3D.
            angle: An angle for rotation in degrees.
            origin: A ladybug_geometry Point3D for the origin around which the
                object will be rotated.
        """
        rad_angle = math.radians(angle)
        self.pos = tuple(pv.Point3D(*self.pos).rotate(axis, rad_angle, origin))
        self.dir = tuple(pv.Vector3D(*self.dir).rotate(axis, rad_angle))

    def rotate_xy(self, angle, origin):
        """Rotate this sensor counterclockwise in the world XY plane by a certain angle.

        Args:
            angle: An angle in degrees.
            origin: A ladybug_geometry Point3D for the origin around which the
                object will be rotated.
        """
        rad_angle = math.radians(angle)
        self.pos = tuple(pv.Point3D(*self.pos).rotate_xy(rad_angle, origin))
        self.dir = tuple(pv.Vector3D(*self.dir).rotate_xy(rad_angle))

    def reflect(self, plane):
        """Reflect this sensor across a plane.

        Args:
            plane: A ladybug_geometry Plane across which the object will
                be reflected.
        """
        self.pos = tuple(pv.Point3D(*self.pos).reflect(plane.n, plane.o))
        self.dir = tuple(pv.Vector3D(*self.dir).reflect(plane.n))

    def scale(self, factor, origin=None):
        """Scale this sensor by a factor from an origin point.

        Args:
            factor: A number representing how much the object should be scaled.
            origin: A ladybug_geometry Point3D representing the origin from which
                to scale. If None, it will be scaled from the World origin (0, 0, 0).
        """
        self.pos = tuple(pv.Point3D(*self.pos).scale(factor, origin))

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

    def __key(self):
        """A tuple based on the object properties, useful for hashing."""
        return (hash(self.pos), hash(self.dir))

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        return isinstance(other, Sensor) and self.__key() == other.__key()

    def __ne__(self, value):
        return not self.__eq__(value)

    def __repr__(self):
        """Get the string representation of the sensor grid."""
        return self.to_radiance()
