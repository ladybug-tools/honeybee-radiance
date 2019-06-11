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


def int_in_range(value, mi=0, ma=1):
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


def tuple_with_length(value, length=3, item_type=float):
    """Try to create a tuple with a certain value."""
    value = tuple(item_type(v) for v in value)
    assert len(value) == length, 'Input length must be %d not %d' % (
        length, len(value))
    return value


def list_with_length(value, length=3, item_type=float):
    """Try to create a list with a certain value."""
    value = [item_type(v) for v in value]
    assert len(value) == length, 'Input length must be %d not %d' % (
        length, len(value))
    return value
