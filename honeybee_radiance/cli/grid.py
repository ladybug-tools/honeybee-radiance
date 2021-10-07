"""honeybee radiance grid commands."""
import click
import sys
import os
import logging
import re
import json

from honeybee.model import Model
from honeybee.units import parse_distance_string
import honeybee_radiance.sensorgrid as sensorgrid
from honeybee_radiance_folder.gridutil import redistribute_sensors, \
    restore_original_distribution

_logger = logging.getLogger(__name__)


@click.group(help='Commands for generating and modifying sensor grids.')
def grid():
    pass


@grid.command('split')
@click.argument('grid-file', type=click.Path(
    exists=True, file_okay=True, dir_okay=False, resolve_path=True))
@click.argument('count', type=int)
@click.option('--folder', help='Output folder.', default='.', show_default=True,
              type=click.Path(file_okay=False, dir_okay=True, resolve_path=True))
@click.option('--log-file', help='Optional log file to output the name of the newly'
              ' created grids. By default the list will be printed out to stdout',
              type=click.File('w'), default='-')
def split_grid(grid_file, count, folder, log_file):
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
        file_count = max(1, int(round(grid.count / count)))
        files = grid.to_files(folder, file_count, mkdir=True)

        log_file.write(json.dumps(files))
    except Exception:
        _logger.exception('Failed to split grid file.')
        sys.exit(1)
    else:
        sys.exit(0)


@grid.command('merge')
@click.argument('input-folder', type=click.Path(
    file_okay=False, dir_okay=True, resolve_path=True))
