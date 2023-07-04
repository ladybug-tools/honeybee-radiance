"""honeybee radiance model-editing commands."""
import click
import sys
import logging
import json

from ladybug_geometry.geometry3d import Vector3D, Face3D
from honeybee.model import Model
from honeybee.units import parse_distance_string
from honeybee.typing import clean_rad_string, clean_and_id_rad_string

from honeybee_radiance.sensorgrid import SensorGrid
from honeybee_radiance.properties.model import ModelRadianceProperties

_logger = logging.getLogger(__name__)


@click.group(help='Commands for editing radiance properties of Honeybee Models.')
def edit():
    pass


@edit.command('reset-resource-ids')
@click.argument('model-file', type=click.Path(
    exists=True, file_okay=True, dir_okay=False, resolve_path=True))
@click.option(
    '--by-name/--by-name-and-uuid', ' /-uuid', help='Flag to note whether '
    'newly-generated resource object IDs should be derived only from a '
    'cleaned display_name or whether this new ID should also have a unique '
    'set of 8 characters appended to it to guarantee uniqueness.', default=True
)
@click.option(
    '--reset-modifiers/--keep-modifiers', ' /-m', help='Flag to note whether '
    'the IDs of all modifiers in the model should be reset.',
    default=True, show_default=True
)
@click.option(
    '--reset-modifier-sets/--keep-modifier-sets', ' /-ms', help='Flag to '
    'note whether the IDs of all modifier sets in the model should be reset.',
    default=True, show_default=True
)
@click.option(
    '--output-file', '-f', help='Optional hbjson file to output the JSON '
    'string of the converted model. By default this will be printed out to '
    'stdout', type=click.File('w'), default='-', show_default=True
)
def reset_resource_ids(
    model_file, by_name, reset_modifiers, reset_modifier_sets, output_file
):
    """Reset the identifiers of resource objects in a Model file.

    This is useful when human-readable names are needed when the model is
    exported to other formats like RAD and the uniqueness of the
    identifiers is less of a concern.

    \b
    Args:
        model_file: Full path to a Honeybee Model (HBJSON) file.
    """
    try:
        # load the model file and separately load up the resource objects
        if sys.version_info < (3, 0):
            with open(model_file) as inf:
                data = json.load(inf)
        else:
            with open(model_file, encoding='utf-8') as inf:
                data = json.load(inf)
        # reset the identifiers of resources in the dictionary
        add_uuid = not by_name
        model_dict = ModelRadianceProperties.reset_resource_ids_in_dict(
            data, add_uuid, reset_modifiers, reset_modifier_sets)
        # write the dictionary into a JSON
        output_file.write(json.dumps(model_dict))
    except Exception as e:
        _logger.exception('Resetting resource identifiers failed.\n{}'.format(e))
        sys.exit(1)
    else:
        sys.exit(0)


@edit.command('add-room-sensors')
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
              'include a Mesh3D object that aligns with the grid positions '
              'under the "mesh" property of each grid. Excluding the mesh can greatly '
              'reduce model size but will mean Radiance results cannot be visualized '
              'as colored meshes.', default=True)
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
@click.option('--room', '-r', multiple=True, help='Room identifier(s) to specify the '
              'room(s) for which sensor grids should be generated. By default, all '
              'rooms will get sensor grids.')
@click.option('--output-file', '-f', help='Optional hbjson file to output the JSON '
              'string of the new model. By default this will be printed out '
              'to stdout', type=click.File('w'), default='-', show_default=True)
