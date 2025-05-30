"""honeybee radiance ray-tracing command commands."""
import sys
import logging
import os
import traceback
import json
import math
from collections import OrderedDict
import click

from ladybug_geometry.geometry3d.mesh import Mesh3D
from honeybee.model import Model
from honeybee.aperture import Aperture
from honeybee.boundarycondition import Outdoors
from honeybee_radiance_folder import ModelFolder
from honeybee_radiance_folder.gridutil import redistribute_sensors
from honeybee_radiance_command.rfluxmtx import RfluxmtxOptions, Rfluxmtx

from honeybee_radiance.config import folders
from honeybee_radiance.reader import sensor_count_from_file
from honeybee_radiance.sensorgrid import SensorGrid
from honeybee_radiance.reader import parse_from_file
from honeybee_radiance.geometry.polygon import Polygon
from honeybee_radiance.dynamic.multiphase import automatic_aperture_grouping
from honeybee_radiance.dynamic import StateGeometry, RadianceSubFaceState
from honeybee_radiance.modifier.material.trans import Trans

from .octree import _generate_octrees_info
from .threephase import three_phase

_logger = logging.getLogger(__name__)


@click.group(help="Commands to run multi-phase operations in Radiance.")
def multi_phase():
    pass


multi_phase.add_command(three_phase)


@multi_phase.command("view-matrix")
@click.argument(
    "receiver-file", type=click.Path(exists=True, file_okay=True, resolve_path=True)
)
@click.argument(
    "octree", type=click.Path(exists=True, file_okay=True, resolve_path=True)
)
@click.argument(
    "sensor-grid", type=click.Path(exists=True, file_okay=True, resolve_path=True)
)
@click.option(
    "--sensor-count",
    type=click.INT,
    show_default=True,
    help="Number of sensors in sensor grid file. Number of sensors will be parsed form"
    " the sensor file if not provided.",
)
@click.option("--rad-params", show_default=True, help="Radiance parameters.")
@click.option(
    "--rad-params-locked",
    show_default=True,
    help="Protected Radiance parameters. "
    "These values will overwrite user input rad parameters.",
)
@click.option(
    "--output",
    "-o",
    show_default=True,
    help="Path to output file. If a relative path"
    " is provided it should be relative to project folder.",
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    show_default=True,
    help="A flag to show the command without running it.",
)
def view_matrix_command(
    receiver_file,
    octree,
    sensor_grid,
    sensor_count,
    rad_params,
    rad_params_locked,
    output,
    dry_run,
):
    """Calculate view matrix for a receiver file.

    \b
    Args:
        receiver_file: Path to receiver file.
        octree: Path to octree file.
        sensor_grid: Path to sensor grid file.
    """

    try:
        options = RfluxmtxOptions()
        # parse input radiance parameters
        if rad_params:
            options.update_from_string(rad_params.strip())
        # overwrite input values with protected ones
        if rad_params_locked:
            options.update_from_string(rad_params_locked.strip())

        if not sensor_count:
            sensor_count = sensor_count_from_file(sensor_grid)

        options.update_from_string('-aa 0.0 -y {}'.format(sensor_count))

        # create command.
        rfluxmtx_cmd = Rfluxmtx(
            options=options, output=output, octree=octree, sensors=sensor_grid,
            receivers=receiver_file
        )

        if dry_run:
            click.echo(rfluxmtx_cmd)
            sys.exit(0)

        if output:
            parent = os.path.dirname(output)
            if not os.path.isdir(parent):
                os.mkdir(parent)

        if options.o.value is not None:
            parent = os.path.dirname(options.o.value)
            if not os.path.isdir(parent):
                os.mkdir(parent)

        env = None
        if folders.env != {}:
            env = folders.env
        env = dict(os.environ, **env) if env else None
        rfluxmtx_cmd.run(env=env)

    except Exception:
        _logger.exception("Failed to run view-matrix command.")
        traceback.print_exc()
        sys.exit(1)
    else:
        sys.exit(0)