@click.argument('base-name', type=str)
@click.argument('extension', default='.pts', type=str)
@click.option('--folder', help='Optional output folder.', default='.', show_default=True)
@click.option('--name', help='Optional output filename. Default is base-name.')
def merge_grid(input_folder, base_name, extension, folder, name):
    """Merge several radiance files into a single file.

    This command removes headers from file if it exist.

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
        name = name or base_name
        output_file = os.path.normpath(os.path.join(folder, name + extension))
        # get the new dir name as grid name might be group/name
        dirname = os.path.dirname(output_file)
        if dirname and not os.path.exists(dirname):
            os.makedirs(dirname)

        with open(output_file, 'w') as outf:
            for f in grids:
                with open(os.path.join(input_folder, f)) as inf:
                    first_line = next(inf)
                    if first_line[:10] == '#?RADIANCE':
                        for line in inf:
                            if line[:7] == 'FORMAT=':
                                # pass next empty line
                                next(inf)
                                break
                            continue
                    else:
                        outf.write(first_line)
                    # add rest of the file to outfile
                    for line in inf:
                        outf.write(line)
    except Exception:
        _logger.exception('Failed to merge grid files.')
        sys.exit(1)
    else:
        sys.exit(0)


@grid.command('from-rooms')
@click.argument('model-json', type=click.Path(
    exists=True, file_okay=True, dir_okay=False, resolve_path=True))
@click.option('--grid-size', '-s', help='A number for the dimension of the mesh grid '
              'cells. This can include the units of the distance (eg. 1ft) '
              'or, if no units are provided, the value will be interpreted in the '
              'honeybee model units.', type=str, default='0.5m', show_default=True)
@click.option('--offset', '-o', help='A number for the distance at which the '
              'the sensor grid should be offset from the floor. This can include the '
              'units of the distance (eg. 3ft) or, if no units are provided, the '
              'value will be interpreted in the honeybee model units.',
              type=str, default='0.8m', show_default=True)
@click.option('--include-mesh/--exclude-mesh', ' /-xm', help='Flag to note whether to '
              'include a Mesh3D object that aligns with the grid positions under the '
              '"mesh" property of each grid. Excluding the mesh can reduce size but '
              'will mean Radiance results cannot be visualized as colored meshes.',
              default=True)
@click.option('--keep-out/--remove-out', ' /-out', help='Flag to note whether an extra '
              'check should be run to remove sensor points that lie outside the Room '
              'volume. Note that this can add significantly to the runtime and this '
              'check is not necessary in the case that all walls are vertical '
              'and all floors are horizontal.', default=True, show_default=True)
@click.option('--room', '-r', multiple=True, help='Room identifier to specify the '
              'room for which sensor grids should be generated. You can pass multiple '
              'rooms (each preceded by -r). By default, all rooms get sensor grids.')
@click.option('--write-json/--write-pts', ' /-pts', help='Flag to note whether output '
              'data collection should be in JSON format or the typical CSV-style format '
              'of the Radiance .pts files.', default=True, show_default=True)
@click.option('--folder', help='Optional output folder. If specified, the --output-file '
              'will be ignored and each sensor grid will be written into its own '
              '.json or .pts file within the folder.', default=None,
              type=click.Path(exists=True, file_okay=False,
                              dir_okay=True, resolve_path=True))
@click.option('--output-file', '-f', help='Optional file to output the JSON or CSV '
              'string of the sensor grids. By default this will be printed '
              'to stdout', type=click.File('w'), default='-', show_default=True)
def from_rooms(model_json, grid_size, offset, include_mesh, keep_out, room,
               write_json, folder, output_file):
    """Generate SensorGrids from the Room floors of a honeybee model.

    \b
    Args:
        model_json: Full path to a Model JSON file.
    """
    try:
        # re-serialize the Model and extract rooms and units
        model = Model.from_hbjson(model_json)
        rooms = model.rooms if room is None or len(room) == 0 else \
            [r for r in model.rooms if r.identifier in room]
        grid_size = parse_distance_string(grid_size, model.units)
        offset = parse_distance_string(offset, model.units)

        # loop through the rooms and generate sensor grids
        sensor_grids = []
        remove_out = not keep_out
        for room in rooms:
            sg = room.properties.radiance.generate_sensor_grid(
                grid_size, offset=offset, remove_out=remove_out)
            sensor_grids.append(sg)
        if not include_mesh:
            for sg in sensor_grids:
                sg.mesh = None

        # write the sensor grids to the output file or folder
        if folder is None:
            if write_json:
                output_file.write(json.dumps([sg.to_dict() for sg in sensor_grids]))
            else:
                output_file.write('\n'.join([sg.to_radiance() for sg in sensor_grids]))
        else:
            if write_json:
                for sg in sensor_grids:
                    sg.to_json(folder)
            else:
                for sg in sensor_grids:
                    sg.to_file(folder)
    except Exception as e:
        _logger.exception('Model translation failed.\n{}'.format(e))
        sys.exit(1)
    else:
        sys.exit(0)


@grid.command('split-folder')
@click.argument(
    'input-folder',
    type=click.Path(exists=True, file_okay=False, dir_okay=True, resolve_path=True))
@click.argument(
    'output-folder',
    type=click.Path(file_okay=False, dir_okay=True, resolve_path=True))
@click.argument('grid-count', type=int)
@click.option(
    '--grid-divisor', '-d', help='An optional integer to be divided by the grid-count '
    'to yield a final number of grids to generate. This is useful in workflows where '
    'the grid-count is being interpreted as a cpu-count but there are multiple '
    'processors acting on a single grid. To ignore this limitation set the value '
    'to 1. Default: 1.', type=int, default=1)
@click.option(
    '--min-sensor-count', '-msc', help='Minimum number of sensors in each output grid. '
    'Use this number to ensure the number of sensors in output grids never gets very '
    'small. This input will override the input grid-count when specified. '
    'To ignore this limitation, set the value to 1. Default: 1.', type=int,
    default=1)
def split_grid_folder(
        input_folder, output_folder, grid_count, grid_divisor, min_sensor_count):
    """Create new sensor grids folder with evenly distribute sensors.

    This function creates a new folder with evenly distributed sensor grids. The folder
    will include a ``_dist_info.json`` file which has the information to recreate the
    original input files from this folder and the results generated based on the grids
    in this folder.

    ``_dist_info.json`` file includes an array of JSON objects. Each object has the
    ``id`` or the original file and the distribution information. The distribution
    information includes the id of the new files that the sensors has been distributed
    to and the start and end line in the target file.

    This file is being used to restructure the data that is generated based on the newly
    created sensor grids.

    .. code-block:: python

        [
          {
            "id": "room_1",
            "dist_info": [
              {"id": 0, "st_ln": 0, "end_ln": 175},
              {"id": 1, "st_ln": 0, "end_ln": 21}
            ]
          },
          {
            "id": "room_2",
            "dist_info": [
              {"id": 1, "st_ln": 22, "end_ln": 135}
            ]
          }
        ]

    Args:
        input_folder: Input sensor grids folder.
        output_folder: A new folder to write the newly created files.
        grid_count: Number of output sensor grids to be created. This number
            is usually equivalent to the number of processes that will be used to run
            the simulations in parallel.
    """
    try:
        grid_count = int(grid_count / grid_divisor)
        grid_count = 1 if grid_count < 1 else grid_count
        redistribute_sensors(input_folder, output_folder, grid_count, min_sensor_count)
    except Exception:
        _logger.exception('Failed to distribute sensor grids in folder.')
        sys.exit(1)
    else:
        sys.exit(0)


@grid.command('merge-folder')
@click.argument(
    'input-folder',
    type=click.Path(exists=True, file_okay=False, dir_okay=True, resolve_path=True))
@click.argument(
    'output-folder',
    type=click.Path(file_okay=False, dir_okay=True, resolve_path=True))
@click.argument('extension', type=str)
def merge_grid_folder(input_folder, output_folder, extension):
    """Restructure files in a distributed folder.

    Args:
        input_folder: Path to input folder.
        output_folder: Path to the new restructured folder
        extention: Extension of the files to collect data from. It will be ``pts`` for
            sensor files. Another common extension is ``ill`` for the results of daylight
            studies.
    """
    try:
        restore_original_distribution(input_folder, output_folder, extension)
    except Exception:
        _logger.exception('Failed to restructure data from folder.')
        sys.exit(1)
    else:
        sys.exit(0)
