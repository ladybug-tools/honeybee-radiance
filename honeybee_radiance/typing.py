"""Collection of methods for type checking."""
import re


def valid_string(value):
    """Get a valid string from input value."""
    return re.sub(r'[^.A-Za-z0-9_-]', '', value)


def float_in_range(value, mi=0.0, ma=1.0):
    """Check a float value to be between minimum and maximum."""
    number = float(value)
    assert mi <= number <= ma, 'Input number must be between %f and %f.' % (
        mi, ma)
    return number


def int_in_range(value, mi=0.0, ma=1.0):
    """Check an integer value to be between minimum and maximum."""
    number = int(value)
    assert mi <= number <= ma, 'Input number must be between %f and %f.' % (
        mi, ma)
    return number


def float_positive(input):
    """Check a float value to be positive."""
    number = float(input)
    assert 0 <= number, 'Input (%f) must be positive.' % number
    return number


def int_positive(value):
    """Check an integer value to be positive."""
    number = int(value)
    assert 0 <= number, 'Input (%d) must be positive.' % number
    return number
