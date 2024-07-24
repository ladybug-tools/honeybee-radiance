"""Functions for post-processing LEED daylight outputs."""
import json
import os
import shutil
import math

from honeybee.model import Model
from honeybee.units import conversion_factor_to_meters
from ..writer import _filter_by_pattern


def _process_input_folder(folder, filter_pattern):
    """Process and input annual daylight results folder."""
    info = os.path.join(folder, 'grids_info.json')
    with open(info) as data_f:
        data = json.load(data_f)
    grids = _filter_by_pattern(data, filter=filter_pattern)
    return grids


def ill_pass_fail_from_folder(
        results_folder, glare_control=True, grids_filter='*'):
    """Compute a list of LEED pass/fail values from a list of illuminance results.

    Args:
        results_folder: Folder containing illuminance result (.res) files for
            a single irradiance simulation.
        glare_control: A boolean for whether the model has "view-preserving automatic
            (with manual override) glare-control devices," which means that illuminance
            only needs to be above 300 lux and not between 300 and 3000 lux.
        grids_filter: A pattern to filter the grids. By default all the grids will be
            processed.

    Returns:
        A list of lists where each sub-list represents a sensor grid and contains
        zero/one values for whether each sensor fails/passes the LEED illuminance
        criteria.
    """
    pass_fail = []
    grids = _process_input_folder(results_folder, grids_filter)
    for grid in grids:
        res_file = os.path.join(results_folder, '%s.res' % grid['full_id'])
        with open(res_file) as inf:
            values = [float(line) for line in inf]
        grid_pf = []
        for val in values:
            if val > 300:
                pf = 1 if glare_control or val < 3000 else 0
                grid_pf.append(pf)
            else:
                grid_pf.append(0)
        pass_fail.append(grid_pf)
    return pass_fail


def _pass_fail_to_files(
        folder, sub_folder, pass_fail_comb, pass_fail_9, pass_fail_3, filter_pattern):
    """Write pass/fail matrices into files that can be loaded and visualized later.

    Args:
        folder: Project folder for a LEED daylight illuminance simulation.
        sub_folder: Relative path for a subfolder to write the pass/fail files for
            each sensor grid.
        pass_fail_comb: Matrix of ones/zeros for combined pass/failing.
        pass_fail_9: Matrix of ones/zeros for 9AM pass/failing.
        pass_fail_3:  Matrix of ones/zeros for 3PM pass/failing.
        filter_pattern: Pattern used to filter the grids.
    """
    # get the grids_info.json and determine which grids we are working with
    res_folder_9 = os.path.join(folder, '9AM', 'results')
    info_json = os.path.join(res_folder_9, 'grids_info.json')
    with open(info_json) as data_f:
        data = json.load(data_f)
    grids = _filter_by_pattern(data, filter=filter_pattern)

    # create the directories into which the files will be written
    output_folder = os.path.join(folder, sub_folder)
    folder_comb = os.path.join(output_folder, 'combined')
    folder_9 = os.path.join(output_folder, '9AM')
    folder_3 = os.path.join(output_folder, '3PM')
    for sub_dir in (folder_comb, folder_9, folder_3):
        if not os.path.isdir(sub_dir):
            os.makedirs(sub_dir)
        shutil.copyfile(info_json, os.path.join(sub_dir, 'grids_info.json'))

    # loop through each grid and write the results into files
    for g_d, res_c, res_9, res_3 in zip(grids, pass_fail_comb, pass_fail_9, pass_fail_3):
        g_file_name = '%s.res' % g_d['full_id']
        file_c = os.path.join(folder_comb, g_file_name)
        file_9 = os.path.join(folder_9, g_file_name)
        file_3 = os.path.join(folder_3, g_file_name)

        with open(file_c, 'w') as fc, open(file_9, 'w') as f9, open(file_3, 'w') as f3:
            for rc, r9, r3 in zip(res_c, res_9, res_3):
                fc.write(str(rc) + '\n')
                f9.write(str(r9) + '\n')
                f3.write(str(r3) + '\n')


def _sum_passing_area(pass_fails, grid_areas):
    """Compute the sum of passing area given aligned pass_fail and grid_area matrices.
    """
    area_passing = 0
    for pf, ga in zip(pass_fails, grid_areas):
        if pf == 1:
            area_passing += ga
    return area_passing


def _sum_all_passing_area(pass_fails, grid_areas):
    """Compute the sum of passing area given aligned pass_fail and grid_area matrices.
    """
    area_passing = 0
    for p_fails, g_areas in zip(pass_fails, grid_areas):
        for pf, ga in zip(p_fails, g_areas):
            if pf == 1:
                area_passing += ga
    return area_passing


