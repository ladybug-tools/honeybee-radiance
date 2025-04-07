# coding=utf-8
"""Functions for auto-assigning aperture groups for multiphase studies."""
from __future__ import division
import os
import math
import json
from collections import OrderedDict

from ladybug_geometry.geometry3d.mesh import Mesh3D
from ladybug.futil import write_to_file_by_name
from honeybee.boundarycondition import Outdoors
from honeybee.typing import clean_rad_string
from honeybee.config import folders as hb_folders
from honeybee_radiance_command.oconv import Oconv
from honeybee_radiance_command.rfluxmtx import RfluxmtxOptions, Rfluxmtx

from honeybee_radiance.config import folders
from honeybee_radiance.sensorgrid import SensorGrid
from honeybee_radiance.lightsource.sky.skydome import SkyDome


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


def _transpose_matrix(matrix):
    """Transposes the distance matrix."""
    matrix = list(map(list, zip(*matrix)))
    return matrix


def _rmse_from_matrix(vf_matrix_dict):
    """Calculates RMSE."""
    rmse = []
    for predicted in vf_matrix_dict.values():
        r_list = []
        for observed in vf_matrix_dict.values():
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


def _agglomerative_clustering_complete(distance_matrix, apertures, threshold=0.001):
    """Cluster apertures based on the threshold."""

    # Fill the diagonal with 9999 so a diagonal of zeros will NOT be stored
    # as min_value.
    for i in range(len(distance_matrix)):
        distance_matrix[i][i] = 9999

    # Create starting list of aperture groups. Each aperture starts as its
    # own group.
    ap_groups = apertures

    # Set the number of samples and the minimum value of the distance
    # matrix.
    n_samples = len(distance_matrix)

    # Set the minimum value of the distance matrix and find the indices of
    # the minimum value in the distance matrix.
    min_value, index = _index_and_min(distance_matrix)

    while n_samples > 1 and min_value < threshold:
        # Combine the two groups and place it at index 0, and remove item
        # at index 1.
        ap_groups[index[0]] = [ap_groups[index[0]], ap_groups[index[1]]]
        ap_groups.pop(index[1])

        # Update the values in the distance matrix. We need the maximum
        # values between the new cluster and all the remaining apertures or
        # clusters still in the distance matrix.
        distance_matrix[index[0]] = \
            _pairwise_maximum(distance_matrix[index[0]], distance_matrix[index[1]])
        distance_matrix = _transpose_matrix(distance_matrix)
        distance_matrix[index[0]] = \
            _pairwise_maximum(distance_matrix[index[0]], distance_matrix[index[1]])

        # Remove the values at index 1 along both axes.
        distance_matrix.pop(index[1])
        distance_matrix = _transpose_matrix(distance_matrix)
        distance_matrix.pop(index[1])

        # Update the number of samples that are left in the distance matrix.
        n_samples -= 1
        # Update the minimum value and the indices.
        min_value, index = _index_and_min(distance_matrix)

    return ap_groups


def aperture_view_factor(
    project_folder, apertures, size=0.2, ambient_division=1000,
    receiver='rflux_sky.sky', octree='scene.oct',
    calc_folder='aperture_grouping'
):
    """Calculates the view factor for each aperture by sensor points."""

    # Instantiate dictionary that will store the sensor count for each
    # aperture. We need a OrderedDict so that we can split the rfluxmtx
    # output file by each aperture (sensor count) in the correct order.
    ap_dict = OrderedDict()

    meshes = []
    # Create a mesh for each aperture and add the the sensor count to dict.
    for aperture in apertures:
        ap_mesh = aperture.geometry.mesh_grid(size, generate_centroids=False)
        meshes.append(ap_mesh)
        ap_dict[aperture.identifier] = \
            {
                'sensor_count': len(ap_mesh.faces),
                'aperture': aperture
            }

    # Create a sensor grid from joined aperture mesh.
    mesh = Mesh3D.join_meshes(meshes).offset_mesh(0.001)
    grid_mesh = SensorGrid.from_mesh3d('aperture_grid', mesh)

    # Write sensor grid to pts file.
    sensors = grid_mesh.to_file(os.path.join(project_folder, calc_folder),
                                file_name='apertures')

    # Rfluxmtx options.
    rflux_opt = RfluxmtxOptions()
    rflux_opt.ad = ambient_division
    rflux_opt.lw = 1.0 / float(rflux_opt.ad)
    rflux_opt.I = True
    rflux_opt.h = True

    # Rfluxmtx command.
    rflux = Rfluxmtx()
    rflux.options = rflux_opt
    rflux.receivers = receiver
    rflux.sensors = sensors
    rflux.octree = octree
    rflux.output = os.path.join(calc_folder, 'apertures_vf.mtx')

    # Run rfluxmtx command.
    env = None
    if folders.env != {}:
        env = folders.env
    env = dict(os.environ, **env) if env else None
    rflux.run(env=env, cwd=project_folder)

    # Get the output file of the rfluxmtx command.
    mtx_file = os.path.join(project_folder, rflux.output)

    return mtx_file, ap_dict


