"""Test oconv options."""
from honeybee_radiance.command.options.oconv import OconvOptions
import pytest


def test_default():
    options = OconvOptions()
    assert options.to_radiance() == ''


def test_assignment():
    options = OconvOptions()
    options.i = 'existing.oct'
    assert options.i == 'existing.oct'
    assert options.to_radiance() == '-i existing.oct'


def test_reassignment():
    options = OconvOptions()
    options.i = 'existing.oct'
    assert options.i == 'existing.oct'
    assert options.to_radiance() == '-i existing.oct'
    # remove assigned values
    options.i = None
    assert options.i == None
    assert options.to_radiance() == ''


def test_multiple_assignment():
    options = OconvOptions()
    options.f = True
    options.b = (0, 10, 10, 2000)
    assert '-b 0.0 10.0 10.0 2000.0' in options.to_radiance()
    assert '-f' in options.to_radiance()


def test_boolean_assignment():
    options = OconvOptions()
    options.w = False
    assert '-w-' in options.to_radiance()


def test_invalid_assignment():
    opts = OconvOptions()
    with pytest.raises(AttributeError):
        opts.ab = 20
    
    with pytest.raises(TypeError):
        opts.r = 'max resolution'  # must be a numeric value


def test_exclusives_i():
    opt = OconvOptions()
    opt.i = 'existing.oct'
    with pytest.raises(AssertionError):
        # b and i cannot be used together
        opt.b = (0, 0, 0, 10)

def test_from_string_non_standard():
    opt = OconvOptions()
    opt_str = '-g 200'
    opt.update_from_string(opt_str)
    assert '-g 200' in opt.to_radiance()

def test_from_string():
    opt = OconvOptions()
    opt_str = '-b 0 0 0 10 -f -n 8 -r 200000 -w'
    opt.update_from_string(opt_str)
    assert opt.b == (0, 0, 0, 10)
    assert opt.f == True
    assert opt.n == 8
    assert opt.r == 200000
    assert opt.w == True
