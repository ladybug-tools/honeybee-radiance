"""honeybee-radiance commands which will be added to honeybee command line interface."""
import click
import sys
import logging
import json

from honeybee.cli import main
from ..config import folders
from .edit import edit
from .translate import translate
from .lib import lib
from .sky import sky
from .grid import grid
from .view import view
from .sunpath import sunpath
from .octree import octree
from .raytrace import raytrace
from .rpict import rpict
from .dc import dc
from .postprocess import post_process
from .mtx import mtxop


_logger = logging.getLogger(__name__)

# command group for all radiance extension commands.
@click.group(help='honeybee radiance commands.')
@click.version_option()
def radiance():
    pass


@radiance.command('config')
@click.option('--output-file', help='Optional file to output the JSON string of '
              'the config object. By default, it will be printed out to stdout',
              type=click.File('w'), default='-', show_default=True)
def config(output_file):
    """Get a JSON object with all configuration information"""
    try:
        config_dict = {
            'radiance_path': folders.radiance_path,
            'radbin_path': folders.radbin_path,
            'radlib_path': folders.radlib_path,
            'radiance_version': folders.radiance_version_str,
            'standards_data_folder': folders.standards_data_folder,
            'modifier_lib': folders.modifier_lib,
            'modifierset_lib': folders.modifierset_lib
        }
        output_file.write(json.dumps(config_dict, indent=4))
    except Exception as e:
        _logger.exception('Failed to retrieve configurations.\n{}'.format(e))
        sys.exit(1)
    else:
        sys.exit(0)


# add sub-commands to radiance
radiance.add_command(edit)
radiance.add_command(translate)
radiance.add_command(lib)
radiance.add_command(sky)
radiance.add_command(grid)
radiance.add_command(view)
radiance.add_command(sunpath)
radiance.add_command(octree)
radiance.add_command(raytrace)
radiance.add_command(rpict)
radiance.add_command(dc)
radiance.add_command(post_process, name='post-process')
radiance.add_command(mtxop)

# add radiance sub-commands to honeybee CLI
main.add_command(radiance)
