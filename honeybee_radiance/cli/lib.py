"""honeybee radiance standards library commands."""
import click
import sys
import os
import logging
import json

from honeybee_radiance.config import folders
from honeybee_radiance.lib.modifiers import modifier_by_identifier, MODIFIERS
from honeybee_radiance.lib.modifiersets import modifier_set_by_identifier, \
    MODIFIER_SETS

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
    '--standards-folder', '-s', default=None, help='A directory containing subfolders '
    'of resource objects (modifiers, modifiersets) to be loaded as '
    'ModelRadianceProperties. Note that this standards folder MUST contain these '
    'subfolders. Each sub-folder can contain JSON files of objects following '
    'honeybee schema or RAD/MAT files (if appropriate). If None, the honeybee '
    'default standards folder will be used.',type=click.Path(
        exists=True, file_okay=False, dir_okay=True, resolve_path=True)
)
@click.option(
    '--output-file', '-f', help='Optional JSON file to output the JSON string of '
    'the translation. By default this will be printed out to stdout',
    type=click.File('w'), default='-', show_default=True
)
def to_model_properties(standards_folder, output_file):
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

        # write out the JSON file
        output_file.write(json.dumps(base))
    except Exception as e:
        _logger.exception('Loading standards to properties failed.\n{}'.format(e))
        sys.exit(1)
    else:
        sys.exit(0)
