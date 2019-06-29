from honeybee_radiance.command.rcontrib import Rcontrib
import pytest
import honeybee_radiance.exception as exceptions


def test_defaults():
    rcontrib = Rcontrib()
    assert rcontrib.command == 'rcontrib'
    assert rcontrib.options.to_radiance() == ''
    with pytest.raises(exceptions.MissingArgumentError):
        # missing octree
        rcontrib.to_radiance()


def test_assignment():
    rcontrib = Rcontrib()  
    rcontrib.octree = 'input.oct'
    assert rcontrib.octree == 'input.oct'
    rcontrib.sensors = 'sensors.pts'
    assert rcontrib.sensors == 'sensors.pts'
    assert rcontrib.to_radiance() == 'rcontrib input.oct < sensors.pts'
    rcontrib.output = 'results.dat'
    assert rcontrib.output == 'results.dat'
    assert rcontrib.to_radiance() == 'rcontrib input.oct < sensors.pts > results.dat'
    rcontrib.options.c = 1000
    assert rcontrib.to_radiance() == \
        'rcontrib -c 1000 input.oct < sensors.pts > results.dat'


def test_stdin():
    rcontrib = Rcontrib()  
    rcontrib.octree = 'input.oct'
    rcontrib.sensors = 'sensors.pts'
    rcontrib.output = 'results.dat'
    assert rcontrib.to_radiance(stdin_input=True) == 'rcontrib input.oct > results.dat'


def test_validation():
    rcontrib = Rcontrib()
    with pytest.raises(exceptions.MissingArgumentError):
        # missing octree
        rcontrib.to_radiance()

    rcontrib.octree = 'input.oct'
    with pytest.raises(exceptions.MissingArgumentError):
        # missing sensors
        rcontrib.to_radiance()

    rcontrib.sensors = 'sensors.pts'
    assert rcontrib.to_radiance() == 'rcontrib input.oct < sensors.pts'
