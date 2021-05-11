# coding=utf-8
"""Utilities to convert light source dictionaries to Python objects."""
from honeybee_radiance.lightsource.sunpath import Sunpath
from honeybee_radiance.lightsource.ground import Ground
from honeybee_radiance.lightsource.sky.certainirradiance import CertainIrradiance
from honeybee_radiance.lightsource.sky.cie import CIE
from honeybee_radiance.lightsource.sky.climatebased import ClimateBased
from honeybee_radiance.lightsource.sky.hemisphere import Hemisphere
from honeybee_radiance.lightsource.sky.skydome import SkyDome
from honeybee_radiance.lightsource.sky.skymatrix import SkyMatrix
from honeybee_radiance.lightsource.sky.sunmatrix import SunMatrix


LIGHT_SOURCE_TYPES = {
    'Sunpath': Sunpath,
    'Ground': Ground,
    'CertainIrradiance': CertainIrradiance,
    'CIE': CIE,
    'ClimateBased': ClimateBased,
    'Hemisphere': Hemisphere,
    'SkyDome': SkyDome,
    'SkyMatrix': SkyMatrix,
    'SunMatrix': SunMatrix
}


def dict_to_light_source(light_source_dict, raise_exception=True):
    """Get a Python object of any light source from a dictionary.

    Args:
        light_source_dict: A dictionary of any Honeybee Radiance light source. Note
            that this should be a non-abridged dictionary to be valid.
        raise_exception: Boolean to note whether an excpetion should be raised
            if the object is not identified as a light source. Default: True.

    Returns:
        A Python object derived from the input light_source_dict.
    """
    try:  # get the type key from the dictionary
        light_type = light_source_dict['type']
    except KeyError:
        raise ValueError('Light source dictionary lacks required "type" key.')

    try:
        return LIGHT_SOURCE_TYPES[light_type].from_dict(light_source_dict)
    except KeyError:
        if raise_exception:
            raise ValueError(
                '{} is not a recognized radiance Light Source type'.format(light_type))
