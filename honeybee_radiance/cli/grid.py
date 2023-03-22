"""honeybee radiance grid commands."""
import click
import sys
import os
import logging
import re
import json
import shutil

from ladybug_geometry.geometry3d import Vector3D, Face3D
from ladybug.futil import preparedir
from honeybee.model import Model
from honeybee.units import parse_distance_string
from honeybee.typing import clean_rad_string, clean_and_id_rad_string

from honeybee_radiance.sensorgrid import SensorGrid
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
        grid = SensorGrid.from_file(grid_file)
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
        extension: File extension. [Default: .pts]
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


@grid.command('split-folder')
@click.argument(
    'input-folder',
    type=click.Path(file_okay=False, dir_okay=True, resolve_path=True))
@click.argument(
    'output-folder',
    type=click.Path(file_okay=False, dir_okay=True, resolve_path=True))
@click.argument('grid-count', type=int)
@click.argument('extension', default='.pts', type=str)
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
@click.option(
    '--grid-info-file', help='Optional input JSON file containing information about '
    'the sensor grids to be split. If unspecified, it will be assumed that this '
    'JSON already exists in the input-folder with the name _info.json', default=None,
    type=click.Path(file_okay=True, dir_okay=False, resolve_path=True))
def split_grid_folder(
    input_folder, output_folder, grid_count, extension,
    grid_divisor, min_sensor_count, grid_info_file
):
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

    \b
    Args:
        input_folder: Input sensor grids folder.
        output_folder: A new folder to write the newly created files.
        grid_count: Number of output sensor grids to be created. This number
            is usually equivalent to the number of processes that will be used to run
            the simulations in parallel.
        extension: Extension of the files to split. The default is ``pts`` for
            sensor files. Another common extension is ``csv`` for data aligned with
            the sensor grids.
    """
    try:
        if os.path.isdir(input_folder):
            if grid_info_file is not None and os.path.isfile(grid_info_file):
                info_file = os.path.join(input_folder, '_info.json')
                shutil.copyfile(grid_info_file, info_file)
            grid_count = int(grid_count / grid_divisor)
            grid_count = 1 if grid_count < 1 else grid_count
            redistribute_sensors(
                input_folder, output_folder, grid_count, min_sensor_count,
                extension=extension.replace('.', '')
            )
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
@click.option(
    '--dist-info', '-di',
    help='An optional input for distribution information to put the grids back together '
    '. Alternatively, the command will look for a _redist_info.json file inside the '
    'folder.', type=click.Path(file_okay=True, dir_okay=False, resolve_path=True)
)
def merge_grid_folder(input_folder, output_folder, extension, dist_info):
    """Restructure files in a distributed folder.

    \b
    Args:
        input_folder: Path to input folder.
        output_folder: Path to the new restructured folder
        extension: Extension of the files to collect data from. It will be ``pts`` for
            sensor files. Another common extension is ``ill`` for the results of daylight
            studies.
    """
    try:
        # handle optional case for Functions input
        if dist_info and not os.path.isfile(dist_info):
            dist_info = None
        restore_original_distribution(input_folder, output_folder, extension, dist_info)
    except Exception:
        _logger.exception('Failed to restructure data from folder.')
        sys.exit(1)
    else:
        sys.exit(0)


@grid.command('mirror')
@click.argument('grid-file', type=click.Path(
    exists=True, file_okay=True, dir_okay=False, resolve_path=True))
@click.option(
    '--vector', '-v', default=None, help='An optional list of three values '
    '(separated by spaces) to standardize the direction of all rays in the output '
    'files. For example, inputting "0 0 1" will ensure that the output sensor files '
    'all have vectors pointing up in the base file and down in the mirrored file. If '
    'unspecified, the direction of sensors in the input file will be used.'
)
@click.option(
    '--name', '-n', default='grid', help='File name, which will be incorporated into '
    'both the base grid and the mirrored grid.'
)
@click.option(
    '--suffix', '-s', default='ref', show_default=True,
    help='Text for the suffix to be applied to the mirrored grid file.',
)
@click.option(
    '--folder', '-f', default='.', help='Output folder into which the base grid '
    'and mirrored grid files will be written.'
)
@click.option(
    '--log-file', '-log', help='Optional log file to output the list of generated '
    'radiant enclosure JSONs. By default this will be printed to stdout.',
    type=click.File('w'), default='-'
)
def mirror_grid(grid_file, vector, name, suffix, folder, log_file):
    """Mirror a honeybee Model's SensorGrids and format them for thermal mapping.

    This involves setting the direction of every sensor to point up (0, 0, 1) and
    then adding a mirrored sensor grid with the same sensor positions that all
    point downward. In thermal mapping workflows, the upward-pointing grids can
    be used to account for direct and diffuse shortwave irradiance while the
    downward pointing grids account for ground-reflected shortwave irradiance.

    \b
    Args:
        model_json: Full path to a Model JSON file.
    """
    try:
        # create the directory if it's not there and set up output paths
        if not os.path.isdir(folder):
            preparedir(folder)
        base_file = os.path.join(folder, '{}.pts'.format(name))
        rev_file = os.path.join(folder, '{}_{}.pts'.format(name, suffix))

        # loop through the lines of the grid_file and mirror the sensors
        if vector is not None and vector != '':
            # process the vector if it exists
            vec = [float(v) for v in vector.split()]
            assert len(vec) == 3, \
                'Vector "{}" must have 3 values. Got {}.'.format(vector, len(vec))
            vec_str = ' {} {} {}\n'.format(*vec)
            rev_vec = [-v for v in vec]
            rev_vec_str = ' {} {} {}\n'.format(*rev_vec)
            # get the lines from the grid file
            with open(grid_file) as sg_file:
                with open(base_file, 'w') as b_file, open(rev_file, 'w') as r_file:
                    for line in sg_file:
                        origin_str = ' '.join(line.split()[:3])
                        b_file.write(origin_str + vec_str)
                        r_file.write(origin_str + rev_vec_str)
        else:
            # loop through each sensor and reverse the vector
            with open(grid_file) as sg_file:
                with open(rev_file, 'w') as r_file:
                    for line in sg_file:
                        ray_vals = line.strip().split()
                        origin_str = ' '.join(ray_vals[:3])
                        vec_vals = (-float(v) for v in ray_vals[3:])
                        rev_vec_str = ' {} {} {}\n'.format(*vec_vals)
                        r_file.write(origin_str + rev_vec_str)
            # copy the input grid file to the base file location
            shutil.copyfile(grid_file, base_file)

        # write the resulting file paths to the log file
        log_file.write(json.dumps([base_file, rev_file], indent=4))
    except Exception as e:
        _logger.exception('Sensor grid mirroring failed.\n{}'.format(e))
        sys.exit(1)
    else:
        sys.exit(0)


@grid.command('from-rooms')
@click.argument('model-file', type=click.Path(
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
              default=True, show_default=True)
@click.option('--keep-out/--remove-out', ' /-out', help='Flag to note whether an extra '
              'check should be run to remove sensor points that lie outside the Room '
              'volume. Note that this can add significantly to the runtime and this '
              'check is not necessary in the case that all walls are vertical '
              'and all floors are horizontal.', default=True, show_default=True)
@click.option('--wall-offset', '-w', help='A number for the distance at which sensors '
              'close to walls should be removed. This can include the units of the '
              'distance (eg. 3ft) or, if no units are provided, the value will be '
              'interpreted in the honeybee model units. Note that this option has '
              'no effect unless the value is more than half of the grid-size.',
              type=str, default='0m', show_default=True)
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
def from_rooms(model_file, grid_size, offset, include_mesh, keep_out, wall_offset,
               room, write_json, folder, output_file):
    """Generate SensorGrids from the Room floors of a honeybee model.

    \b
    Args:
        model_file: Full path to a HBJSON or HBPkl Model file.
    """
    try:
        # re-serialize the Model and extract rooms and units
        model = Model.from_file(model_file)
        rooms = model.rooms if room is None or len(room) == 0 else \
            [r for r in model.rooms if r.identifier in room]
        grid_size = parse_distance_string(grid_size, model.units)
        offset = parse_distance_string(offset, model.units)
        wall_offset = parse_distance_string(wall_offset, model.units)

        # loop through the rooms and generate sensor grids
        sensor_grids = []
        remove_out = not keep_out
        for room in rooms:
            sg = room.properties.radiance.generate_sensor_grid(
                grid_size, offset=offset, remove_out=remove_out, wall_offset=wall_offset)
            if sg is not None:
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
        _logger.exception('Grid generation failed.\n{}'.format(e))
        sys.exit(1)
    else:
        sys.exit(0)


@grid.command('from-rooms-radial')
@click.argument('model-file', type=click.Path(
    exists=True, file_okay=True, dir_okay=False, resolve_path=True))
@click.option('--grid-size', '-s', help='A number for the dimension of the '
              'radial grid. This can include the units of the distance (eg. 1ft) '
              'or, if no units are provided, the value will be interpreted in the '
              'honeybee model units.', type=str, default='0.5m', show_default=True)
@click.option('--offset', '-o', help='A number for the distance at which the '
              'the sensor grid should be offset from the floor. This can include the '
              'units of the distance (eg. 3ft) or, if no units are provided, the '
              'value will be interpreted in the honeybee model units.',
              type=str, default='1.2m', show_default=True)
@click.option('--include-mesh/--exclude-mesh', ' /-xm', help='Flag to note whether to '
              'include a Mesh3D object that aligns with the grid positions under the '
              '"mesh" property of each grid. Excluding the mesh can reduce size but '
              'will mean Radiance results cannot be visualized as colored meshes.',
              default=True, show_default=True)
@click.option('--keep-out/--remove-out', ' /-out', help='Flag to note whether an extra '
              'check should be run to remove sensor points that lie outside the Room '
              'volume. Note that this can add significantly to the runtime and this '
              'check is not necessary in the case that all walls are vertical '
              'and all floors are horizontal.', default=True, show_default=True)
@click.option('--wall-offset', '-w', help='A number for the distance at which sensors '
              'close to walls should be removed. This can include the units of the '
              'distance (eg. 3ft) or, if no units are provided, the value will be '
              'interpreted in the honeybee model units. Note that this option has '
              'no effect unless the value is more than half of the grid-size.',
              type=str, default='0m', show_default=True)
@click.option('--dir-count', '-d', help='A positive integer for the number of '
              'radial directions to be generated around each position.',
              type=click.INT, default=8, show_default=True)
@click.option('--start-vector', '-v', help='An optional list of three values '
              '(separated by spaces) set the start direction of the generated '
              'directions. This can be used to orient the resulting sensors to '
              'specific parts of the scene. It can also change the elevation of the '
              'resulting directions since this start vector will always be rotated in '
              'the XY plane to generate the resulting directions.',
              type=str, default='0 -1 0', show_default=True)
@click.option('--mesh-radius', '-m', help='An optional number to override the radius '
              'of the meshes generated around each sensor. If unspecified, it will be '
              'equal to 45 percent of the grid-size. Set to zero to ensure no mesh is '
              'added to the resulting sensor grids.', type=float, default=None)
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
def from_rooms_radial(
        model_file, grid_size, offset, include_mesh, keep_out, wall_offset,
        dir_count, start_vector, mesh_radius, room, write_json, folder, output_file):
    """Generate SensorGrids of radial directions around positions from room floors.

    \b
    Args:
        model_file: Full path to a HBJSON or HBPkl Model file.
    """
    try:
        # re-serialize the Model and extract rooms and units
        model = Model.from_file(model_file)
        rooms = model.rooms if room is None or len(room) == 0 else \
            [r for r in model.rooms if r.identifier in room]
        grid_size = parse_distance_string(grid_size, model.units)
        offset = parse_distance_string(offset, model.units)
        wall_offset = parse_distance_string(wall_offset, model.units)
        vec = [float(v) for v in start_vector.split()]
        st_vec = Vector3D(*vec)

        # loop through the rooms and generate sensor grids
        sensor_grids = []
        remove_out = not keep_out
        for room in rooms:
            sg = room.properties.radiance.generate_sensor_grid_radial(
                grid_size, offset=offset, remove_out=remove_out, wall_offset=wall_offset,
                dir_count=dir_count, start_vector=st_vec, mesh_radius=mesh_radius)
            if sg is not None:
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
        _logger.exception('Grid generation failed.\n{}'.format(e))
        sys.exit(1)
    else:
        sys.exit(0)


@grid.command('from-exterior-faces')
@click.argument('model-file', type=click.Path(
    exists=True, file_okay=True, dir_okay=False, resolve_path=True))
@click.option('--grid-size', '-s', help='A number for the dimension of the mesh grid '
              'cells. This can include the units of the distance (eg. 1ft) '
              'or, if no units are provided, the value will be interpreted in the '
              'honeybee model units.', type=str, default='0.5m', show_default=True)
@click.option('--offset', '-o', help='A number for the distance at which the '
              'the sensor grid should be offset from the faces. This can include the '
              'units of the distance (eg. 3ft) or, if no units are provided, the '
              'value will be interpreted in the honeybee model units.',
              type=str, default='0.1m', show_default=True)
@click.option('--face-type', '-t', help='Text to specify the type of face that will be '
              'used to generate grids. Note that only Faces with Outdoors boundary '
              'conditions will be used, meaning that most Floors will typically '
              'be excluded unless they represent the underside of a cantilever. '
              'Choose from Wall, Roof, Floor, All.',
              type=str, default='Wall', show_default=True)
@click.option('--full-geometry/--punched-geometry', ' /-p', help='Flag to note whether '
              'the punched_geometry of the faces should be used with the areas '
              'of sub-faces removed from the grid or the full geometry should be used.',
              default=True)
@click.option('--include-mesh/--exclude-mesh', ' /-xm', help='Flag to note whether to '
              'include a Mesh3D object that aligns with the grid positions under the '
              '"mesh" property of each grid. Excluding the mesh can reduce size but '
              'will mean Radiance results cannot be visualized as colored meshes.',
              default=True, show_default=True)
@click.option('--room', '-r', multiple=True, help='Room identifier to specify the '
              'room for which sensor grids should be generated. You can pass multiple '
              'rooms (each preceded by -r). By default, all rooms get sensor grids '
              'joined into a single grid.')
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
def from_exterior_faces(
        model_file, grid_size, offset, face_type, full_geometry, include_mesh,
        room, write_json, folder, output_file):
    """Generate SensorGrids from the exterior Faces of a honeybee model.

    \b
    Args:
        model_file: Full path to a HBJSON or HBPkl Model file.
    """
    try:
        # re-serialize the Model and extract rooms and units
        model = Model.from_file(model_file)
        rooms = None if room is None or len(room) == 0 else \
            [r for r in model.rooms if r.identifier in room]
        grid_size = parse_distance_string(grid_size, model.units)
        offset = parse_distance_string(offset, model.units)
        punched_geometry = not full_geometry

        # loop through the rooms and generate sensor grids
        sensor_grids = []
        if rooms is None:
            sg = model.properties.radiance.generate_exterior_face_sensor_grid(
                grid_size, offset=offset, face_type=face_type,
                punched_geometry=punched_geometry)
            sensor_grids.append(sg)
        else:
            for room in rooms:
                sg = room.properties.radiance.generate_exterior_face_sensor_grid(
                    grid_size, offset=offset, face_type=face_type,
                    punched_geometry=punched_geometry)
                if sg is not None:
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
        _logger.exception('Grid generation failed.\n{}'.format(e))
        sys.exit(1)
    else:
        sys.exit(0)


@grid.command('from-exterior-apertures')
@click.argument('model-file', type=click.Path(
    exists=True, file_okay=True, dir_okay=False, resolve_path=True))
@click.option('--grid-size', '-s', help='A number for the dimension of the mesh grid '
              'cells. This can include the units of the distance (eg. 1ft) '
              'or, if no units are provided, the value will be interpreted in the '
              'honeybee model units.', type=str, default='0.5m', show_default=True)
@click.option('--offset', '-o', help='A number for the distance at which the '
              'the sensor grid should be offset from the apertures. This can include the'
              ' units of the distance (eg. 3ft) or, if no units are provided, the '
              'value will be interpreted in the honeybee model units.',
              type=str, default='0.1m', show_default=True)
@click.option('--aperture-type', '-t', help='Text to specify the type of aperture that '
              'will be used to generate grids. Note that only Faces with Outdoors '
              'boundary conditions will be used, meaning that most Floors will typically'
              ' be excluded unless they represent the underside of a cantilever. '
              'Choose from Window, Skylight, All.',
              type=str, default='All', show_default=True)
@click.option('--include-mesh/--exclude-mesh', ' /-xm', help='Flag to note whether to '
              'include a Mesh3D object that aligns with the grid positions under the '
              '"mesh" property of each grid. Excluding the mesh can reduce size but '
              'will mean Radiance results cannot be visualized as colored meshes.',
              default=True, show_default=True)
@click.option('--room', '-r', multiple=True, help='Room identifier to specify the '
              'room for which sensor grids should be generated. You can pass multiple '
              'rooms (each preceded by -r). By default, all rooms get sensor grids '
              'joined into a single grid.')
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
def from_exterior_apertures(
        model_file, grid_size, offset, aperture_type, include_mesh,
        room, write_json, folder, output_file):
    """Generate SensorGrids from the exterior Faces of a honeybee model.

    \b
    Args:
        model_file: Full path to a HBJSON or HBPkl Model file.
    """
    try:
        # re-serialize the Model and extract rooms and units
        model = Model.from_file(model_file)
        rooms = None if room is None or len(room) == 0 else \
            [r for r in model.rooms if r.identifier in room]
        grid_size = parse_distance_string(grid_size, model.units)
        offset = parse_distance_string(offset, model.units)

        # loop through the rooms and generate sensor grids
        sensor_grids = []
        if rooms is None:
            sg = model.properties.radiance.generate_exterior_aperture_sensor_grid(
                grid_size, offset=offset, aperture_type=aperture_type)
            sensor_grids.append(sg)
        else:
            for room in rooms:
                sg = room.properties.radiance.generate_exterior_aperture_sensor_grid(
                    grid_size, offset=offset, aperture_type=aperture_type)
                if sg is not None:
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
        _logger.exception('Grid generation failed.\n{}'.format(e))
        sys.exit(1)
    else:
        sys.exit(0)


@grid.command('from-face3ds')
@click.argument('face3d-file', type=click.Path(
    exists=True, file_okay=True, dir_okay=False, resolve_path=True))
@click.option('--grid-name', '-n', help='Text string for the name of the SensorGrid, '
              'which will also be used to assign SensorGrid ID. This will be used to '
              'identify the object across a model and in the exported Radiance files '
              'so it is recommended that it be relatively unique. If unspecified, '
              'a random name will be generated.', type=str, default=None)
@click.option('--grid-size', '-s', help='A number for the dimension of the mesh grid '
              'cells. This can include the units of the distance (eg. 1ft) '
              'or, if no units are provided, the value will be interpreted in the '
              '--units.', type=str, default='0.5m', show_default=True)
@click.option('--offset', '-o', help='A number for the distance at which the the sensor '
              'grid should be offset from the base geometry. This can include the'
              ' units of the distance (eg. 3ft) or, if no units are provided, the '
              'value will be interpreted in the --units.',
              type=str, default='0', show_default=True)
@click.option('--units', '-u', help=' Text for the units system in which the Face3D '
              'geometry exists, which will be used to interpret the --grid-size and '
              '--offset inputs. Must be (Meters, Millimeters, Feet, Inches, '
              'Centimeters).', type=str, default='Meters', show_default=True)
@click.option('--no-flip/--flip', ' /-fl', help='Flag to note whether the mesh '
              'normals should be reversed from the direction of the face geometries'
              'and the --offset move the sensors in the opposite direction from the '
              'face normals.', default=True, show_default=True)
@click.option('--include-mesh/--exclude-mesh', ' /-xm', help='Flag to note whether to '
              'include a Mesh3D object that aligns with the grid positions under the '
              '"mesh" property of each grid. Excluding the mesh can reduce size but '
              'will mean Radiance results cannot be visualized as colored meshes.',
              default=True, show_default=True)
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
def from_face3ds(
        face3d_file, grid_name, grid_size, offset, units, no_flip,
        include_mesh, write_json, folder, output_file):
    """Generate a SensorGrid from a JSON array of Face3D objects.

    \b
    Args:
        face3d_file: Full path to a JSON file containing an array of Face3D objects
            that will be used to generate the sensor grid. This could also be a
            nested array (list of lists of Face3Ds), in which case a separate
            SensorGrid will be computed for each sub-list.
    """
    try:
        # re-serialize the Face3Ds
        with open(face3d_file) as inf:
            data = json.load(inf)
        face_arrays = []
        for obj in data:
            if isinstance(obj, list):
                face_arrays.append([Face3D.from_dict(f) for f in obj])
            else:  # assume that it is a single Face3D
                face_arrays.append([Face3D.from_dict(obj)])

        # process all of the other inputs
        grid_size = parse_distance_string(grid_size, units)
        offset = parse_distance_string(offset, units)
        base_id = clean_rad_string(grid_name) if grid_name is not None \
            else clean_and_id_rad_string('SensorGrid')
        flip = not no_flip

        # loop through the face3ds and generate sensor grids
        sensor_grids = []
        for i, faces in enumerate(face_arrays):
            grid_id = base_id if len(face_arrays) == 1 else '{}_{}'.format(base_id, i)
            try:
                sensor_grids.append(
                    SensorGrid.from_face3d(grid_id, faces, grid_size, None, offset, flip)
                )
            except AssertionError:  # none of the Face3Ds make a valid grid
                continue
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
        _logger.exception('Grid generation failed.\n{}'.format(e))
        sys.exit(1)
    else:
        sys.exit(0)


@grid.command('enclosure-info')
@click.argument('model-file', type=click.Path(
    exists=True, file_okay=True, dir_okay=False, resolve_path=True))
@click.argument('grid-file', type=click.Path(
    exists=True, file_okay=True, dir_okay=False, resolve_path=True))
@click.option(
    '--air-boundary-distance', '-d', help='A number to set the distance from air '
    'boundaries over which values should be interpolated. Using 0 will assume a '
    'hard edge between Rooms of the same radiant enclosures. This can include the '
    'units of the distance (eg. 3ft) or, if no units are provided the value will '
    'be interpreted in the honeybee model units.',
    type=str, default='2m', show_default=True)
@click.option(
    '--output-file', '-f', help='Optional output file for the generated radiant '
    'enclosure JSON. By default this will be printed to stdout',
    type=click.File('w'), default='-'
)
def enclosure_info_grid(model_file, grid_file, air_boundary_distance, output_file):
    """Get a JSON of radiant enclosure information from a .pts file of a sensor grid.

    \b
    Args:
        model_file: Full path to a Model JSON file (HBJSON) or a Model pkl (HBpkl) file.
        grid-file: Full path to a sensor grid file (.pts).
    """
    try:
        # re-serialize the Model
        model = Model.from_file(model_file)
        grid = SensorGrid.from_file(grid_file)
        ab_distance = parse_distance_string(air_boundary_distance, model.units)
        # write out the list of radiant enclosure JSON info
        output_file.write(json.dumps(grid.enclosure_info_dict(model, ab_distance)))
    except Exception as e:
        _logger.exception('Creation of radiant enclosure info failed.\n{}'.format(e))
        sys.exit(1)
    else:
        sys.exit(0)
