"""honeybee radiance standards library commands."""
import click
import sys
import os
import logging
import json
import zipfile
from datetime import datetime

from honeybee_radiance.config import folders
from honeybee_radiance.lib.modifiers import modifier_by_identifier, MODIFIERS
from honeybee_radiance.lib.modifiersets import modifier_set_by_identifier, \
    lib_dict_abridged_to_modifier_set, MODIFIER_SETS
from honeybee_radiance.mutil import dict_to_modifier

from honeybee_radiance.lib._loadmodifiers import load_modifiers_from_folder
from honeybee_radiance.lib._loadmodifiersets import load_modifiersets_from_folder

_logger = logging.getLogger(__name__)


@click.group(help='Commands for retrieving objects from the standards library.')
def lib():
    pass


@lib.command('modifiers')
@click.option('--output-file', help='Optional file to output the JSON string of '
              'the object. By default, it will be printed out to stdout',
              type=click.File('w'), default='-', show_default=True)
def modifiers(output_file):
    """Get a list of all modifiers in the standards library."""
    try:
        output_file.write(json.dumps(MODIFIERS))
    except Exception as e:
        _logger.exception('Failed to load modifiers.\n{}'.format(e))
        sys.exit(1)
    else:
        sys.exit(0)


@lib.command('modifier-sets')
@click.option('--output-file', help='Optional file to output the JSON string of '
              'the object. By default, it will be printed out to stdout',
              type=click.File('w'), default='-', show_default=True)
def modifier_sets(output_file):
    """Get a list of all modifier sets in the standards library."""
    try:
        output_file.write(json.dumps(MODIFIER_SETS))
    except Exception as e:
        _logger.exception('Failed to load modifier sets.\n{}'.format(e))
        sys.exit(1)
    else:
        sys.exit(0)


@lib.command('modifier-by-id')
@click.argument('modifier-id', type=str)
@click.option('--output-file', help='Optional file to output the JSON string of '
              'the object. By default, it will be printed out to stdout',
              type=click.File('w'), default='-', show_default=True)
def modifier_by_id(modifier_id, output_file):
    """Get a modifier definition from the standards lib with its identifier.
    \n
    Args:
        modifier_id: The identifier of a modifier in the library.
    """
    try:
        output_file.write(json.dumps(modifier_by_identifier(modifier_id).to_dict()))
    except Exception as e:
        _logger.exception(
            'Retrieval from modifier library failed.\n{}'.format(e))
        sys.exit(1)
    else:
        sys.exit(0)


@lib.command('modifier-set-by-id')
@click.argument('modifier-set-id', type=str)
@click.option('--none-defaults', help='Boolean to note whether default modifiers '
              'in the set should be included in detail (False) or should be None '
              '(True).', type=bool, default=True, show_default=True)
@click.option('--abridged', help='Optional boolean to note wether an abridged definition'
              ' should be returned.', type=bool, default=False, show_default=True)
@click.option('--output-file', help='Optional file to output the JSON string of '
              'the object. By default, it will be printed out to stdout',
              type=click.File('w'), default='-', show_default=True)
def modifier_set_by_id(modifier_set_id, none_defaults, abridged, output_file):
    """Get an modifier set definition from the standards lib with its identifier.
    \n
    Args:
        modifier_set_id: The identifier of a modifier set in the library.
    """
    try:
        m_set = modifier_set_by_identifier(modifier_set_id)
        output_file.write(json.dumps(m_set.to_dict(
            none_for_defaults=none_defaults, abridged=abridged)))
    except Exception as e:
        _logger.exception(
            'Retrieval from modifier set library failed.\n{}'.format(e))
        sys.exit(1)
    else:
        sys.exit(0)


@lib.command('modifiers-by-id')
@click.argument('modifier-ids', nargs=-1)
@click.option('--output-file', help='Optional file to output the JSON strings of '
              'the objects. By default, it will be printed out to stdout',
              type=click.File('w'), default='-', show_default=True)
def modifiers_by_id(modifier_ids, output_file):
    """Get several modifier definitions from the standards lib at once.
    \n
    Args:
        modifier_ids: A list of modifier identifiers to be retrieved from the library.
    """
    try:
        mods = [modifier_by_identifier(mod_id) for mod_id in modifier_ids]
        output_file.write(json.dumps([mod.to_dict() for mod in mods]))
    except Exception as e:
        _logger.exception(
            'Retrieval from modifier library failed.\n{}'.format(e))
        sys.exit(1)
    else:
        sys.exit(0)