@multi_phase.command("flux-transfer")
@click.argument(
    "sender-file", type=click.Path(exists=True, file_okay=True, resolve_path=True)
)
@click.argument(
    "receiver-file", type=click.Path(exists=True, file_okay=True, resolve_path=True)
)
@click.argument(
    "octree", type=click.Path(exists=True, file_okay=True, resolve_path=True)
)
@click.option("--rad-params", show_default=True, help="Radiance parameters.")
@click.option(
    "--rad-params-locked",
    show_default=True,
    help="Protected Radiance parameters. "
    "These values will overwrite user input rad parameters.",
)
@click.option(
    "--output",
    "-o",
    show_default=True,
    help="Path to output file. If a relative path"
    " is provided it should be relative to project folder.",
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    show_default=True,
    help="A flag to show the command without running it.",
)
def flux_transfer_command(
    sender_file,
    receiver_file,
    octree,
    rad_params,
    rad_params_locked,
    output,
    dry_run,
):
    """Calculate flux transfer matrix for a sender file per receiver.

    This command calculates a flux transfer matrix for the given sender and receiver
    files. This can be used to calculate a flux transfer matrix for input and output
    apertures on a light pipe, or a flux transfer matrix from an aperture to a
    discretized sky (daylight matrix).

    \b
    Args:
        sender_file: Path to sender file. The controlling parameters in the sender file
            must follow the form: #@rfluxmtx variable=value. At minimum it must specify
            a hemisphere sampling type. If the command is used to calculate e.g. daylight
            matrix the sender file represents an aperture or multiple apertures.
        receiver_file: Path to receiver file. The controlling parameters in the receiver
            file must follow the form: #@rfluxmtx variable=value. At minimum it must
            specify a hemisphere sampling type. If the command is used to calculate e.g.
            daylight matrix the receiver file represents the ground and sky.
        octree: Path to octree file.
    """

    try:
        options = RfluxmtxOptions()
        # parse input radiance parameters
        if rad_params:
            options.update_from_string(rad_params.strip())
        # overwrite input values with protected ones
        if rad_params_locked:
            options.update_from_string(rad_params_locked.strip())

        options.update_from_string('-aa 0.0')

        # create command.
        rfluxmtx_cmd = Rfluxmtx(
            options=options, output=output, octree=octree, sender=sender_file,
            receivers=receiver_file
        )

        if dry_run:
            click.echo(rfluxmtx_cmd)
            sys.exit(0)

        env = None
        if folders.env != {}:
            env = folders.env
        env = dict(os.environ, **env) if env else None
        rfluxmtx_cmd.run(env=env)

    except Exception:
        _logger.exception("Failed to run flux-transfer command.")
        traceback.print_exc()
        sys.exit(1)
    else:
        sys.exit(0)


@multi_phase.command("dmtx-group")
@click.argument("folder", type=click.STRING)
@click.argument(
    "octree", type=click.Path(exists=True, file_okay=True, resolve_path=True)
)
@click.argument(
    "rflux_sky", type=click.Path(exists=True, file_okay=True, resolve_path=True)
)
@click.option(
    "--name", help="Name of output JSON file.", show_default=True,
    default='dmx_aperture_groups'
)
@click.option(
    "--size", "-s", type=float, default=0.2, show_default=True,
    help="Aperture grid size. A lower number will give a finer grid and more accurate"
    " results but the calculation time will increase.")
@click.option(
    "--threshold", "-t", type=float, default=0.001, show_default=True,
    help="A number that determines if two apertures/aperture groups can be clustered. A"
    " higher number is more accurate but will also increase the number of aperture groups.")
@click.option(
    "--ambient-division", "-ad", type=int, default=1000, show_default=True,
    help="Number of ambient divisions (-ad) for view factor calculation in rfluxmtx."
    " Increasing the number will give more accurate results but also increase the"
    " calculation time.")
@click.option(
    "--output-folder", help="Output folder into which the files be written.",
    default="dmtx_aperture_groups", show_default=True)