def aperture_view_factor_postprocess(mtx_file, ap_dict, room_apertures, room_based=True):
    view_factor = []
    # Read view factor file, convert to one channel output, and divide by
    # Pi.
    with open(mtx_file) as mtx_data:
        for sensor in mtx_data:
            sensor_split = sensor.strip().split()
            if len(sensor_split) % 3 == 0:
                one_channel = sensor_split[::3]

                def convert_to_vf(x):
                    return float(x) / math.pi
                view_factor.append(list(map(convert_to_vf, one_channel)))

    ap_view_factor = OrderedDict()
    # Split the view factor file by the aperture sensor count.
    for ap_id, value in ap_dict.items():
        sensor_count = value['sensor_count']
        ap_vf, view_factor = view_factor[:sensor_count], view_factor[sensor_count:]
        ap_view_factor[ap_id] = ap_vf

    ap_view_factor_mean = OrderedDict()
    # Get the mean view factor per sky patch for each aperture.
    for ap_id, ap_vf in ap_view_factor.items():
        ap_t = _transpose_matrix(ap_vf)
        ap_view_factor_mean[ap_id] = \
            [sum(sky_patch) / len(sky_patch) for sky_patch in ap_t]

    if room_based:  # Restructure ap_view_factor_mean.
        _ap_view_factor_mean = {}
        for room_id, data in room_apertures.items():
            _ap_view_factor_mean[room_id] = OrderedDict()
            for ap in data['apertures']:
                ap_id = ap.identifier
                _ap_view_factor_mean[room_id][ap_id] = ap_view_factor_mean[ap_id]
        ap_view_factor_mean = _ap_view_factor_mean

    # Calculate RMSE between all combinations of averaged aperture view factors.
    if room_based:
        rmse = OrderedDict()
        for room_id, vf_matrix_dict in ap_view_factor_mean.items():
            _rmse = _rmse_from_matrix(vf_matrix_dict)
            rmse[room_id] = _rmse
    else:
        rmse = _rmse_from_matrix(ap_view_factor_mean)

    return rmse