def add_room_sensors(model_file, grid_size, offset, include_mesh, keep_out, wall_offset,
                     room, output_file):
    """Add SensorGrids to a honeybee model generated from the Room's floors.

    The grids will have the rooms referenced in their room_identifier property.

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
        model.properties.radiance.add_sensor_grids(sensor_grids)

        # write the Model JSON string
        output_file.write(json.dumps(model.to_dict()))
    except Exception as e:
        _logger.exception('Adding Model sensor grids failed.\n{}'.format(e))
        sys.exit(1)
    else:
        sys.exit(0)


@edit.command('add-room-radial-sensors')
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
              'include a Mesh3D object that aligns with the grid positions '
              'under the "mesh" property of each grid. Excluding the mesh can greatly '
              'reduce model size but will mean Radiance results cannot be visualized '
              'as colored meshes.', default=True)
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
@click.option('--room', '-r', multiple=True, help='Room identifier(s) to specify the '
              'room(s) for which sensor grids should be generated. By default, all '
              'rooms will get sensor grids.')
@click.option('--output-file', '-f', help='Optional hbjson file to output the JSON '
              'string of the new model. By default this will be printed out '
              'to stdout', type=click.File('w'), default='-', show_default=True)
def add_room_radial_sensors(
        model_file, grid_size, offset, include_mesh, keep_out, wall_offset,
        dir_count, start_vector, mesh_radius, room, output_file):
    """Add SensorGrids to a honeybee model generated from the Room's floors.

    The grids will have the rooms referenced in their room_identifier property.

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
        model.properties.radiance.add_sensor_grids(sensor_grids)

        # write the Model JSON string
        output_file.write(json.dumps(model.to_dict()))
    except Exception as e:
        _logger.exception('Adding Model sensor grids failed.\n{}'.format(e))
        sys.exit(1)
    else:
        sys.exit(0)


@edit.command('add-face-sensors')
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
              'include a Mesh3D object that aligns with the grid positions '
              'under the "mesh" property of each grid. Excluding the mesh can greatly '
              'reduce model size but will mean Radiance results cannot be visualized '
              'as colored meshes.', default=True)
@click.option('--room', '-r', multiple=True, help='Room identifier(s) to specify the '
              'room(s) for which sensor grids should be generated. By default, all '
              'rooms will get sensor grids.')
@click.option('--output-file', '-f', help='Optional hbjson file to output the JSON '
              'string of the new model. By default this will be printed out '
              'to stdout', type=click.File('w'), default='-', show_default=True)
def add_face_sensors(model_file, grid_size, offset, face_type, full_geometry,
                     include_mesh, room, output_file):
    """Add SensorGrids to a honeybee model generated from the model's faces.

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
        model.properties.radiance.add_sensor_grids(sensor_grids)

        # write the Model JSON string
        output_file.write(json.dumps(model.to_dict()))
    except Exception as e:
        _logger.exception('Adding Model sensor grids failed.\n{}'.format(e))
        sys.exit(1)
    else:
        sys.exit(0)


@edit.command('add-aperture-sensors')
@click.argument('model-file', type=click.Path(
    exists=True, file_okay=True, dir_okay=False, resolve_path=True))
@click.option('--grid-size', '-s', help='A number for the dimension of the mesh grid '
              'cells. This can include the units of the distance (eg. 1ft) '
              'or, if no units are provided, the value will be interpreted in the '
              'honeybee model units.', type=str, default='0.5m', show_default=True)
@click.option('--offset', '-o', help='A number for the distance at which the '
              'the sensor grid should be offset from the apertures. This can include the '
              'units of the distance (eg. 3ft) or, if no units are provided, the '
              'value will be interpreted in the honeybee model units.',
              type=str, default='0.1m', show_default=True)
@click.option('--aperture-type', '-t', help='Text to specify the type of aperture that '
              'will be used to generate grids. Note that only Faces with Outdoors '
              'boundary conditions will be used, meaning that most Floors will typically'
              ' be excluded unless they represent the underside of a cantilever. '
              'Choose from Window, Skylight, All.',
              type=str, default='All', show_default=True)
@click.option('--include-mesh/--exclude-mesh', ' /-xm', help='Flag to note whether to '
              'include a Mesh3D object that aligns with the grid positions '
              'under the "mesh" property of each grid. Excluding the mesh can greatly '
              'reduce model size but will mean Radiance results cannot be visualized '
              'as colored meshes.', default=True)
@click.option('--room', '-r', multiple=True, help='Room identifier(s) to specify the '
              'room(s) for which sensor grids should be generated. By default, all '
              'rooms will get sensor grids.')
@click.option('--output-file', '-f', help='Optional hbjson file to output the JSON '
              'string of the new model. By default this will be printed out '
              'to stdout', type=click.File('w'), default='-', show_default=True)
def add_aperture_sensors(
        model_file, grid_size, offset, aperture_type, include_mesh, room, output_file):
    """Add SensorGrids to a honeybee model generated from the model's apertures.

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
        model.properties.radiance.add_sensor_grids(sensor_grids)

        # write the Model JSON string
        output_file.write(json.dumps(model.to_dict()))
    except Exception as e:
        _logger.exception('Adding Model sensor grids failed.\n{}'.format(e))
        sys.exit(1)
    else:
        sys.exit(0)


