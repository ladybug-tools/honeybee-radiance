"""Test sensor class."""
from honeybee_radiance.sensor import Sensor
import ladybug_geometry.geometry3d.pointvector as pv
from ladybug_geometry.geometry3d.plane import Plane
import pytest


def test_default_values():
    sensor = Sensor()
    str(sensor)  # test the string representation
    hash(sensor)  # test the hash-ability
    assert sensor.pos == (0, 0, 0)
    assert sensor.dir == (0, 0, 1)


def test_assign_values():
    sensor = Sensor((0, 0, 10), (0, 0, -1))
    assert sensor.pos == (0, 0, 10)
    assert sensor.dir == (0, 0, -1)


def test_invalid_input():
    with pytest.raises(AssertionError):
        Sensor((0, 0))


def test_converting_string():
    sensor = Sensor(('0', '0', '10'), ('0', '0', '-1'))
    assert sensor.pos == (0, 0, 10)
    assert sensor.dir == (0, 0, -1)


def test_move():
    sensor = Sensor((0, 0, 10), (0, 0, -1))
    sensor.move(pv.Vector3D(10, 20, 30))

    assert sensor.pos == (10, 20, 40)
    assert sensor.dir == (0, 0, -1)


def test_rotate():
    sensor = Sensor((0, 0, 0), (1, 0, 0))
    sensor.rotate(90, pv.Vector3D(0, 1, 1), pv.Point3D(0, 0, 20))
    assert round(sensor.pos[0], 3) == -14.142
    assert round(sensor.pos[1]) == -10
    assert round(sensor.pos[2]) == 10
    assert round(sensor.dir[0], 1) == 0.0
    assert round(sensor.dir[1], 3) == 0.707
    assert round(sensor.dir[2], 3) == -0.707


def test_rotate_xy():
    sensor = Sensor((1, 0, 2), (2, 0, 0))
    sensor.rotate_xy(90, pv.Point3D(0, 0, 0))

    assert round(sensor.pos[0]) == 0
    assert round(sensor.pos[1]) == 1
    assert round(sensor.pos[2]) == 2
    assert round(sensor.dir[0]) == 0
    assert round(sensor.dir[1]) == 2
    assert round(sensor.dir[2]) == 0


def test_reflect():
    sensor = Sensor((1, 0, 2), (2, 0, 0))
    sensor.reflect(Plane(pv.Vector3D(1, 0, 0), pv.Point3D(0, 0, 0)))

    assert round(sensor.pos[0]) == -1
    assert round(sensor.pos[1]) == 0
    assert round(sensor.pos[2]) == 2
    assert round(sensor.dir[0]) == -2
    assert round(sensor.dir[1]) == 0
    assert round(sensor.dir[2]) == 0


def test_scale():
    sensor = Sensor((1, 0, 2), (1, 0, 0))
    sensor.scale(2)

    assert round(sensor.pos[0]) == 2
    assert round(sensor.pos[1]) == 0
    assert round(sensor.pos[2]) == 4
    assert round(sensor.dir[0]) == 1
    assert round(sensor.dir[1]) == 0
    assert round(sensor.dir[2]) == 0


def test_to_and_from_dict():
    sensor = Sensor()
    sensor_dict = sensor.to_dict()
    assert sensor_dict == {'pos': (0, 0, 0), 'dir': (0, 0, 1)}

    sensor_from = Sensor.from_dict(sensor_dict)
    assert sensor_from == sensor


def test_from_values():
    sensor = Sensor.from_raw_values()
    assert sensor.pos == (0, 0, 0)
    assert sensor.dir == (0, 0, 1)

    sensor = Sensor.from_raw_values(-1, 1, 2, 3, 4, 5)
    assert sensor.pos == (-1, 1, 2)
    assert sensor.dir == (3, 4, 5)
