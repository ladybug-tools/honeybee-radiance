"""honeybee radiance model-editing commands."""
import click
import sys
import os
import logging
import json

from honeybee.model import Model

_logger = logging.getLogger(__name__)


@click.group(help='Commands for translating Honeybee JSON files to/from RAD.')
def edit():
    pass


@edit.command('mirror-model-sensors')
@click.argument('model-json', type=click.Path(
    exists=True, file_okay=True, dir_okay=False, resolve_path=True))
@click.option('--output-file', '-f', help='Optional hbjson file to output the JSON '
              'string of the converted model. By default this will be printed out '
              'to stdout', type=click.File('w'), default='-', show_default=True)
def mirror_model_sensors(model_json, output_file):
    """Mirror a honeybee Model's SensorGrids and format them for thermal mapping.

    This involves setting the direction of every sensor to point up (0, 0, 1) and
    then adding a mirrored sensor grid with the same sensor positions that all
    point downward. In thermal mapping workflows, the upward-pointing grids can
    be used to account for direct and diffuse shortwave irradiance while the
    downard pointing grids account for ground-reflected shortwave irradiance.

    \b
    Args:
        model_json: Full path to a Model JSON file.
    """
    try:
        # re-serialize the Model to Python
        with open(model_json) as json_file:
            data = json.load(json_file)
        model = Model.from_dict(data)

        # loop through the sensor grids and reformat them
        mirror_grids, up_dir, down_dir = [], None, (0, 0, -1)
        for grid in model.properties.radiance.sensor_grids:
            # ensure that all sensors are pointing upward
            grid.group_identifier = None
            for sensor in grid:
                sensor.dir = up_dir
            # create the mirror grid will all sensors pointing downward
            mir_grid = grid.duplicate()
            mir_grid.identifier = '{}_ref'.format(grid.identifier)
            for sensor in mir_grid:
                sensor.dir = down_dir
            mirror_grids.append(mir_grid)
        model.properties.radiance.add_sensor_grids(mirror_grids)

        # write the Model JSON string
        output_file.write(json.dumps(model.to_dict()))
    except Exception as e:
        _logger.exception('Model translation failed.\n{}'.format(e))
        sys.exit(1)
    else:
        sys.exit(0)
