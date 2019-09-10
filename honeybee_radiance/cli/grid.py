"""honeybee radiance grid commands.""" 

try:
    import click
except ImportError:
    raise ImportError(
        'click is not installed. Try `pip install . [cli]` command.'
    )

import sys
import honeybee_radiance.sensorgrid as sensorgrid
import os
import logging
import re

_logger = logging.getLogger(__name__)

@click.group(help='Commands for generating and modifying sensor grids.')
def grid():
    pass

@grid.command('split')
@click.argument('grid-file')
@click.argument('count', type=int)
@click.option('--folder', help='Optional output folder.', default='.', show_default=True)
def split_grid(grid_file, count, folder):
    """Split a radiance grid file into smaller grids based on maximum sensor count.

    \b
    Args:
        grid-file: Full path to input sensor grid file.
        count: Maximum number of sensors in new files. The number will be rounded to
            closest round number for each file. For example if the input file has 21
            sensors and input count is set to 5 this command will generate 4 files where
            the first three files will have 5 sensors and the last file will have 6. 
    """
    try:
        grid = sensorgrid.SensorGrid.from_file(grid_file)
        file_count = int(round(grid.count / count))
        files = grid.to_files(folder, file_count, mkdir=True)
        for f in files:
            click.echo(f)
    except Exception:
        _logger.exception('Failed to split grid file.')
        sys.exit(1)


@grid.command('merge')
@click.argument('input-folder')
@click.argument('base-name')
@click.argument('extension', default='.pts')
@click.option('--folder', help='Optional output folder.', default='.', show_default=True)
def merge_grid(input_folder, base_name, extension, folder):
    """Merge several radiance grid files into a single file.

    \b
    Args:
        input_folder: Input folder.
        base_name: File base name. All of the files must start with base name and
            continue with _ and an integer values.
        extension: File extention. [Default: .pts]
    """
    try:
        pattern = r'{}_\d+{}'.format(base_name, extension)
        grids = sorted(f for f in os.listdir(input_folder) if re.match(pattern, f))
        if len(grids) == 0:
            raise ValueError('Found no file to merge.')
        output_file = os.path.join(folder, base_name + extension)
        with open(output_file, 'w') as outf:
            for f in grids:
                with open(os.path.join(input_folder, f)) as inf:
                    for line in inf:
                        if not line.strip():
                            continue
                        outf.write(line)
    except Exception:
        _logger.exception('Failed to merge grid file.')
        sys.exit(1)
