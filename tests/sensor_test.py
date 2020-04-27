"""Test sensor class."""
from honeybee_radiance.sensor import Sensor
import pytest


def test_default_values():
    sensor = Sensor()
    assert sensor.pos == (0, 0, 0)
    assert sensor.dir == (0, 0, 1)


def test_assign_values():
    sensor = Sensor((0, 0, 10), (0, 0, -1))
    assert sensor.pos == (0, 0, 10)
    assert sensor.dir == (0, 0, -1)


def test_updating_values():
    sensor = Sensor()
    # sensor is immutable - hence no assignment
    with pytest.raises(AttributeError):
        sensor.location = (0, 0, 10)
    with pytest.raises(AttributeError):
        sensor.dir = (0, 0, 20)


def test_invalid_input():
    with pytest.raises(AssertionError):
        Sensor((0, 0))


def test_converting_string():
    sensor = Sensor(('0', '0', '10'), ('0', '0', '-1'))
    assert sensor.pos == (0, 0, 10)
    assert sensor.dir == (0, 0, -1)


def test_to_and_from_dict():
    sensor = Sensor()
    sensor_dict = sensor.to_dict()
    assert sensor_dict == {'pos': (0, 0, 0), 'dir': (0,  0, 1)}

    sensor_from = Sensor.from_dict(sensor_dict)
    assert sensor_from == sensor


def test_from_values():
    sensor = Sensor.from_raw_values()
    assert sensor.pos == (0, 0, 0)
    assert sensor.dir == (0, 0, 1)

    sensor = Sensor.from_raw_values(-1, 1, 2, 3, 4, 5)
    assert sensor.pos == (-1, 1, 2)
    assert sensor.dir == (3, 4, 5)