@lib.command('modifier-sets-by-id')
@click.argument('modifier-set-ids', nargs=-1)
@click.option('--none-defaults', help='Boolean to note whether default modifiers '
              'in the set should be included in detail (False) or should be None '
              '(True).', type=bool, default=True, show_default=True)
@click.option('--abridged', help='Optional boolean to note wether an abridged definition'
              ' should be returned.', type=bool, default=False, show_default=True)
@click.option('--output-file', help='Optional file to output the JSON string of '
              'the object. By default, it will be printed out to stdout',
              type=click.File('w'), default='-', show_default=True)
def modifier_sets_by_id(modifier_set_ids, none_defaults, abridged, output_file):
    """Get several modifier set definitions from the standards lib at once.
    \n
    Args:
        modifier_set_ids: A list of modifier set identifiers to be retrieved
            from the library.
    """
    try:
        m_sets = [modifier_set_by_identifier(m_id) for m_id in modifier_set_ids]
        output_file.write(json.dumps([ms.to_dict(
            none_for_defaults=none_defaults, abridged=abridged) for ms in m_sets]))
    except Exception as e:
        _logger.exception(
            'Retrieval from modifier set library failed.\n{}'.format(e))
        sys.exit(1)
    else:
        sys.exit(0)


@lib.command('to-model-properties')
@click.option(
    '--standards-folder', '-s', default=None, help='A directory containing sub-folders '
    'of resource objects (modifiers, modifiersets) to be loaded as '
    'ModelRadianceProperties. Note that this standards folder MUST contain these '
    'sub-folders. Each sub-folder can contain JSON files of objects following '
    'honeybee schema or RAD/MAT files (if appropriate). If None, the honeybee '
    'default standards folder will be used.', type=click.Path(
        exists=True, file_okay=False, dir_okay=True, resolve_path=True)
)
@click.option(
    '--exclude-abridged/--include-abridged', ' /-a', help='Flag to note whether '
    'fully abridged objects in the user standards library should be included in '
    'the output file. This is useful when some of the sub-objects contained within '
    'the user standards are referenced in another installed standards package that '
    'is not a part of the user personal standards library (eg. honeybee-standards). '
    'When abridged objects are excluded, only objects that contain all '
    'sub-objects within the user library will be in the output-file.',
    default=True, show_default=True
)
@click.option(
    '--output-file', '-f', help='Optional JSON file to output the JSON string of '
    'the translation. By default this will be printed out to stdout',
    type=click.File('w'), default='-', show_default=True
)
def to_model_properties(standards_folder, exclude_abridged, output_file):
    """Translate a lib folder of standards to a JSON of honeybee ModelRadianceProperties.

    This is useful in workflows where one must import everything within a user's
    standards folder and requires all objects to be in a consistent format.
    All objects in the resulting ModelRadianceProperties will be abridged and
    duplicated objects in the folder will be removed such that there
    is only one of each object.
    """
    try:
        # set the folder to the default standards_folder if unspecified
        folder = standards_folder if standards_folder is not None else \
            folders.standards_data_folder

        # load modifiers from the standards folder
        mod_folder = os.path.join(folder, 'modifiers')
        all_m = load_modifiers_from_folder(mod_folder)

        # load modifier sets from the standards folder
        mod_set_folder = os.path.join(folder, 'modifiersets')
        all_mod_sets, misc_m = load_modifiersets_from_folder(mod_set_folder, all_m)
        all_mods = set(list(all_m.values()) + misc_m)

        # add all object dictionaries into one object
        base = {'type': 'ModelRadianceProperties'}
        base['modifiers'] = [m.to_dict() for m in all_mods]
        base['modifier_sets'] = \
            [ms.to_dict(abridged=True) for ms in all_mod_sets.values()]

        # if set to include abridged, add any of such objects to the dictionary
        if not exclude_abridged:
            _add_abridged_objects(base['modifiers'], mod_folder)
            _add_abridged_objects(base['modifier_sets'], mod_set_folder)

        # write out the JSON file
        output_file.write(json.dumps(base))
    except Exception as e:
        _logger.exception('Loading standards to properties failed.\n{}'.format(e))
        sys.exit(1)
    else:
        sys.exit(0)


def _add_abridged_objects(model_prop_array, lib_folder):
    """Add abridged resource objects to an existing model properties array.
    
    Args:
        model_prop_array: An array of resource object dictionaries from a
            ModelRadianceProperties dictionary.
        lib_folder: A folder from which abridged objects will be loaded.
    """
    obj_ids = set(obj['identifier'] for obj in model_prop_array)
    for f in os.listdir(lib_folder):
        f_path = os.path.join(lib_folder, f)
        if os.path.isfile(f_path) and f_path.endswith('.json'):
            with open(f_path) as json_file:
                data = json.load(json_file)
            if 'type' in data:  # single object
                if data['identifier'] not in obj_ids:
                    model_prop_array.append(data)
            else:  # a collection of several objects
                for obj_identifier in data:
                    if obj_identifier not in obj_ids:
                        model_prop_array.append(data[obj_identifier])


