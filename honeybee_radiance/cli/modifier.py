"""honeybee radiance modifier commands."""
import click
import sys
import os
import logging
import json

from honeybee_radiance.sensorgrid import SensorGrid


_logger = logging.getLogger(__name__)


@click.group(help='Commands for generating and modifying Radiance modifiers.')
def modifier():
    pass


@modifier.command('split-modifiers')
@click.argument('modifier-file', type=click.Path(
    exists=True, file_okay=True, dir_okay=False, resolve_path=True))
@click.argument(
    'output-folder',
    type=click.Path(file_okay=False, dir_okay=True, resolve_path=True))
@click.option(
    '--sensor-count', '-sc', help='The number of sensors in the sensor grid '
    'that will be used in rcontrib with the distributed modifiers.', 
    type=int, default=5000, show_default=True)
@click.option(
    '--grid-file', '-gf', help='Full path to a sensor grid file. This file '
    'is used to count the number of sensors and will override the '
    '--sensor-count option.',
    type=click.Path(exists=True, file_okay=True, dir_okay=False, resolve_path=True),
    default=None, show_default=True)
@click.option(
    '--max-value', '-max', help='An optional integer to define the maximum value '
    'allowed when multiplying the number of sensors with the number of modifiers '
    'in the distributed modifiers. Default: 40000000.',
    type=int, default=40000000, show_default=True)
@click.option(
    '--sensor-multiplier', '-d', help='An optional integer to be multiplied by '
    'the grid count to yield a final number of the sensor count. This is useful '
    'in workflows where the sensor grids are modified such as when calculating '
    'view factor. Default: 1.', type=int, default=1)
def split_modifiers(
    modifier_file, output_folder, sensor_count, grid_file, max_value,
    sensor_multiplier
):
    """Split a list of modifiers into multiple files.

    This command splits the modifiers based on the sensor count and the max value.
    The max value is divided by the sensor count to calculate the maximum number
    of modifiers in each distributed file of modifiers.

    This command creates a new folder with evenly distributed modifiers. The folder
    will include a ``_dist_info.json`` file which has the information to recreate the
    original input files from this folder and the results generated based on the modifiers
    in this folder.

    ``_redist_info.json`` file includes an array of JSON objects. Each object has
    the distribution information, which in comparison to the command to split grids
    is much simpler.

    \b
    Args:
        modifier_file: Full path to a file with Radiance modifiers. The modifiers
            must be the identifiers of the modifiers and not the actual Radiance
            description of the modifiers.
        output_folder: A new folder to write the newly created files.
    """
    try:
        if grid_file:
            sg = SensorGrid.from_file(grid_file)
            sensor_count = sg.count
        sensor_count *= sensor_multiplier

        with open(modifier_file, 'r') as file:
            modifiers = [modifier.strip() for modifier in file.readlines()]

        modifier_count = len(modifiers)

        max_lines_per_file = int(max_value / sensor_count)
        lines_per_file = max(1, max_lines_per_file)
        dist_count = int(len(modifiers) / lines_per_file)
        if len(modifiers) % lines_per_file != 0:
            dist_count += 1

        mod_per_dist = int(round(modifier_count / dist_count)) or 1

        # create output folder
        if not os.path.isdir(output_folder):
            os.mkdir(output_folder)

        remainder = modifier_count % dist_count  # extra lines to distribute

        start_index = 0
        dist_info = []
        out_dist_info = []
        for i in range(dist_count):
            end_index = start_index + mod_per_dist + (1 if i <= remainder else 0)

            lines_to_write = modifiers[start_index:end_index]

            dist_info.append(
                {
                    'dist_info': [{'identifier': i}]
                }
            )
            out_dist_info.append(
                {
                    'identifier': str(i),
                    'count': len(lines_to_write)
                }
            )
            # create a file and write the lines
            with open(os.path.join(output_folder, '%s.mod' % i), 'w') as f:
                f.write('\n'.join(lines_to_write))

            # update the start index for the next iteration
            start_index = end_index

        dist_info_file = os.path.join(output_folder, '_redist_info.json')
        with open(dist_info_file, 'w') as dist_out_file:
            json.dump(dist_info, dist_out_file, indent=2)

        dist_info_file = os.path.join(output_folder, '_info.json')
        with open(dist_info_file, 'w') as dist_out_file:
            json.dump(out_dist_info, dist_out_file, indent=2)
    except Exception:
        _logger.exception('Failed to distribute sensor grids in folder.')
        sys.exit(1)
    else:
        sys.exit(0)
