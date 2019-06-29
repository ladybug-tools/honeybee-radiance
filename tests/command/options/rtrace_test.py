"""Test rtrace options."""
from honeybee_radiance.command.options.rtrace import RtraceOptions
import pytest


def test_default():
    options = RtraceOptions()
    assert options.to_radiance() == ''


def test_assignment():
    options = RtraceOptions()
    options.ab = 5
    assert options.ab == 5
    assert options.to_radiance() == '-ab 5'
    # handle wrong value type like a boss
    options.ab = 3.2
    assert options.ab == 3
    assert options.to_radiance() == '-ab 3'


def test_reassignment():
    options = RtraceOptions()
    options.ab = 5
    assert options.ab == 5
    assert options.to_radiance() == '-ab 5'
    # remove assigned values
    options.ab = None
    assert options.ab == None
    assert options.to_radiance() == ''


def test_multiple_assignment():
    options = RtraceOptions()
    options.ab = 2
    options.ad = 546
    assert '-ab 2' in options.to_radiance()
    assert 'ad 546' in options.to_radiance()


def test_boolean_assignment():
    options = RtraceOptions()
    options.w = False
    options.h = True
    assert '-w-' in options.to_radiance()
    assert '-h' in options.to_radiance()


def test_invalid_assignment():
    opts = RtraceOptions()
    with pytest.raises(AttributeError):
        opts.mm = 20
    
    with pytest.raises(TypeError):
        opts.ab = 'ambient bounces'  # must be a numeric value


def test_exclusives_i():
    opt = RtraceOptions()
    opt.i = True
    with pytest.raises(AssertionError):
        # i and I cannot be used together
        opt.I = True


def test_exclusives_ae():
    opt = RtraceOptions()
    opt.ae = 'modifier_1'
    with pytest.raises(AssertionError):
        # i and I cannot be used together
        opt.ai = 'modifier_2'


def test_from_string_non_standard():
    opt = RtraceOptions()
    opt_str = '-g 200'
    opt.update_from_string(opt_str)
    assert '-g 200' in opt.to_radiance()

def test_from_string():
    opt = RtraceOptions()
    opt_str = '-I -u- -h+ -lw 2e-06 -fa'
    opt.update_from_string(opt_str)
    assert opt.I == True
    assert opt.u == False
    assert opt.h == True
    assert opt.lw == 2e-06
    assert opt.fio == 'a'