@lib.command('purge')
@click.option(
    '--standards-folder', '-s', default=None, help='A directory containing sub-folders '
    'of resource objects (modifiers, modifiersets) to be purged of files. If '
    'unspecified, the current user honeybee default standards folder will be used.',
    type=click.Path(exists=True, file_okay=False, dir_okay=True, resolve_path=True)
)
@click.option(
    '--json-only/--all', ' /-a', help='Flag to note whether only JSON files should '
    'be purged from the library or all files should be purged, including RAD files. '
    'Given that all objects added to the library through the `add` command will always '
    'be JSON, only purging the JSONs is useful when one wishes to clear these objects '
    'while preserving objects that originated from other sources.',
    default=True, show_default=True
)
@click.option(
    '--backup/--no-backup', ' /-xb', help='Flag to note whether a backup .zip file '
    'of the user standards library should be made before the purging operation. '
    'This is done by default in case the user ever wants to recover their old '
    'standards but can be turned off if a backup is not desired.',
    default=True, show_default=True
)
@click.option(
    '--log-file', '-log', help='Optional file to output a log of the purging process. '
    'By default this will be printed out to stdout',
    type=click.File('w'), default='-', show_default=True
)
def purge_lib(standards_folder, json_only, backup, log_file):
    """Purge the library of all user radiance standards that it contains.

    This is useful when a user's standard library has become filled with duplicated
    objects or the user wishes to start fresh by re-exporting updated objects.
    """
    try:
        # set the folder to the default standards_folder if unspecified
        folder = standards_folder if standards_folder is not None else \
            folders.standards_data_folder
        resources = ('modifiers', 'modifiersets')
        sub_folders = [os.path.join(folder, std) for std in resources]

        # make a backup of the folder if requested
        if backup:
            r_names, s_files, s_paths = [], [], []
            for sf, r_name in zip(sub_folders, resources):
                for s_file in os.listdir(sf):
                    s_path = os.path.join(sf, s_file)
                    if os.path.isfile(s_path):
                        r_names.append(r_name)
                        s_files.append(s_file)
                        s_paths.append(s_path)
            if len(s_paths) != 0:  # there are resources to back up
                backup_name = '.standards_backup_{}.zip'.format(
                    str(datetime.now()).split('.')[0].replace(':', '-'))
                backup_file = os.path.join(os.path.dirname(folder), backup_name)
                with zipfile.ZipFile(backup_file, 'w') as zf:
                    for r_name, s_file, s_path in zip(r_names, s_files, s_paths):
                        zf.write(s_path, os.path.join(r_name, s_file))

        # loop through the sub-folders and delete the files
        rel_files = []
        for sf in sub_folders:
            for s_file in os.listdir(sf):
                s_path = os.path.join(sf, s_file)
                if os.path.isfile(s_path):
                    if json_only:
                        if s_file.lower().endswith('.json'):
                            rel_files.append(s_path)
                    else:
                        rel_files.append(s_path)
        purged_files, fail_files = [], []
        for rf in rel_files:
            try:
                os.remove(rf)
                purged_files.append(rf)
            except Exception:
                fail_files.append(rf)

        # report all of the deleted files in the log file
        if len(rel_files) == 0:
            log_file.write('The standards folder is empty so no files were removed.')
        if len(purged_files) != 0:
            msg = 'The following files were removed in the purging ' \
                'operations:\n{}\n'.format('  \n'.join(purged_files))
            log_file.write(msg)
        if len(fail_files) != 0:
            msg = 'The following files could not be removed in the purging ' \
                'operations:\n{}\n'.format('  \n'.join(fail_files))
            log_file.write(msg)
    except Exception as e:
        _logger.exception('Purging user standards library failed.\n{}'.format(e))
        sys.exit(1)
    else:
        sys.exit(0)


@lib.command('add')
@click.argument('properties-file', type=click.Path(
    exists=True, file_okay=True, dir_okay=False, resolve_path=True))
