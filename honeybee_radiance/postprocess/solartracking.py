"""Functions for post-processing results of dynamic objects that track the sun."""
import os
import json
import shutil
import math

from ladybug_geometry.geometry3d.pointvector import Vector3D
from ladybug.sunpath import Sunpath


def post_process_solar_tracking(
        result_folders, sun_up_file, location, north=0, tracking_increment=5,
        destination_folder=None):
    """Postprocess a list of result folders to account for dynamic solar tracking.

    This function essentially takes .ill files for each state of a dynamic tracking
    system and produces a single .ill file that models the tracking behavior.

    Args:
        result_folders: A list of folders containing .ill files and each representing
            a state of the dynamic solar tracking system. These file should be
            ordered from eastern-most to wester-most, tracing the path of the
            tracking system over the day. The names of the .ill files should be
            the same in each folder (representing the same sensor grid in a
            different state).
        sun_up_file: Path to a sun-up-hours.txt that contains the sun-up hours of
            the simulation.
        location: A Ladybug Location object to be used to generate sun poisitions.
        north_: A number between -360 and 360 for the counterclockwise difference
            between the North and the positive Y-axis in degrees. (Default: 0).
        tracking_increment: An integer for the increment angle of each state in
            degrees. (Default: 5).
        destination_folder: A path to a destination folder where the final .ill
            files of the dynamic tracking system will be written. If None, all
            files will be written into the directory above the first result_folder.
            (Default: None).
    """
    # get the orientation angles of the panels for each model
    st_angle = int(90 - (len(result_folders) * tracking_increment / 2)) + 1
    end_angle = int(90 + (len(result_folders) * tracking_increment / 2))
    angles = list(range(st_angle, end_angle, tracking_increment))

    # create a sun path ang get the sun-up hours to be used to get solar positions
    sp = Sunpath.from_location(location, north)
    with open(sun_up_file) as suh_file:
        sun_up_hours = [float(hour) for hour in suh_file.readlines()]

    # for each hour of the sun_up_hours, figure out which file is the one to use
    mtx_to_use, ground_vec = [], Vector3D(1, 0, 0)
    for hoy in sun_up_hours:
        sun = sp.calculate_sun_from_hoy(hoy)
        vec = Vector3D(sun.sun_vector_reversed.x, 0, sun.sun_vector_reversed.z)
        orient = math.degrees(ground_vec.angle(vec))
        for i, ang in enumerate(angles):
            if ang > orient:
                mtx_to_use.append(i)
                break
        else:
            mtx_to_use.append(-1)

    # parse the grids_info in the first folder to understand the sensor grids
    grids_info_file = os.path.join(result_folders[0], 'grids_info.json')
    with open(grids_info_file) as gi_file:
        grids_data = json.load(gi_file)
    grid_ids = [g['full_id'] for g in grids_data]

    # prepare the destination folder and copy the grids_info to it
    if destination_folder is None:
        destination_folder = os.path.dirname(result_folders[0])
    if not os.path.isdir(destination_folder):
        os.mkdir(destination_folder)
    shutil.copyfile(grids_info_file, os.path.join(destination_folder, 'grids_info.json'))

    # convert the .ill files of each sensor grid into a single .ill file
    for grid_id in grid_ids:
        grid_mtx = []
        for i, model in enumerate(result_folders):
            grid_file = os.path.join(model, '{}.ill'.format(grid_id))
            with open(grid_file) as ill_file:
                grid_mtx.append([lin.split() for lin in ill_file])
        grid_ill = []
        for i, hoy_mtx in enumerate(mtx_to_use):
            hoy_vals = []
            for pt in range(len(grid_mtx[0])):
                hoy_vals.append(grid_mtx[hoy_mtx][pt][i])
            grid_ill.append(hoy_vals)
        dest_file = os.path.join(destination_folder, '{}.ill'.format(grid_id))
        with open(dest_file, 'w') as ill_file:
            for row in zip(*grid_ill):
                ill_file.write('  '.join(row) + '\n')
