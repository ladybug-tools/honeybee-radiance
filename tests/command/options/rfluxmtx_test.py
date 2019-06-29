"""Test rfluxmtx options."""
from honeybee_radiance.command.options.rfluxmtx import RfluxmtxOptions
import pytest
import honeybee_radiance.exception as exception


def test_default():
    options = RfluxmtxOptions()
    assert options.to_radiance() == ''


def test_assignment():
    options = RfluxmtxOptions()
    options.v = True
    assert options.v == True
    assert options.to_radiance() == '-v'


def test_reassignment():
    options = RfluxmtxOptions()
    options.v = True
    assert options.v == True
    assert options.to_radiance() == '-v'
    # remove assigned values
    options.v = None
    assert options.v == None
    assert options.to_radiance() == ''


def test_protected_assignment():
    options = RfluxmtxOptions()
    with pytest.raises(exception.ProtectedOptionError):
        options.f = 'bins.cal'
    with pytest.raises(exception.ProtectedOptionError):
        options.e = '2*$1=$2'
    with pytest.raises(exception.ProtectedOptionError):
        options.m = 'modifier'
    with pytest.raises(exception.ProtectedOptionError):
        options.m = None
        options.M = './suns.mod'