def dmtx_group_command(
    folder,
    octree,
    rflux_sky,
    name,
    size,
    threshold,
    ambient_division,
    output_folder,
):
    """Calculate aperture groups for daylight matrix purposes.
    This command calculates view factor from apertures to sky patches (rfluxmtx). Each
    aperture is represented by a sensor grid, and the view factor for the whole aperture
    is the average of the grid. The apertures are grouped based on the threshold.

    \b
    Args:
        folder: Path to a Radiance model folder.
        octree: Path to octree file.
        rflux_sky: Path to rflux sky file.
    """

    def _index_and_min(distance_matrix):
        """Return the minimum value of the distance matrix, as well as the index [j, i] of
        the minimum value of the distance matrix."""
        min_value = min([min(sublist) for sublist in distance_matrix])
        for i, _i in enumerate(distance_matrix):
            for j, _j in enumerate(distance_matrix):
                if distance_matrix[i][j] == min_value:
                    index = [j, i]
                    break
        return min_value, index

    def _pairwise_maximum(array1, array2):
        """Return an array of the pairwise maximum of two arrays."""
        pair_array = [array1, array2]
        max_array = list(map(max, zip(*pair_array)))
        return max_array

    def _tranpose_matrix(matrix):
        """Transposes the distance matrix."""
        matrix = list(map(list, zip(*matrix)))
        return matrix

    def _rmse_from_matrix(input):
        """Calculates RMSE."""
        rmse = []
        for i, predicted in enumerate(input):
            r_list = []
            for j, observed in enumerate(input):
                error = [(p - o) for p, o in zip(predicted, observed)]
                square_error = [e ** 2 for e in error]
                mean_square_error = sum(square_error) / len(square_error)
                root_mean_square_error = mean_square_error ** 0.5
                r_list.append(root_mean_square_error)
            rmse.append(r_list)
        return rmse

    def _flatten(container):
        """Flatten an array."""
        if not isinstance(container, list):
            container = [container]
        for i in container:
            if isinstance(i, (list, tuple)):
                for j in _flatten(i):
                    yield j
            else:
                yield i

    def _agglomerative_clustering_complete(distance_matrix, ap_name, threshold=0.001):
        """Cluster apertures based on the threshold."""

        # Fill the diagonal with 9999 so a diagonal of zeros will NOT be stored as min_value.
        for i in range(len(distance_matrix)):
            distance_matrix[i][i] = 9999

        # Create starting list of aperture groups. Each aperture starts as its own group.
        ap_groups = ap_name

        # Set the number of samples and the minimum value of the distance matrix.
        n_samples = len(distance_matrix)

        # Set the minimum value of the distance matrix and find the indices of the minimum
        # value in the distance matrix.
        min_value, index = _index_and_min(distance_matrix)

        while n_samples > 1 and min_value < threshold:
            # Combine the two groups and place it at index 0, and remove item at index 1.
            ap_groups[index[0]] = [ap_groups[index[0]], ap_groups[index[1]]]
            ap_groups.pop(index[1])

            # Update the values in the distance matrix. We need the maximum values between
            # the new cluster and all the remaining apertures or clusters still in the
            # distance matrix.
            distance_matrix[index[0]] = \
                _pairwise_maximum(distance_matrix[index[0]], distance_matrix[index[1]])
            distance_matrix = _tranpose_matrix(distance_matrix)
            distance_matrix[index[0]] = \
                _pairwise_maximum(distance_matrix[index[0]], distance_matrix[index[1]])

            # Remove the values at index 1 along both axes.
            distance_matrix.pop(index[1])
            distance_matrix = _tranpose_matrix(distance_matrix)
            distance_matrix.pop(index[1])

            # Update the number of samples that are left in the distance matrix.
            n_samples -= 1
            # Update the minimum value and the indices.
            min_value, index = _index_and_min(distance_matrix)

        return ap_groups

    def _aperture_view_factor(
            project_folder, apertures, size=0.2, ambient_division=1000,
            receiver='rflux_sky.sky', octree='scene.oct',
            calc_folder='dmtx_aperture_grouping'):
        """Calculates the view factor for each aperture by sensor points."""

        # Instantiate dictionary that will store the sensor count for each aperture. We need
        # a OrderedDict so that we can split the rfluxmtx output file by each aperture
        # (sensor count) in the correct order.
        ap_dict = OrderedDict()

        meshes = []
        # Create a mesh for each aperture and add the the sensor count to dict.
        for aperture in apertures:
            ap_mesh = aperture.geometry.mesh_grid(size, flip=True, generate_centroids=False)
            meshes.append(ap_mesh)
            ap_dict[aperture.display_name] = {'sensor_count': len(ap_mesh.faces)}

        # Create a sensor grid from joined aperture mesh.
        grid_mesh = SensorGrid.from_mesh3d('aperture_grid', Mesh3D.join_meshes(meshes))

        # Write sensor grid to pts file.
        sensors = grid_mesh.to_file(os.path.join(project_folder, calc_folder),
                                    file_name='apertures')

        # rfluxmtx options
        rfluxOpt = RfluxmtxOptions()
        rfluxOpt.ad = ambient_division
        rfluxOpt.lw = 1.0 / float(rfluxOpt.ad)
        rfluxOpt.I = True
        rfluxOpt.h = True

        # rfluxmtx command
        rflux = Rfluxmtx()
        rflux.options = rfluxOpt
        rflux.receivers = receiver
        rflux.sensors = sensors
        rflux.octree = octree
        rflux.output = os.path.join(calc_folder, 'apertures_vf.mtx')

        # Run rfluxmtx command
        env = None
        if folders.env != {}:
            env = folders.env
        env = dict(os.environ, **env) if env else None
        rflux.run(env=env, cwd=project_folder)

        # Get the output file of the rfluxmtx command.
        mtx_file = os.path.join(project_folder, rflux.output)

        return mtx_file, ap_dict

    try:
        model_folder = ModelFolder.from_model_folder(folder)

        apertures = []
        states = model_folder.aperture_groups_states(full=True)
        ap_group_folder = model_folder.aperture_group_folder(full=True)
        for ap_group in states.keys():
            if 'dmtx' in states[ap_group][0]:
                mtx_file = os.path.join(ap_group_folder,
                                        os.path.basename(states[ap_group][0]['dmtx']))
                polygon_string = parse_from_file(mtx_file)
                polygon = Polygon.from_string('\n'.join(polygon_string))
                apertures.append(Aperture.from_vertices(ap_group, polygon.vertices))

        assert len(apertures) != 0, \
            'Found no valid dynamic apertures. There should at least be one aperture ' \
            'with transmittance matrix in your model.'

        # Calculate view factor.
        mtx_file, ap_dict = _aperture_view_factor(
            model_folder.folder, apertures, size=size, ambient_division=ambient_division,
            receiver=rflux_sky, octree=octree, calc_folder=output_folder
        )

        view_factor = []
        # Read view factor file, convert to one channel output, and divide by Pi.
        with open(mtx_file) as mtx_data:
            for sensor in mtx_data:
                sensor_split = sensor.strip().split()
                if len(sensor_split) % 3 == 0:
                    one_channel = sensor_split[::3]

                    def convert_to_vf(x):
                        return float(x) / math.pi
                    view_factor.append(list(map(convert_to_vf, one_channel)))

        ap_view_factor = []
        # Split the view factor file by the aperture sensor count.
        for aperture in ap_dict.values():
            sensor_count = aperture['sensor_count']
            ap_vf, view_factor = view_factor[:sensor_count], view_factor[sensor_count:]
            ap_view_factor.append(ap_vf)

        ap_view_factor_mean = []
        # Get the mean view factor per sky patch for each aperture.
        for aperture in ap_view_factor:
            ap_t = _tranpose_matrix(aperture)
            ap_view_factor_mean.append(
                [sum(sky_patch) / len(sky_patch) for sky_patch in ap_t])

        # Calculate RMSE between all combinations of averaged aperture view factors.
        rmse = _rmse_from_matrix(ap_view_factor_mean)

        ap_name = list(ap_dict.keys())
        # Cluster the apertures by the 'complete method'.
        ap_groups = _agglomerative_clustering_complete(rmse, ap_name, threshold)

        # Flatten the groups. This will break the intercluster structure, but we do not need
        # to know that.
        ap_groups = [list(_flatten(cluster)) for cluster in ap_groups]

        # Add the aperture group to each aperture in the dictionary and write the aperture
        # group rad files.
        group_names = []
        groups_folder = os.path.join(
                model_folder.folder, output_folder, 'groups'
        )
        if not os.path.isdir(groups_folder):
            os.mkdir(groups_folder)
        for idx, group in enumerate(ap_groups):
            group_name = "group_{}".format(idx)
            group_file = os.path.join(groups_folder, group_name + '.rad')
            xform = []
            group_names.append(
                {'identifier': group_name, 'aperture_groups': group}
            )

            for ap in group:
                xform.append("!xform ./model/aperture_group/{}..mtx.rad".format(ap))

            with open(group_file, "w") as file:
                file.write('\n'.join(xform))

        # Write aperture dictionary to json file.
        output = os.path.join(
            model_folder.folder, output_folder, 'groups', '%s.json' % name
        )
        with open(output, 'w') as fp:
            json.dump(group_names, fp, indent=2)

    except Exception:
        _logger.exception("Failed to run dmtx-group command.")
        traceback.print_exc()
        sys.exit(1)
    else:
        sys.exit(0)