def _space_by_space_summary(
        folder, sub_folder, grid_areas, units_conversion,
        pass_fail_comb, pass_fail_9, pass_fail_3, filter_pattern):
    """Write a CSV with space-by-space information for the percentage of sensors passing.

    Args:
        folder: Project folder for a LEED daylight illuminance simulation.
        sub_folder: Relative path for a subfolder to write the pass/fail files for
            each sensor grid.
        grid_areas: A matrix of numbers for the area occupied by each sensor.
        units_conversion: A number for the conversion factor from the grid_areas units
            to Meters.
        pass_fail_comb: Matrix of ones/zeros for combined pass/failing.
        pass_fail_9: Matrix of ones/zeros for 9AM pass/failing.
        pass_fail_3:  Matrix of ones/zeros for 3PM pass/failing.
        filter_pattern: Pattern used to filter the grids.
    """
     # get the grids_info.json and determine which grids we are working with
    res_folder_9 = os.path.join(folder, '9AM', 'results')
    info_json = os.path.join(res_folder_9, 'grids_info.json')
    with open(info_json) as data_f:
        data = json.load(data_f)
    grids = _filter_by_pattern(data, filter=filter_pattern)

    # define the header row of the CSV
    csv_data = [['Space Name', 'Sensor Count']]
    if len(grid_areas) == len(pass_fail_9):  # compute passing floor area for each grid
        csv_data[0].extend(['Area (m2)', 'Area (ft2)', 'Spacing (m)'])
    csv_data[0].extend(['% Passing 9AM', '% Passing 3PM', '% Passing Combined'])

    # loop through each grid and get the rows of the CSV
    if len(grid_areas) == len(pass_fail_9):
        all_data = zip(grids, grid_areas, pass_fail_comb, pass_fail_9, pass_fail_3)
        for gr, gr_a, res_c, res_9, res_3 in all_data:
            csv_row = [gr['name'], gr['count']]
            total_a = sum(gr_a)
            csv_row.append(round(total_a * units_conversion, 3))
            csv_row.append(round(csv_row[2] / 0.305, 3))
            csv_row.append(round(math.sqrt(csv_row[2] / csv_row[1]), 3))
            csv_row.append(round(100 * (_sum_passing_area(res_9, gr_a) / total_a), 2))
            csv_row.append(round(100 * (_sum_passing_area(res_3, gr_a) / total_a), 2))
            csv_row.append(round(100 * (_sum_passing_area(res_c, gr_a) / total_a), 2))
            csv_data.append(csv_row)
    else:
        all_data = zip(grids, pass_fail_comb, pass_fail_9, pass_fail_3)
        for gr, res_c, res_9, res_3 in all_data:
            csv_row = [gr['name'], gr['count']]
            total_count = csv_row[1]
            csv_row.append(round(100 * (sum(res_9) / total_count), 2))
            csv_row.append(round(100 * (sum(res_3) / total_count), 2))
            csv_row.append(round(100 * (sum(res_c) / total_count), 2))
            csv_data.append(csv_row)

    # write the results into a CSV
    output_file = os.path.join(folder, sub_folder, 'space_summary.csv')
    with open(output_file, 'w') as of:
        for row in csv_data:
            of.write(','.join((str(v) for v in row)) + '\n')


