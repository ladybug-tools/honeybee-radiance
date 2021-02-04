"""honeybee radiance standards library commands."""
import click
import sys
import logging
import json

from honeybee_radiance.lib.modifiers import modifier_by_identifier, MODIFIERS
from honeybee_radiance.lib.modifiersets import modifier_set_by_identifier, \
    MODIFIER_SETS

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
