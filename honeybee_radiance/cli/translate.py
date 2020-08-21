"""honeybee radiance translation commands."""

try:
    import click
except ImportError:
    raise ImportError(
        'click is not installed. Try `pip install honeybee-radiance[cli]` command.'
    )

from honeybee_radiance.reader import string_to_dicts
from honeybee_radiance.mutil import dict_to_modifier, modifier_class_from_type_string

from honeybee.model import Model

import sys
import os
import logging
import json

_logger = logging.getLogger(__name__)


@click.group(help='Commands for translating Honeybee JSON files to/from RAD.')
def translate():
    pass


@translate.command('model-to-rad-folder')
@click.argument('model-json', type=click.Path(
    exists=True, file_okay=True, dir_okay=False, resolve_path=True))
@click.option('--folder', help='Folder on this computer, into which the Radiance '
              'folders will be written. If None, the files will be output in the'
              'same location as the model_json.', default=None, show_default=True)
@click.option('--config-file', help='An optional config file path to modify the '
              'default folder names. If None, folder.cfg in honeybee-radiance-folder '
              'will be used.', default=None, show_default=True)
@click.option('--minimal/--maximal', help='Flag to note whether the radiance strings '
              'should be written in a minimal format (with spaces instead of line '
              'breaks).', default=False, show_default=True)
@click.option('--log-file', help='Optional log file to output the path of the radiance '
              'folder generated from the model. By default this will be printed '
              'to stdout', type=click.File('w'), default='-')
def model_to_rad_folder(model_json, folder, config_file, minimal, log_file):
    """Translate a Model JSON file into a Radiance Folder.
    \n
    Args:
        model_json: Full path to a Model JSON file.
    """
    try:
        # check that the model JSON is there
        assert os.path.isfile(model_json), \
            'No Model JSON file found at {}.'.format(model_json)

        # set the default folder if it's not specified
        if folder is None:
            folder = os.path.dirname(os.path.abspath(model_json))

        # re-serialize the Model to Python
        with open(model_json) as json_file:
            data = json.load(json_file)
        model = Model.from_dict(data)

        # translate the model to a radiance folder
        rad_fold = model.to.rad_folder(model, folder, config_file, minimal)
        log_file.write(rad_fold)
    except Exception as e:
        _logger.exception('Model translation failed.\n{}'.format(e))
        sys.exit(1)
    else:
        sys.exit(0)


@translate.command('model-to-rad')
@click.argument('model-json', type=click.Path(
    exists=True, file_okay=True, dir_okay=False, resolve_path=True))
@click.option('--blk', help='Boolean to note whether the "blacked out" version '
              'of the geometry should be output, which is useful for direct studies '
              'and isolation studies of individual apertures.',
              default=False, show_default=True)
@click.option('--minimal/--maximal', help='Flag to note whether the radiance strings '
              'should be written in a minimal format (with spaces instead of line '
              'breaks).', default=False, show_default=True)
@click.option('--output-file', help='Optional RAD file to output the RAD string of the '
              'translation. By default this will be printed out to stdout',
              type=click.File('w'), default='-', show_default=True)
def model_to_rad(model_json, blk, minimal, output_file):
    """Translate a Model JSON file to a Radiance string.
    \n
    The resulting strings will include all geometry (Rooms, Faces, Shades, Apertures,
    Doors) and all modifiers. However, it does not include any states for dynamic
    geometry and will only write the default state for each dynamic object. To
    correctly account for dynamic objects, model-to-rad-folder should be used.
    \n
    Args:
        model_json: Full path to a Model JSON file.
    """
    try:
        # check that the model JSON is there
        assert os.path.isfile(model_json), \
            'No Model JSON file found at {}.'.format(model_json)

        # re-serialize the Model to Python
        with open(model_json) as json_file:
            data = json.load(json_file)
        model = Model.from_dict(data)

        # translate the model to a rad string
        model_str, modifier_str = model.to.rad(model, blk, minimal)
        rad_str_list = ['# ========  MODEL MODIFIERS ========', modifier_str,
                        '# ========  MODEL GEOMETRY ========', model_str]
        rad_str = '\n\n'.join(rad_str_list)

        # write out the rad string
        output_file.write(rad_str)
    except Exception as e:
        _logger.exception('Model translation failed.\n{}'.format(e))
        sys.exit(1)
    else:
        sys.exit(0)


@translate.command('modifiers-to-rad')
@click.argument('modifier-json', type=click.Path(
    exists=True, file_okay=True, dir_okay=False, resolve_path=True))
@click.option('--minimal/--maximal', help='Flag to note whether the radiance strings '
              'should be written in a minimal format (with spaces instead of line '
              'breaks).', default=False, show_default=True)
@click.option('--output-file', help='Optional RAD file to output the RAD string of the '
              'translation. By default this will be printed out to stdout',
              type=click.File('w'), default='-', show_default=True)
def modifier_to_rad(modifier_json, minimal, output_file):
    """Translate a Modifier JSON file to an RAD using direct-to-rad translators.
    \n
    Args:
        modifier_json: Full path to a Modifier JSON file. This file should
            either be an array of non-abridged Modifiers or a dictionary where
            the values are non-abridged Modifiers.
    """
    try:
        # check that the modifier JSON is there
        assert os.path.isfile(modifier_json), \
            'No Modifier JSON file found at {}.'.format(modifier_json)

        # re-serialize the Modifiers to Python
        with open(modifier_json) as json_file:
            data = json.load(json_file)
        mod_list = data.values() if isinstance(data, dict) else data
        mod_objs = []
        for mod_dict in mod_list:
            m_class = modifier_class_from_type_string(mod_dict['type'].lower())
            mod_objs.append(m_class.from_dict(mod_dict))

        # create the RAD strings
        rad_str_list = []
        rad_str_list.extend([mod.to_radiance(minimal) for mod in mod_objs])
        rad_str = '\n\n'.join(rad_str_list)

        # write out the RAD file
        output_file.write(rad_str)
    except Exception as e:
        _logger.exception('Modifier translation failed.\n{}'.format(e))
        sys.exit(1)
    else:
        sys.exit(0)


@translate.command('modifiers-from-rad')
@click.argument('modifier-rad', type=click.Path(
    exists=True, file_okay=True, dir_okay=False, resolve_path=True))
@click.option('--output-file', help='Optional JSON file to output the JSON string of the'
              'translation. By default this will be printed out to stdout',
              type=click.File('w'), default='-', show_default=True)
def modifier_from_rad(modifier_rad, output_file):
    """Translate a Modifier JSON file to a honeybee JSON as an array of modifiers.
    \n
    Args:
        modifier_rad: Full path to a Modifier .rad or .mat file. Only the modifiers
            and materials in this file will be extracted.
    """
    try:
        # check that the modifier file is there
        assert os.path.isfile(modifier_rad), \
            'No Modifier file found at {}.'.format(modifier_rad)

        # re-serialize the Modifiers to Python
        mod_objs = []
        with open(modifier_rad) as f:
            rad_dicts = string_to_dicts(f.read())
            for mod_dict in rad_dicts:
                mod_objs.append(dict_to_modifier(mod_dict))

        # create the honeybee dictionaries
        json_dicts = [mod.to_dict() for mod in mod_objs]

        # write out the JSON file
        output_file.write(json.dumps(json_dicts))
    except Exception as e:
        _logger.exception('Modifier translation failed.\n{}'.format(e))
        sys.exit(1)
    else:
        sys.exit(0)