@click.option(
    '--standards-folder', '-s', default=None, help='A directory containing sub-folders '
    'of resource objects (modifiers, modifiersets) to which the properties-file objects '
    'will be added. If unspecified, the current user honeybee default standards folder '
    'will be used.', type=click.Path(
        exists=True, file_okay=False, dir_okay=True, resolve_path=True)
)
@click.option(
    '--log-file', '-log', help='Optional file to output a log of the purging process. '
    'By default this will be printed out to stdout',
    type=click.File('w'), default='-', show_default=True
)
def add_to_lib(properties_file, standards_folder, log_file):
    """Add an object or set of objects to the user's standard library.

    \b
    Args:
        properties_file: A JSON file of a ModelRadianceProperties object containing
            the objects to be written into the user standards library. All sub-objects
            within this ModelRadianceProperties object must be Abridged if the sub-object
            has an abridged schema and these abridged schemas are allowed to
            reference either other objects in the ModelRadianceProperties or existing
            objects within the standards library.
    """
    try:
        # set the folder to the default standards_folder if unspecified
        folder = standards_folder if standards_folder is not None else \
            folders.standards_data_folder

        # load up the model radiance properties from the JSON
        with open(properties_file) as inf:
            data = json.load(inf)
        assert 'type' in data, 'Properties file lacks required type key.'
        assert data['type'] == 'ModelRadianceProperties', 'Expected ' \
            'ModelRadianceProperties JSON object. Got {}.'.format(data['type'])
        success_objects, dup_id_objects, mis_dep_objects = [], [], []

        # extract, check, and write the modifiers
        mods = {}
        if 'modifiers' in data and data['modifiers'] is not None and \
                len(data['modifiers']) != 0:
            for mod_obj in data['modifiers']:
                msg = _object_message('Modifier', mod_obj)
                if mod_obj['identifier'] in MODIFIERS:
                    dup_id_objects.append(msg)
                else:
                    try:
                        mods[mod_obj['identifier']] = dict_to_modifier(mod_obj)
                        success_objects.append(msg)
                    except (ValueError, KeyError, AssertionError):
                        mis_dep_objects.append(msg)
        if mods:
            mod_dict = {m.identifier: m.to_dict() for m in mods.values()}
            mod_json = os.path.join(folder, 'modifiers', 'custom_modifiers.json')
            _update_user_json(mod_dict, mod_json)

        # extract, check, and write the modifier sets
        mod_sets = {}
        if 'modifier_sets' in data and data['modifier_sets'] is not None:
            for ms in data['modifier_sets']:
                msg = _object_message('Modifier Set', ms)
                if ms['identifier'] in MODIFIER_SETS:
                    dup_id_objects.append(msg)
                else:
                    try:
                        mod_sets[ms['identifier']] = \
                            lib_dict_abridged_to_modifier_set(ms, mods)
                        success_objects.append(msg)
                    except (ValueError, KeyError, AssertionError):
                        mis_dep_objects.append(msg)
        if mod_sets:
            ms_dict = {m.identifier: m.to_dict(abridged=True) for m in mod_sets.values()}
            ms_json = os.path.join(folder, 'modifiersets', 'custom_sets.json')
            _update_user_json(ms_dict, ms_json)

        # write a report of the objects that were or were not added
        success_objects, dup_id_objects, mis_dep_objects
        m_start = 'THESE OBJECTS'
        if len(success_objects) != 0:
            msg = '{} WERE SUCCESSFULLY ADDED TO THE STANDARDS LIBRARY:\n{}\n\n'.format(
                m_start, '  \n'.join(success_objects))
            log_file.write(msg)
        if len(dup_id_objects) != 0:
            msg = '{} WERE NOT ADDED SINCE THEY ALREADY EXIST IN THE STANDARDS ' \
                'LIBRARY:\n{}\n\n'.format(m_start, '  \n'.join(dup_id_objects))
            log_file.write(msg)
        if len(mis_dep_objects) != 0:
            msg = '{} WERE NOT ADDED BECAUSE THEY ARE INVALID OR ARE MISSING ' \
                'DEPENDENT OBJECTS:\n{}\n\n'.format(m_start, '  \n'.join(mis_dep_objects))
            log_file.write(msg)
    except Exception as e:
        _logger.exception('Adding to user standards library failed.\n{}'.format(e))
        sys.exit(1)
    else:
        sys.exit(0)


def _object_message(obj_type, obj_dict):
    """Get the reporting message of an object to add to the user library."""
    obj_name = obj_dict['display_name'] if 'display_name' in obj_dict and \
        obj_dict['display_name'] is not None else obj_dict['identifier']
    return '{}: {}'.format(obj_type, obj_name)


def _update_user_json(dict_to_add, user_json):
    """Update a JSON file within a user standards folder."""
    if os.path.isfile(user_json):
        with open(user_json) as inf:
            exist_data = json.load(inf)
        dict_to_add.update(exist_data)
    with open(user_json, 'w') as outf:
        json.dump(dict_to_add, outf, indent=4)