def leed_illuminance_to_folder(
        folder, glare_control=True, grids_filter='*', sub_folder=None):
    """Estimate LEED daylight credits from two point-in-time illuminance folders.

    Args:
        folder: Project folder for a LEED illuminance simulation. It should contain
            a HBJSON model and two sub-folders of complete point-in-time illuminance
            simulations labeled "9AM" and "3PM". These two sub-folders should each
            have results folders that include a grids_info.json and .res files with
            illuminance values for each sensor. If Meshes are found for the sensor
            grids in the HBJSON file, they will be used to compute percentages
            of occupied floor area that pass vs. fail. Otherwise, all sensors will
            be assumed to represent an equal amount of floor area.
        glare_control: A boolean for whether the model has "view-preserving automatic
            (with manual override) glare-control devices," which means that illuminance
            only needs to be above 300 lux and not between 300 and 3000 lux.
        grids_filter: A pattern to filter the grids. By default all the grids will be
            processed.
        sub_folder: Relative path for a subfolder to write the pass/fail files for
            each sensor grid and a space-by-space summary CSV. If None, the files
            will not be written and only the summary dictionary will be calculated.

    Returns:
        A dictionary with a summary of LEED credits in the format below. All
        percentages are between 0 and 100 and the floor areas are in the units system
        of the HBJSON model. If no sensor grid meshes were found in the HBJSON
        model and no areas could be associated with each mesh face, the output
        will not contain floor_area keys and each sensor will be assumed to
        occupy a similar area.

    .. code-block:: python

        {
            "credits": 2,
            "percentage_passing": 76.2,
            "percentage_passing_9AM": 78.5,
            "percentage_passing_3PM": 82.4,
            "sensor_count_passing": 762,
            "sensor_count_passing_9AM": 785,
            "sensor_count_passing_3PM": 824,
            "total_sensor_count": 1000,
            "floor_area_passing": 762.0,
            "floor_area_passing_9AM": 785.0,
            "floor_area_passing_3PM": 824.0,
            "total_floor_area": 1000.0
        }
    """
    # first load the results into pass/fail matrices of ones/zeros
    res_folder_9 = os.path.join(folder, '9AM', 'results')
    res_folder_3 = os.path.join(folder, '3PM', 'results')
    pass_fail_9 = ill_pass_fail_from_folder(res_folder_9, glare_control, grids_filter)
    pass_fail_3 = ill_pass_fail_from_folder(res_folder_3, glare_control, grids_filter)

    # determine which sensors pass for both hours
    pass_fail_comb = []
    for p_fails9, p_fails3 in zip(pass_fail_9, pass_fail_3):
        p_fails_comb = []
        for pf9, pf3 in zip(p_fails9, p_fails3):
            if pf9 == 1 and pf3 == 1:
                p_fails_comb.append(1)
            else:
                p_fails_comb.append(0)
        pass_fail_comb.append(p_fails_comb)

    # next, check to see if there is a HBJSON with sensor grid meshes for areas
    grid_areas, units_conversion = [], 1
    for base_file in os.listdir(folder):
        if base_file.endswith('.hbjson') or base_file.endswith('.hbpkl'):
            hb_model = Model.from_file(os.path.join(folder, base_file))
            units_conversion = conversion_factor_to_meters(hb_model.units)
            filt_grids = _filter_by_pattern(
                hb_model.properties.radiance.sensor_grids, filter=grids_filter)
            for s_grid in filt_grids:
                if s_grid.mesh is not None:
                    grid_areas.append(s_grid.mesh.face_areas)

    # write the pass/fail criteria into the sub-directory if specified
    if sub_folder:
        _pass_fail_to_files(
            folder, sub_folder, pass_fail_comb, pass_fail_9, pass_fail_3, grids_filter)
        _space_by_space_summary(
            folder, sub_folder, grid_areas, units_conversion,
            pass_fail_comb, pass_fail_9, pass_fail_3, grids_filter)

    # setup the summary dictionary with the results
    summary_dict = {
        'sensor_count_passing': sum(sum(pf) for pf in pass_fail_comb),
        'sensor_count_passing_9AM': sum(sum(pf9) for pf9 in pass_fail_9),
        'sensor_count_passing_3PM': sum(sum(pf3) for pf3 in pass_fail_3),
        'total_sensor_count': sum(len(pf9) for pf9 in pass_fail_9)
    }

    # determine the percentage passing from either mesh areas or sensor counts
    if len(grid_areas) == len(pass_fail_9):  # compute passing floor area for each grid
        area_pass_comb = _sum_all_passing_area(pass_fail_comb, grid_areas)
        area_pass_9 = _sum_all_passing_area(pass_fail_9, grid_areas)
        area_pass_3 = _sum_all_passing_area(pass_fail_3, grid_areas)
        area_total = sum(sum(sar) for sar in grid_areas)
        summary_dict['floor_area_passing'] = area_pass_comb
        summary_dict['floor_area_passing_9AM'] = area_pass_9
        summary_dict['floor_area_passing_3PM'] = area_pass_3
        summary_dict['total_floor_area'] = area_total
        pct_pass = (area_pass_comb / area_total) * 100
        pct_pass_9 = (area_pass_9 / area_total) * 100
        pct_pass_3 = (area_pass_3 / area_total) * 100
    else:
        total_count = summary_dict['total_sensor_count']
        pct_pass = (summary_dict['sensor_count_passing'] / total_count) * 100
        pct_pass_9 = (summary_dict['sensor_count_passing_9AM'] / total_count) * 100
        pct_pass_3 = (summary_dict['sensor_count_passing_3PM'] / total_count) * 100

    # lastly, estimate the number of LEED credits from the percentage passing
    summary_dict['percentage_passing'] = pct_pass
    summary_dict['percentage_passing_9AM'] = pct_pass_9
    summary_dict['percentage_passing_3PM'] = pct_pass_3
    if pct_pass >= 90:
        summary_dict['credits'] = 3
    elif pct_pass >= 75:
        summary_dict['credits'] = 2
    elif pct_pass >= 55:
        summary_dict['credits'] = 1
    else:
        summary_dict['credits'] = 0
    return summary_dict
