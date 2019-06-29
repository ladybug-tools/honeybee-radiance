"""Test rcalc options."""
from honeybee_radiance.command.options.rcalc import RcalcOptions
import pytest
import honeybee_radiance.exception as exception
import warnings


def test_default():
    options = RcalcOptions()
    assert options.to_radiance() == ''


def test_assignment():
    options = RcalcOptions()
    options.o = 'd'
    assert options.o == 'd'
    assert options.to_radiance() == '-od'


def test_reassignment():
    options = RcalcOptions()
    options.o = 'd'
    assert options.o == 'd'
    assert options.to_radiance() == '-od'
    # remove assigned values
    options.o = None
    assert options.o == None
    assert options.to_radiance() == ''


def test_expression_assignment():
    options = RcalcOptions()
    options.e = '$1=(0.265*$1+0.67*$2+0.065*$3)*179/1000'
    assert len(options.e) == len('$1=(0.265*$1+0.67*$2+0.065*$3)*179/1000') + 2


def test_warning():
    options = RcalcOptions()
    with warnings.catch_warnings(record=True) as catcher:
        warnings.simplefilter('always')
        options.p =True
        # verify a warning has been raised for empty scene.
        assert len(catcher) == 1
        message = str(catcher[0].message)
        assert '-p has no effect unless -i is also specified.' in message
        assert 'rcalc:' in message