def cluster_view_factor(rmse, room_apertures, apertures, threshold,
                        room_based=True, vertical_tolerance=None):
    # Cluster the apertures by the 'complete method'.
    if room_based:
        ap_groups = {}
        for room_id, _rmse in rmse.items():
            ap_groups[room_id] = {}
            apertures = room_apertures[room_id]['apertures']
            _room_ap_groups = \
                _agglomerative_clustering_complete(_rmse, apertures, threshold)
            # Flatten the groups. This will break the inter-cluster
            # structure, but we do not need to know that.
            grouped_apertures = [list(_flatten(cluster)) for cluster in _room_ap_groups]
            if vertical_tolerance:
                # Check groups by vertical tolerance.
                vertical_groups = []
                for ap_group in grouped_apertures:
                    vert_dist_matrix = []
                    for ap_1 in ap_group:
                        vert_dist_list = []
                        for ap_2 in ap_group:
                            vert_dist = abs(ap_1.center.z - ap_2.center.z)
                            vert_dist_list.append(vert_dist)
                        vert_dist_matrix.append(vert_dist_list)
                    _ap_groups = _agglomerative_clustering_complete(
                        vert_dist_matrix, ap_group, vertical_tolerance
                    )
                    _ap_groups = [list(_flatten(cluster)) for cluster in _ap_groups]
                    vertical_groups.extend(_ap_groups)
                grouped_apertures = vertical_groups

            ap_groups[room_id]['aperture_groups'] = grouped_apertures
            ap_groups[room_id]['display_name'] = room_apertures[room_id]['display_name']
    else:
        ap_groups = _agglomerative_clustering_complete(rmse, apertures, threshold)
        # Flatten the groups. This will break the inter-cluster structure,
        # but we do not need to know that.
        ap_groups = [list(_flatten(cluster)) for cluster in ap_groups]
        if vertical_tolerance:
            # Check groups by vertical tolerance.
            vertical_groups = []
            for ap_group in ap_groups:
                vert_dist_matrix = []
                for ap_1 in ap_group:
                    vert_dist_list = []
                    for ap_2 in ap_group:
                        vert_dist = abs(ap_1.center.z - ap_2.center.z)
                        vert_dist_list.append(vert_dist)
                    vert_dist_matrix.append(vert_dist_list)
                _ap_groups = _agglomerative_clustering_complete(
                    vert_dist_matrix, ap_group, vertical_tolerance)
                _ap_groups = [list(_flatten(cluster)) for cluster in _ap_groups]
                vertical_groups.extend(_ap_groups)
            ap_groups = vertical_groups

    return ap_groups


def cluster_orientation(room_apertures, apertures, room_based=True, vertical_tolerance=None):
    if room_based:
        ap_groups = {}
        for room_id, data in room_apertures.items():
            _normal_list = []
            grouped_apertures = []
            ap_groups[room_id] = {}
            for ap in data['apertures']:
                # check if normal is already in list
                n_bools = [ap.normal.is_equivalent(n, tolerance=0.05)
                           for n in _normal_list]
                if not any(n_bools):
                    _normal_list.append(ap.normal)
                    # append empty list for new group
                    grouped_apertures.append([])
                for idx, n in enumerate(_normal_list):
                    if n.is_equivalent(ap.normal, tolerance=0.05):
                        group_index = idx
                grouped_apertures[group_index].append(ap)
            if vertical_tolerance:
                # Check groups by vertical tolerance.
                vertical_groups = []
                for ap_group in grouped_apertures:
                    vert_dist_matrix = []
                    for ap_1 in ap_group:
                        vert_dist_list = []
                        for ap_2 in ap_group:
                            vert_dist = abs(ap_1.center.z - ap_2.center.z)
                            vert_dist_list.append(vert_dist)
                        vert_dist_matrix.append(vert_dist_list)
                    _ap_groups = _agglomerative_clustering_complete(
                        vert_dist_matrix, ap_group, vertical_tolerance
                    )
                    _ap_groups = [list(_flatten(cluster)) for cluster in _ap_groups]
                    vertical_groups.extend(_ap_groups)
                grouped_apertures = vertical_groups

            ap_groups[room_id]['aperture_groups'] = grouped_apertures
            ap_groups[room_id]['display_name'] = data['display_name']
    else:
        _normal_list = []
        grouped_apertures = []
        for ap in apertures:
            # check if normal is already in list
            n_bools = [ap.normal.is_equivalent(n, tolerance=0.05)
                       for n in _normal_list]
            if not any(n_bools):
                _normal_list.append(ap.normal)
                # append empty list for new group
                grouped_apertures.append([])
            for idx, n in enumerate(_normal_list):
                if n.is_equivalent(ap.normal, tolerance=0.05):
                    group_index = idx
            grouped_apertures[group_index].append(ap)
        ap_groups = grouped_apertures
        if vertical_tolerance:
            # Check groups by vertical tolerance.
            vertical_groups = []
            for ap_group in ap_groups:
                vert_dist_matrix = []
                for ap_1 in ap_group:
                    vert_dist_list = []
                    for ap_2 in ap_group:
                        vert_dist = abs(ap_1.center.z - ap_2.center.z)
                        vert_dist_list.append(vert_dist)
                    vert_dist_matrix.append(vert_dist_list)
                _ap_groups = _agglomerative_clustering_complete(
                    vert_dist_matrix, ap_group, vertical_tolerance)
                _ap_groups = [list(_flatten(cluster)) for cluster in _ap_groups]
                vertical_groups.extend(_ap_groups)
            ap_groups = vertical_groups

    return ap_groups


