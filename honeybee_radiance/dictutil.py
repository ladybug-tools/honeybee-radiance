# coding=utf-8
"""Utilities to convertint any dictionary to Python objects.

Note that importing this module will import almost all modules within the
library in order to be able to re-serialize almost any dictionary produced
from the library.
"""
from honeybee_radiance.putil import dict_to_primitive
from honeybee_radiance.modifierset import ModifierSet
from honeybee_radiance.sensorgrid import SensorGrid
from honeybee_radiance.view import View
from honeybee_radiance.lightsource.dictutil import dict_to_light_source, \
    LIGHT_SOURCE_TYPES


def dict_to_object(honeybee_radiance_dict, raise_exception=True):
    """Re-serialize a dictionary of almost any object within honeybee_radiance.

    This includes any Modifier, ModifierSet, LightSource, SensorGrid or View object.

    Args:
        honeybee_radiance_dict: A dictionary of any Honeybee radiance object. Note
            that this should be a non-abridged dictionary to be valid.
        raise_exception: Boolean to note whether an excpetion should be raised
            if the object is not identified as a part of honeybee_radiance.
            Default: True.

    Returns:
        A Python object derived from the input honeybee_radiance_dict.
    """
    try:  # get the type key from the dictionary
        obj_type = honeybee_radiance_dict['type']
    except KeyError:
        raise ValueError('Honeybee_radiance dictionary lacks required "type" key.')

    if obj_type == 'ModifierSet':
        return ModifierSet.from_dict(honeybee_radiance_dict)
    elif obj_type == 'SensorGrid':
        return SensorGrid.from_dict(honeybee_radiance_dict)
    elif obj_type == 'View':
        return View.from_dict(honeybee_radiance_dict)
    elif obj_type in LIGHT_SOURCE_TYPES:
        return dict_to_light_source(honeybee_radiance_dict)
    else:
        try:
            return dict_to_primitive(honeybee_radiance_dict)
        except (NotImplementedError, ValueError):
            if raise_exception:
                raise ValueError(
                    '{} is not a recognized honeybee radiance object'.format(obj_type))