@edit.command('add-face3d-sensors')
@click.argument('model-file', type=click.Path(
    exists=True, file_okay=True, dir_okay=False, resolve_path=True))
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
              'honeybee model units.', type=str, default='0.5m', show_default=True)
@click.option('--offset', '-o', help='A number for the distance at which the the sensor '
              'grid should be offset from the base geometry. This can include the '
              'units of the distance (eg. 3ft) or, if no units are provided, the '
              'value will be interpreted in the honeybee model units.',
              type=str, default='0', show_default=True)
@click.option('--no-flip/--flip', ' /-fl', help='Flag to note whether the mesh '
              'normals should be reversed from the direction of the face geometries'
              'and the --offset move the sensors in the opposite direction from the '
              'face normals.', default=True, show_default=True)
@click.option('--include-mesh/--exclude-mesh', ' /-xm', help='Flag to note whether to '
              'include a Mesh3D object that aligns with the grid positions '
              'under the "mesh" property of each grid. Excluding the mesh can greatly '
              'reduce model size but will mean Radiance results cannot be visualized '
              'as colored meshes.', default=True)
@click.option('--output-file', '-f', help='Optional hbjson file to output the JSON '
              'string of the new model. By default this will be printed out '
              'to stdout', type=click.File('w'), default='-', show_default=True)
def add_face3d_sensors(
        model_file, face3d_file, grid_name, grid_size, offset, no_flip,
        include_mesh, output_file):
    """Add SensorGrids to a honeybee model generated from a JSON array of Face3D objects.

    \b
    Args:
        model_file: Full path to a HBJSON or HBPkl Model file.
        face3d_file: Full path to a JSON file containing an array of Face3D objects
            that will be used to generate the sensor grid. This could also be a
            nested array (list of lists of Face3Ds), in which case a separate
            SensorGrid will be computed for each sub-list.
    """
    try:
        # re-serialize the Model
        model = Model.from_file(model_file)
        
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
        grid_size = parse_distance_string(grid_size, model.units)
        offset = parse_distance_string(offset, model.units)
        base_id = clean_rad_string(grid_name) if grid_name is not None \
            else clean_and_id_rad_string('SensorGrid')
        flip = not no_flip

        # loop through the Face3Ds and generate sensor grids
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
        model.properties.radiance.add_sensor_grids(sensor_grids)

        # write the Model JSON string
        output_file.write(json.dumps(model.to_dict()))
    except Exception as e:
        _logger.exception('Adding Model sensor grids failed.\n{}'.format(e))
        sys.exit(1)
    else:
        sys.exit(0)


@edit.command('mirror-model-sensors')
@click.argument('model-file', type=click.Path(
    exists=True, file_okay=True, dir_okay=False, resolve_path=True))
@click.option('--output-file', '-f', help='Optional hbjson file to output the JSON '
              'string of the converted model. By default this will be printed out '
              'to stdout', type=click.File('w'), default='-', show_default=True)
def mirror_model_sensors(model_file, output_file):
    """Mirror a honeybee Model's SensorGrids and format them for thermal mapping.

    This involves setting the direction of every sensor to point up (0, 0, 1) and
    then adding a mirrored sensor grid with the same sensor positions that all
    point downward. In thermal mapping workflows, the upward-pointing grids can
    be used to account for direct and diffuse shortwave irradiance while the
    downward pointing grids account for ground-reflected shortwave irradiance.

    \b
    Args:
        model_file: Full path to a HBJSON or HBPkl Model file.
    """
    try:
        # re-serialize the Model and loop through the sensor grids to reformat them
        model = Model.from_file(model_file)
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
        _logger.exception('Model sensor grid mirroring failed.\n{}'.format(e))
        sys.exit(1)
    else:
        sys.exit(0)