def cluster_output(ap_groups, room_apertures, room_based=True):
    # Add the aperture group to each aperture in the dictionary.
    group_names = []
    group_dict = {}
    if room_based:
        for room_id, data in ap_groups.items():
            for idx, group in enumerate(data['aperture_groups']):
                ap_ids = [ap.identifier for ap in group]
                group_name = '{}_ApertureGroup_{}'.format(data['display_name'], idx)
                group_name = clean_rad_string(group_name)
                group_names.append(
                    {'identifier': group_name, 'apertures': ap_ids}
                )
                for ap_id in ap_ids:
                    group_dict[ap_id] = group_name
    else:
        for idx, group in enumerate(ap_groups):
            ap_ids = [ap.identifier for ap in group]
            group_name = 'ApertureGroup_{}'.format(idx)
            group_name = clean_rad_string(group_name)
            group_names.append(
                {'identifier': group_name, 'apertures': ap_ids}
            )
            for ap_id in ap_ids:
                group_dict[ap_id] = group_name

    return group_names, group_dict


def automatic_aperture_grouping(
    model, octree=None, rflux_sky=None, size=0.2, threshold=0.001, ambient_division=1000,
    room_based=True, view_factor_or_orientation=True,
    vertical_tolerance=None, states=None, working_folder=None
):
    """Automatically calculate aperture groups for exterior apertures.

    This function calculates view factor from apertures to sky patches (rfluxmtx). Each
    aperture is represented by a sensor grid, and the view factor for the whole aperture
    is the average of the grid. The apertures are grouped based on the threshold.

    Args:
        model: A Honeybee Model object to which aperture groups will be assigned.
        octree: Optional path to octree file to be used for view factor calculation.
            If None, the octree will be created from the model.
        rflux_sky: Optional path to an rflux sky file. If None, the rflux sky
            file will be auto-created.
        size: Aperture grid size. A lower number will give a finer grid and more
            accurate results but the calculation time will increase. (Default: 0.2).
        threshold: A number that determines if two apertures/aperture groups can
            be clustered. A lower number is more accurate but will also increase
            the number of aperture groups. (Default: 0.001).
        ambient_division: Number of ambient divisions (-ad) for view factor
            calculation in rfluxmtx. Increasing the number will give more accurate
            results but also increase the calculation time. (Default: 1000).
        room_based: Boolean to note whether the apertures should be grouped
            on a room basis. If grouped on a room basis apertures from different
            room cannot be in the same group. (Default: False).
        view_factor_or_orientation: Boolean to note whether the apertures should
            be grouped by calculating view factors for the apertures to a
            discretized sky (True) or simply by the normal orientation of the
            apertures (False). (Default: False).
        vertical_tolerance: A float value for vertical tolerance between two apertures.
            If the vertical distance between two apertures is larger than this
            tolerance the apertures cannot be grouped. If None, the vertical
            grouping will be skipped. (Default: None).
        states: An optional list of Honeybee State objects to be applied to all
            the generated groups. These states should be ordered based on how
            they will be switched on. The first state is the default state and,
            typically, higher states are more shaded. If the objects in the group
            have no states, the modifiers already assigned the apertures will
            be used for all states.
        working_folder: Path to a folder into which the files be written. If None,
            the files will be written into a folder called aperture_groups
            within the default simulation folder.

    Returns:
        A Model with Aperture groups automatically assigned.
    """
    # serialize the model, set the output folder, and process simpler attributes
    if working_folder is None:
        working_folder = os.path.join(hb_folders.default_simulation_folder,
                                      'aperture_groups')
    if not os.path.isdir(working_folder):
        os.makedirs(working_folder)
    view_factor = view_factor_or_orientation

    # Get all room-based apertures with Outdoors boundary condition
    apertures = []
    room_apertures = {}
    for room in model.rooms:
        for face in room.faces:
            for ap in face.apertures:
                if isinstance(ap.boundary_condition, Outdoors):
                    apertures.append(ap)
                    if room.identifier not in room_apertures:
                        room_apertures[room.identifier] = {}
                    if 'apertures' not in room_apertures[room.identifier]:
                        room_apertures[room.identifier]['apertures'] = \
                            [ap]
                    else:
                        room_apertures[room.identifier]['apertures'].append(ap)
                    if 'display_name' not in room_apertures[room.identifier]:
                        room_apertures[room.identifier]['display_name'] = \
                            room.display_name

    assert len(apertures) != 0, \
        'Found no Honeybee Apertures. There should at least be one Aperture ' \
        'in the model to compute aperture groups.'

    if view_factor:
        if not octree:
            # write octree
            model_content, modifier_content = model.to.rad(model, minimal=True)
            scene_file, mat_file = 'scene.rad', 'scene.mat'
            write_to_file_by_name(working_folder, scene_file, model_content)
            write_to_file_by_name(working_folder, mat_file, modifier_content)
            octree = 'scene.oct'
            oconv = Oconv(inputs=[mat_file, scene_file], output=octree)
            oconv.options.f = True

            # run Oconv command
            env = None
            if folders.env != {}:
                env = folders.env
            env = dict(os.environ, **env) if env else None
            oconv.run(env, cwd=working_folder)

        if not rflux_sky:
            rflux_sky = SkyDome()
            rflux_sky = rflux_sky.to_file(working_folder, name='rflux_sky.sky')

        # Calculate view factor.
        mtx_file, ap_dict = aperture_view_factor(
            working_folder, apertures, size=size, ambient_division=ambient_division,
            receiver=rflux_sky, octree=octree, calc_folder=working_folder
        )
        rmse = aperture_view_factor_postprocess(
            mtx_file, ap_dict, room_apertures, room_based
        )

    # cluster apertures into groups
    if view_factor:
        ap_groups = cluster_view_factor(
            rmse, room_apertures, apertures, threshold, room_based, vertical_tolerance)
    else:
        ap_groups = cluster_orientation(
            room_apertures, apertures, room_based, vertical_tolerance
        )

    # process clusters
    group_names, group_dict = \
        cluster_output(ap_groups, room_apertures, room_based)

    # Write aperture groups to JSON file.
    dyn_gr = os.path.join(working_folder, 'aperture_groups.json')
    with open(dyn_gr, 'w') as fp:
        json.dump(group_names, fp, indent=2)

    # Write dynamic group identifiers to JSON file.
    dyn_gr_ids = os.path.join(working_folder, 'dynamic_group_identifiers.json')
    with open(dyn_gr_ids, 'w') as fp:
        json.dump(group_dict, fp, indent=2)

    # assign dynamic group identifiers for each aperture
    group_ap_dict = {}
    for room in model.rooms:
        for face in room.faces:
            for ap in face.apertures:
                if isinstance(ap.boundary_condition, Outdoors):
                    dyn_group_id = group_dict[ap.identifier]
                    ap.properties.radiance.dynamic_group_identifier = \
                        dyn_group_id
                    try:
                        group_ap_dict[dyn_group_id].append(ap)
                    except KeyError:
                        group_ap_dict[dyn_group_id] = [ap]

    # assign any states if they are connected
    if states is not None and len(states) != 0:
        for group_aps in group_ap_dict.values():
            # assign states (including shades) to the first aperture
            group_aps[0].properties.radiance.states = \
                [state.duplicate() for state in states]
            # remove shades from following apertures to ensure they aren't double-counted
            states_wo_shades = []
            for state in states:
                new_state = state.duplicate()
                new_state.remove_shades()
                states_wo_shades.append(new_state)
            for ap in group_aps[1:]:
                ap.properties.radiance.states = \
                    [state.duplicate() for state in states_wo_shades]

    # return the model
    return model
