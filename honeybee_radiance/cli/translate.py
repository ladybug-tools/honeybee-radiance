"""honeybee radiance translation commands."""
import click
import sys
import os
import logging
import json

from honeybee_radiance.reader import string_to_dicts
from honeybee_radiance.mutil import dict_to_modifier, modifier_class_from_type_string

from honeybee.model import Model
from ladybug.futil import preparedir

_logger = logging.getLogger(__name__)


@click.group(help='Commands for translating Honeybee JSON files to/from RAD.')
def translate():
    pass


@translate.command('model-to-rad-folder')
@click.argument('model-json', type=click.Path(
    exists=True, file_okay=True, dir_okay=False, resolve_path=True))
@click.option('--folder', help='Folder into which the model Radiance '
              'folders will be written. If None, the files will be output in the '
              'same location as the model_json.', default=None, show_default=True)
@click.option(
    '--grid', '-g', multiple=True, help='List of grids to be included in folder. By '
    'default all the sensor grids will be exported. You can also use wildcards here. '
    'For instance first_floor_* will select all the sensor grids that has an identifier '
    'that starts with first_floor. To filter based on group_identifier use /. For '
    'example daylight/* will select all the grids that belong to daylight group.')
@click.option(
    '--view', '-v', multiple=True, help='List of views to be included in folder. By '
    'default all the views will be exported. You can also use wildcards to fileter '
    'multiple views. For instance first_floor_* will select all the views that has an '
    'identifier that starts with first_floor. To filter based on group_identifier use '
    '/. For example daylight/* will select all the views that belong to daylight group.')
@click.option('--config-file', help='An optional config file path to modify the '
              'default folder names. If None, folder.cfg in honeybee-radiance-folder '
              'will be used.', default=None, show_default=True)
@click.option('--minimal/--maximal', help='Flag to note whether the radiance strings '
              'should be written in a minimal format (with spaces instead of line '
              'breaks).', default=False, show_default=True)
@click.option('--no-grid-check/--grid-check', ' /-gc', help='Flag to note whether the '
              'model should be checked for the presence of sensor grids. If the check '
              'is set and the model has no grids, an explicit error will be raised.',
              default=True, show_default=True)
@click.option('--no-view-check/--view-check', ' /-vc', help='Flag to note whether the '
              'model should be checked for the presence of views. If the check '
              'is set and the model has no views, an explicit error will be raised.',
              default=True, show_default=True)
@click.option('--log-file', help='Optional log file to output the path of the radiance '
              'folder generated from the model. By default this will be printed '
              'to stdout', type=click.File('w'), default='-')
def model_to_rad_folder(model_json, folder, view, grid, config_file, minimal,
                        no_grid_check, no_view_check, log_file):
    """Translate a Model JSON file into a Radiance Folder.

    \b
    Args:
        model_json: Full path to a Model JSON file (HBJSON) or a Model pkl (HBpkl) file.
    """
    try:
        # set the default folder if it's not specified
        if folder is None:
            folder = os.path.dirname(os.path.abspath(model_json))

        # re-serialize the Model and perform any checks
        model = Model.from_file(model_json)
        if not no_grid_check and len(model.properties.radiance.sensor_grids) == 0:
            raise ValueError('Model contains no sensor grids. These are required.')
        if not no_view_check and len(model.properties.radiance.sensor_grids) == 0:
            raise ValueError('Model contains no views These are required.')

        # translate the model to a radiance folder
        rad_fold = model.to.rad_folder(
            model, folder, config_file, minimal, views=view, grids=grid
        )
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

    The resulting strings will include all geometry (Rooms, Faces, Shades, Apertures,
    Doors) and all modifiers. However, it does not include any states for dynamic
    geometry and will only write the default state for each dynamic object. To
    correctly account for dynamic objects, model-to-rad-folder should be used.

    \b
    Args:
        model_json: Full path to a Model JSON file (HBJSON) or a Model pkl (HBpkl) file.
    """
    try:
        # re-serialize the Model and translate the model to a rad string
        model = Model.from_file(model_json)
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


@translate.command('model-radiant-enclosure-info')
@click.argument('model-json', type=click.Path(
    exists=True, file_okay=True, dir_okay=False, resolve_path=True))
@click.option('--folder', help='Folder into which the radiant enclosure info JSONs '
              'will be written. If None, the files will be output in the'
              'same location as the model_json in an enclosure subfolder.',
              default=None, show_default=True)
@click.option('--log-file', help='Optional log file to output the list of generated '
              'radiant enclosure JSONs. By default this will be printed '
              'to stdout', type=click.File('w'), default='-')
def model_radiant_enclosure_info(model_json, folder, log_file):
    """Translate a Model JSON file to a list of JSONs with radiant enclosure information.

    There will be one radiant enclosure JSON for each Model SensorGrid written to
    the output folder and each JSON will contain a list of values about which room
    (or radiant enclosure) each sensor is located. JSONs will also include a mapper
    that links the integers of each sensor with the identifier(s) of a room.

    \b
    Args:
        model_json: Full path to a Model JSON file (HBJSON) or a Model pkl (HBpkl) file.
    """
    try:
        # re-serialize the Model
        model = Model.from_file(model_json)

        # set the default folder if it's not specified
        if folder is None:
            folder = os.path.dirname(os.path.abspath(model_json))
            folder = os.path.join(folder, 'enclosure')
        if not os.path.isdir(folder):
            preparedir(folder)  # create the directory if it's not there

        # loop through sensor grids and build up the radiant enclosure dicts
        grids_info = []
        for grid in model.properties.radiance.sensor_grids:
            # write an enclosure JSON for each grid
            enc_dict = grid.enclosure_info_dict(model)
            enclosure_file = os.path.join(folder, '{}.json'.format(grid.identifier))
            with open(enclosure_file, 'w') as fp:
                json.dump(enc_dict, fp)
            g_info = {
                'id': grid.identifier,
                'enclosure_path': enclosure_file,
                'enclosure_full_path': os.path.abspath(enclosure_file),
                'count': grid.count
            }
            grids_info.append(g_info)

        # write out the list of radiant enclosure JSON info
        log_file.write(json.dumps(grids_info, indent=4))
    except Exception as e:
        _logger.exception('Model translation to radiant enclosure failed.\n{}'.format(e))
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
