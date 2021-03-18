"""honeybee radiance model-editing commands."""
import click
import sys
import logging
import json

from honeybee.model import Model
from honeybee.units import parse_distance_string

_logger = logging.getLogger(__name__)


@click.group(help='Commands for translating Honeybee JSON files to/from RAD.')
def edit():
    pass


@edit.command('add-room-sensors')
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
              'include a Mesh3D object that aligns with the grid positions '
              'under the "mesh" property of each grid. Excluding the mesh can greatly '
              'reduce model size but will mean Radiance results cannot be visualized '
              'as colored meshes.', default=True)
@click.option('--keep-out/--remove-out', ' /-out', help='Flag to note whether an extra '
              'check should be run to remove sensor points that lie outside the Room '
              'volume. Note that this can add significantly to the runtime and this '
              'check is not necessary in the case that all walls are vertical '
              'and all floors are horizontal.', default=True, show_default=True)
@click.option('--room', '-r', multiple=True, help='Room identifier(s) to specify the '
              'room(s) for which sensor grids should be generated. By default, all '
              'rooms will get sensor grids.')
@click.option('--output-file', '-f', help='Optional hbjson file to output the JSON '
              'string of the new model. By default this will be printed out '
              'to stdout', type=click.File('w'), default='-', show_default=True)
def add_room_sensors(model_json, grid_size, offset, include_mesh, keep_out,
                     room, output_file):
    """Add SensorGrids to a honeybee model generated from the Room's floors.

    The grids will have the rooms referenced in their room_identifier property.

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
        model.properties.radiance.add_sensor_grids(sensor_grids)

        # write the Model JSON string
        output_file.write(json.dumps(model.to_dict()))
    except Exception as e:
        _logger.exception('Model translation failed.\n{}'.format(e))
        sys.exit(1)
    else:
        sys.exit(0)


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
        # re-serialize the Model and loop through the sensor grids to reformat them
        model = Model.from_hbjson(model_json)
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
