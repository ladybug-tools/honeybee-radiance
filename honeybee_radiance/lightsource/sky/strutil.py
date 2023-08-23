# coding=utf-8
"""Utilities to convert sky strings to Python objects."""
from honeybee_radiance.lightsource.sky.certainirradiance import CertainIrradiance
from honeybee_radiance.lightsource.sky.cie import CIE
from honeybee_radiance.lightsource.sky.climatebased import ClimateBased

SKY_TYPES = {
    'irradiance': CertainIrradiance,
    'illuminance': CertainIrradiance,
    'cie': CIE,
    'climate-based': ClimateBased
}


def string_to_sky(sky_string, raise_exception=True):
    """Get a Python object of any sky from a string representation.

    Args:
        sky_string: A text string representing a CIE, ClimateBased, or CertainIrradiance
            sky. This can be a minimal representation of the sky (eg.
            "cie -alt 71.6 -az 185.2 -type 0"). Or it can be a detailed specification of
            time and location (eg. "cie 21 Jun 12:00 -lat 41.78 -lon -87.75 -type 0").
        raise_exception: Boolean to note whether an exception should be raised
            if the object is not identified as a sky. Default: True.

    Returns:
        A Python object derived from the input sky_string.
    """
    sky_type = sky_string.lower().split(' ')[0].strip()
    try:
        return SKY_TYPES[sky_type].from_string(sky_string)
    except KeyError:
        if raise_exception:
            raise ValueError('{} is not a recognized radiance Sky type'.format(sky_type))