@multi_phase.command('prepare-multiphase')
@click.argument(
    'folder', type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.argument('grid-count', type=int)
@click.option(
    '--grid-divisor', '-d', help='An optional integer to be divided by the '
    'grid-count to yield a final number of grids to generate. This is useful '
    'in workflows where the grid-count is being interpreted as a cpu-count '
    'but there are multiple processors acting on a single grid. To ignore '
    'this limitation set the value to 1. Default: 1.', type=int, default=1)
@click.option(
    '--min-sensor-count', '-msc', help='Minimum number of sensors in each '
    'output grid. Use this number to ensure the number of sensors in output '
    'grids never gets very small. This input will override the input '
    'grid-count when specified. To ignore this limitation, set the value to '
    '1. Default: 1.', type=int, default=1)
@click.option(
    '--sun-path',
    type=click.Path(
        exists=True, file_okay=True, dir_okay=False, resolve_path=False),
    default=None, show_default=True,
    help='Path for a sun-path file that will be added to octrees for direct '
    'sunlight studies. If sunpath is provided an extra octree for direct_sun '
    'will be created.'
)
@click.option(
    '--phase',
    type=click.Choice(['2', '3', '5']), default='5', show_default=True,
    help='Select a multiphase study for which octrees will be created. 3-phase '
    'includes 2-phase, and 5-phase includes 3-phase and 2-phase.'
)
@click.option(
    '--octree-folder', default='octree', show_default=True,
    help='Output folder into which the octree files be written.')
@click.option(
    '--grid-folder', default='grid', show_default=True,
    help='Output folder into which the grid files be written.')
@click.option(
    '--exclude-static/--include-static',
    is_flag=True, default=True, show_default=True,
    help='A flag to indicate if static apertures should be excluded or '
    'included. If excluded static apertures will not be treated as its own '
    'dynamic state.'
)
@click.option(
    '--default-states/--all-states',
    is_flag=True, default=False, show_default=True,
    help='A flag to indicate if the command should generate octrees and grids '
    'for all aperture group states or just the default states of aperture '
    'groups.'
)
def prepare_multiphase_command(
    folder, grid_count, grid_divisor, min_sensor_count, sun_path, phase,
    octree_folder, grid_folder, exclude_static, default_states
):
    """This command prepares the model folder for simulations with aperture
    groups. It will generate a set of octrees and sensor grids that are unique
    to each state of each aperture group.

    This command will generate octrees for both default and direct studies for
    aperture groups, creating one octree for each light path, i.e., all other
    light paths are blacked.

    Sensor grids will be redistributed if they are to be used in a two phase
    simulation. A subfolder for each light path will be created. In this folder
    the redistributed grids are found.

    If the model folder have aperture groups, a file with states information
    for each grid will be written.

    \b
    Args:
        folder: Path to a Radiance model folder.
        grid_count: Number of output sensor grids to be created. This number
            is usually equivalent to the number of processes that will be used
            to run the simulations in parallel.
    """
    model_folder = ModelFolder.from_model_folder(folder)

    # check if sunpath file exist - otherwise continue without it
    if sun_path and not os.path.isfile(sun_path):
        sun_path = None

    phase = int(phase)
    if phase == 5 and not sun_path:
        raise RuntimeError(
            'To generate octrees for a 5 Phase study you must provide a '
            'sunpath.'
        )

    phases = {
        2: ['two_phase'],
        3: ['two_phase', 'three_phase'],
        5: ['two_phase', 'three_phase', 'five_phase']
    }

    def _get_grid_states(model_folder):
        states_info = model_folder.aperture_groups_states()
        grid_info = model_folder.grid_info()
        grid_states = {}

        for grid in grid_info:
            grid_states[grid['full_id']] = {}
            try:
                light_paths = grid['light_path']
            except KeyError:
                light_paths = []
            for light_path in light_paths:
                for elem in light_path:
                    if elem != '__static_apertures__':
                        grid_states[grid['full_id']][elem] = \
                            [s['identifier'] for s in states_info[elem]]

        grid_states_output = \
            os.path.join(model_folder.folder, 'grid_states.json')
        with open(grid_states_output, 'w') as fp:
            json.dump(grid_states, fp, indent=2)

    def _get_octrees_and_grids(
        model_folder, grid_count, phase, octree_folder, grid_folder,
        exclude_static, default_states
    ):
        scene_mapping = model_folder.octree_scene_mapping(
            exclude_static=exclude_static, phase=phase,
            default_states=default_states
            )
        grid_mapping = model_folder.grid_mapping(
            exclude_static=exclude_static, phase=phase
            )
        if not os.path.isdir(octree_folder):
            os.mkdir(octree_folder)
        dynamic_mapping = {
            'two_phase': [],
            'three_phase': [],
            'five_phase': []
        }
        for study, states in scene_mapping.items():
            if study == 'two_phase':
                grid_info_dict = {}

                if not os.path.isdir(grid_folder):
                    os.mkdir(grid_folder)

                grid_count = int(grid_count / grid_divisor)
                grid_count = 1 if grid_count < 1 else grid_count

                for light_path in grid_mapping['two_phase']:
                    grid_info = light_path['grid']
                    output_folder = \
                        os.path.join(grid_folder, light_path['identifier'])
                    _grid_count, _sensor_per_grid, out_grid_info = \
                        redistribute_sensors(model_folder.grid_folder(),
                                             output_folder, grid_count,
                                             min_sensor_count,
                                             grid_info=grid_info)
                    grid_info_dict[light_path['identifier']] = out_grid_info

            for state in states:
                light_path = state['light_path']
                if light_path not in grid_info_dict:
                    if state['identifier'] == '__three_phase__':
                        pass
                    else:
                        # in this case we do not want to generate an octree for
                        # this state
                        continue
                info, commands = _generate_octrees_info(
                    state, octree_folder, study, sun_path
                    )
                for cmd in commands:
                    env = None
                    if folders.env:
                        env = folders.env
                    env = dict(os.environ, **env) if env else None
                    cmd.run(env=env, cwd=model_folder.folder)

                # add grid information and folder if two_phase
                if study == 'two_phase':
                    info['sensor_grids_folder'] = light_path
                    info['sensor_grids_info'] = grid_info_dict[light_path]

                dynamic_mapping[study].append(info)

        for study, study_info in dynamic_mapping.items():
            dynamic_output = os.path.join(model_folder.folder, '%s.json' % study)
            with open(dynamic_output, 'w') as fp:
                json.dump(study_info, fp, indent=2)

        dynamic_output = os.path.join(model_folder.folder, 'multi_phase.json')
        with open(dynamic_output, 'w') as fp:
            json.dump(dynamic_mapping, fp, indent=2)

    try:
        if model_folder.has_aperture_group or not exclude_static:
            _get_octrees_and_grids(
                model_folder, grid_count, phase, octree_folder, grid_folder,
                exclude_static, default_states
            )
            _get_grid_states(model_folder=model_folder)
        else:
            # no aperture groups and static excluded, write empty files
            dynamic_mapping = []
            for study in phases[phase]:
                study_type = []
                dynamic_mapping.append({study: study_type})
                dynamic_output = os.path.join(model_folder.folder, '%s.json' % study)
                with open(dynamic_output, 'w') as fp:
                    json.dump(study_type, fp, indent=2)

            dynamic_output = \
                os.path.join(model_folder.folder, 'multi_phase.json')
            with open(dynamic_output, 'w') as fp:
                json.dump(dynamic_mapping, fp, indent=2)

    except Exception:
        _logger.exception('Failed to generate octrees and grids.')
        sys.exit(1)
    else:
        sys.exit(0)


@multi_phase.command('aperture-group')
@click.argument('model-file', type=click.Path(
    exists=True, file_okay=True, dir_okay=False, resolve_path=True))
@click.option(
    '--octree', type=click.Path(exists=True, file_okay=True, resolve_path=True),
    help='Path to octree file. The octree will be created from the model-file '
    'if no file is provided.', default=None
)
@click.option(
    '--rflux-sky', type=click.Path(exists=True, file_okay=True, resolve_path=True),
    help='Path to rflux sky file. The rflux sky file will be created if no file '
    'is provided.', default=None
)
@click.option(
    '--size', '-s', type=float, default=0.2, show_default=True,
    help='Aperture grid size. A lower number will give a finer grid and more accurate '
    'results but the calculation time will increase.')
@click.option(
    '--threshold', '-t', type=float, default=0.001, show_default=True,
    help='A number that determines if two apertures/aperture groups can be clustered. A '
    'lower number is more accurate but will also increase the number of aperture groups.')
@click.option(
    '--ambient-division', '-ad', type=int, default=1000, show_default=True,
    help='Number of ambient divisions (-ad) for view factor calculation in rfluxmtx. '
    'Increasing the number will give more accurate results but also increase the '
    'calculation time.')
@click.option(
    '--room-based/--no-room-based', '-rb/-nrb', help='Flag to note '
    'whether the apertures should be grouped on a room basis. If grouped on a room '
    'basis apertures from different room cannot be in the same group.',
    default=True, show_default=True)
@click.option(
    '--view-factor/--orientation', '-vf/-or', help='Flag to note '
    'whether the apertures should be grouped by calculating view factors for '
    'the apertures to a discretized sky or simply by the normal orientation of '
    'the apertures.',
    default=True, show_default=True)
@click.option(
    '--vertical-tolerance', '-vt', type=click.FLOAT, default=None,
    show_default=True, help='A float value for vertical tolerance between two '
    'apertures. If the vertical distance between two apertures is larger than '
    'this tolerance the apertures cannot be grouped. If no value is given the '
    'vertical grouping will be skipped.')
@click.option(
    '--output-folder', help='Output folder into which the files be written.',
    default='.', show_default=True,
    type=click.Path(file_okay=False, dir_okay=True, resolve_path=True))
@click.option(
    '--output-model', help='Optional file to output the string of the model '
    'with aperture groups assigned. By default, it will be printed out to stdout.',
    type=click.File('w'), default='-', show_default=True)
def aperture_group_cli(
    model_file, octree, rflux_sky, size, threshold, ambient_division,
    room_based, view_factor, vertical_tolerance, output_folder, output_model
):
    """Calculate aperture groups for exterior apertures.

    This command calculates view factor from apertures to sky patches (rfluxmtx). Each
    aperture is represented by a sensor grid, and the view factor for the whole aperture
    is the average of the grid. The apertures are grouped based on the threshold.

    \b
    Args:
        model_file: Full path to a Model JSON file (HBJSON) or a Model pkl (HBpkl) file.
    """
    try:
        # process all of the CLI input so that it can be passed to the function
        no_room_based = not room_based
        orientation = not view_factor

        # pass the input to the function
        aperture_group(model_file, octree, rflux_sky, size, threshold, ambient_division,
                       no_room_based, orientation, vertical_tolerance,
                       output_folder, output_model)
    except Exception:
        _logger.exception("Failed to run aperture-group command.")
        traceback.print_exc()
        sys.exit(1)
    else:
        sys.exit(0)


def aperture_group(
    model_file, octree=None, rflux_sky=None,
    size=0.2, threshold=0.001, ambient_division=1000,
    no_room_based=False, orientation=False, vertical_tolerance=None,
    output_folder=None, output_model=None,
    room_based=True, view_factor=True
):
    """Automatically calculate aperture groups for exterior apertures.

    This function calculates view factor from apertures to sky patches (rfluxmtx). Each
    aperture is represented by a sensor grid, and the view factor for the whole aperture
    is the average of the grid. The apertures are grouped based on the threshold.

    Args:
        model_file: Full path to a Model JSON file (HBJSON) or a Model pkl (HBpkl) file.
        octree: Path to octree file. The octree will be created from the model
            file if no file is provided.
        rflux_sky: Path to rflux sky file. The rflux sky file will be created
            if no file is provided.
        size: Aperture grid size. A lower number will give a finer grid and more
            accurate results but the calculation time will increase. (Default: 0.2).
        threshold: A number that determines if two apertures/aperture groups can
            be clustered. A lower number is more accurate but will also increase
            the number of aperture groups. (Default: 0.001).
        ambient_division: Number of ambient divisions (-ad) for view factor
            calculation in rfluxmtx. Increasing the number will give more accurate
            results but also increase the calculation time. (Default: 1000).
        no_room_based: Boolean to note whether the apertures should be grouped
            on a room basis. If grouped on a room basis apertures from different
            room cannot be in the same group. (Default: False).
        orientation: Boolean to note whether the apertures should be grouped by
            calculating view factors for the apertures to a discretized sky or
            simply by the normal orientation of the apertures. (Default: False).
        vertical_tolerance: A float value for vertical tolerance between two apertures.
            If the vertical distance between two apertures is larger than this
            tolerance the apertures cannot be grouped. If None, the vertical
            grouping will be skipped. (Default: None).
        output_folder: Output folder into which the files be written. If None,
            the files will be written into a folder called aperture_groups
            within the default simulation folder.
        output_model: Optional file to output the JSON string of the Model with
            aperture groups set. If None, the string will simply be returned from
            this method.
    """
    # serialize the model and process simpler attributes
    model = Model.from_file(model_file)
    room_based = not no_room_based
    view_factor = not orientation

    # perform the automatic aperture grouping
    model = automatic_aperture_grouping(
        model, octree, rflux_sky, size, threshold, ambient_division,
        room_based, view_factor, vertical_tolerance, working_folder=output_folder)

    # return the more with the dynamic groups
    if output_model is None:
        return json.dumps(model.to_dict())
    elif isinstance(output_model, str):
        with open(output_model, 'w') as of:
            of.write(json.dumps(model.to_dict()))
    else:
        output_model.write(json.dumps(model.to_dict()))


@multi_phase.command('add-aperture-group-blinds')
@click.argument('model-file', type=click.Path(
    exists=True, file_okay=True, dir_okay=False, resolve_path=True)
)
@click.option(
    '--diffuse-transmission', '-dt',
    help='Diffuse transmission of the aperture group blinds. Default is 0.05 '
    '(5%).',
    default=0.05, type=float, show_default=True
)
@click.option(
    '--specular-transmission', '-dt',
    help='Specular transmission of the aperture group blinds. Default is 0 '
    '(0%).',
    default=0, type=float, show_default=True
)
@click.option(
    '--distance', '-d',
    help='Distance from the aperture parent surface to the blind surface.',
    default=0.001, type=float, show_default=True
)
@click.option(
    '--scale', '-s',
    help='Scaling value to scale blind geometry at the center point of the '
    'aperture.',
    default=1.001, type=float, show_default=True
)
@click.option(
    '--create-groups', '-cg', default=False, show_default=True, is_flag=True,
    help='Flag to note whether aperture groups should be created if none exists.'
)
@click.option(
    '--output-model', help='Optional name of output HBJSON file as a '
    'string. If no name is provided the name will be the identifier of the '
    'model with "blinds" as suffix.',
    default=None, show_default=True, type=click.STRING
)
def add_aperture_group_blinds_command(
    model_file, diffuse_transmission, specular_transmission, distance, scale,
    create_groups, output_model
):
    """Add a state geometry to aperture groups.

    This command adds state geometry to all aperture groups in the model. The
    geometry is the same as the aperture geometry but the modifier is changed.
    The geometry is translated inward by a distance which by default is 0.001
    in model units.

    \b
    Args:
        model_file: Full path to a Model JSON file (HBJSON) or a Model pkl
            (HBpkl) file.
    """
    try:
        model: Model = Model.from_file(model_file)

        def get_unique_aperture_groups(model):
            unique_aperture_groups = {}
            for ap in model.apertures:
                if isinstance(ap.boundary_condition, Outdoors):
                    dgi = ap.properties.radiance.dynamic_group_identifier
                    if dgi is not None:
                        ap.properties.radiance.remove_states()
                        if dgi in unique_aperture_groups:
                            unique_aperture_groups[dgi].append(ap)
                        else:
                            unique_aperture_groups[dgi] = [ap]

            return unique_aperture_groups

        unique_aperture_groups = get_unique_aperture_groups(model)
        if unique_aperture_groups:  # there are aperture groups in the model already
            pass
        elif not unique_aperture_groups and create_groups:  # no aperture groups, create them
            model.solve_adjacency()
            model = automatic_aperture_grouping(
                model, room_based=True, view_factor_or_orientation=False)
            unique_aperture_groups = get_unique_aperture_groups(model)
        else:
            raise ValueError(
                'No aperture groups found in the model. Either provide a model with aperture '
                'groups or use the --create-groups option to calculate the aperture groups as '
                'part of this command.'
            )

        for apertures in unique_aperture_groups.values():
            shades = []
            # create the shades
            for ap in apertures:
                vec = ap.normal * distance
                in_vec = vec.reverse()
                base_geo = ap.geometry.move(in_vec)
                if base_geo.is_convex:
                    base_geo = base_geo.scale(scale, base_geo.centroid)
                else:
                    plane = base_geo.plane
                    origin = base_geo.polygon2d.pole_of_inaccessibility(0.01)
                    origin_xyz = plane.xy_to_xyz(origin)
                    base_geo = base_geo.scale(scale, origin_xyz)
                diff_ref = 0.2
                trans_mod = Trans.from_reflected_specularity(
                    identifier='generic-blind-trans', r_reflectance=diff_ref,
                    g_reflectance=diff_ref, b_reflectance=diff_ref,
                    transmitted_diff=diffuse_transmission,
                    transmitted_spec=specular_transmission)
                # state geometry
                state_geo = StateGeometry('{}_blind'.format(ap.identifier), base_geo, trans_mod)
                shades.append(state_geo)

            # blind state
            blind_state = RadianceSubFaceState(shades=shades)

            # default state and blind state
            states = [RadianceSubFaceState(), blind_state]
            apertures[0].properties.radiance.states = [state.duplicate() for state in states]

            # remove shades from following apertures to ensure they aren't double-counted
            states_wo_shades = []
            for state in states:
                new_state = state.duplicate()
                new_state.remove_shades()
                states_wo_shades.append(new_state)
            for ap in apertures[1:]:
                ap.properties.radiance.states = \
                    [state.duplicate() for state in states_wo_shades]

        if output_model is None:
            output_model = '{}_blinds'.format(model.identifier)
        model.to_hbjson(output_model, '.')

    except Exception:
        _logger.exception("Failed to run add-aperture-group-blinds command.")
        traceback.print_exc()
        sys.exit(1)
    else:
        sys.exit(0)
