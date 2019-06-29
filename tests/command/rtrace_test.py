from honeybee_radiance.command.rtrace import Rtrace
import pytest
import honeybee_radiance.exception as exceptions


def test_defaults():
    rtrace = Rtrace()
    assert rtrace.command == 'rtrace'
    assert rtrace.options.to_radiance() == ''
    with pytest.raises(exceptions.MissingArgumentError):
        # missing octree
        rtrace.to_radiance()


def test_assignment():
    rtrace = Rtrace()  
    rtrace.octree = 'input.oct'
    assert rtrace.octree == 'input.oct'
    rtrace.sensors = 'sensors.pts'
    assert rtrace.sensors == 'sensors.pts'
    assert rtrace.to_radiance() == 'rtrace input.oct < sensors.pts'
    rtrace.output = 'results.dat'
    assert rtrace.output == 'results.dat'
    assert rtrace.to_radiance() == 'rtrace input.oct < sensors.pts > results.dat'


def test_stdin():
    rtrace = Rtrace()  
    rtrace.octree = 'input.oct'
    rtrace.sensors = 'sensors.pts'
    rtrace.output = 'results.dat'
    assert rtrace.to_radiance(stdin_input=True) == 'rtrace input.oct > results.dat'


def test_validation():
    rtrace = Rtrace()
    with pytest.raises(exceptions.MissingArgumentError):
        # missing octree
        rtrace.to_radiance()

    rtrace.octree = 'input.oct'
    with pytest.raises(exceptions.MissingArgumentError):
        # missing sensors
        rtrace.to_radiance()

    rtrace.sensors = 'sensors.pts'
    assert rtrace.to_radiance() == 'rtrace input.oct < sensors.pts'
