"""Functions for post-processing annual irradiance outputs.

Note: These functions will most likely be moved to a separate package in the near future.
"""
import os
import shutil
import json

from ladybug.wea import Wea

from .annual import remove_header


def annual_irradiance_to_folder(folder, wea, timestep=1, sub_folder='metrics'):
    """Compute irradiance metrics in a folder and write them in a subfolder.

    This command generates 3 files for each input grid.

        * average_irradiance/{grid-name}.res -- Average Irradiance (W/m2)
        * peak_irradiance/{grid-name}.res -- Peak Irradiance (W/m2)
        * cumulative_radiation/{grid-name}.res -- Cumulative Radiation (kWh/m2)

    Args:
        folder: Results folder from an annual irradiance recipe.
        wea: The .wea file that was used in the annual irradiance simulation. This
            will be used to determine the duration of the analysis for computing
            cumulative radiation.
        timestep: The timestep of the Wea file, which is used to ensure the summed
            row of irradiance yields cumulative radiation over the time period
            of the Wea. (Default: 1).
        sub_folder: An optional relative path for subfolder to copy results
            files. (Default: metrics).

    Returns:
        str -- Path to results folder.
    """
    # get the time length of the Wea and the list of grids
    wea_len = Wea.count_timesteps(wea) * timestep
    grids = [g.replace('.ill', '') for g in os.listdir(folder) if g.endswith('.ill')]
    grid_info = os.path.join(folder, 'grids_info.json')

    # write a record of the timestep into the result folder for result processing
    t_step_f = os.path.join(folder, 'timestep.txt')
    with open(t_step_f, 'w') as t_f:
        t_f.write(str(timestep))

    # setup the folder into which the metrics will be written
    metrics_folder = os.path.join(folder, sub_folder)
    metrics_folders = []
    for sub_f in ('average_irradiance', 'peak_irradiance', 'cumulative_radiation'):
        m_path = os.path.join(metrics_folder, sub_f)
        metrics_folders.append(m_path)
        if not os.path.isdir(m_path):
            os.makedirs(m_path)
        grid_info_copy = os.path.join(m_path, 'grids_info.json')
        shutil.copyfile(grid_info, grid_info_copy)

    # loop through the grids and compute metrics
    for grid in grids:
        input_matrix = os.path.join(folder, '{}.ill'.format(grid))
        first_line, input_file = remove_header(input_matrix)
        avg = os.path.join(metrics_folders[0], '{}.res'.format(grid))
        pk = os.path.join(metrics_folders[1], '{}.res'.format(grid))
        cml = os.path.join(metrics_folders[2], '{}.res'.format(grid))
        with open(avg, 'w') as avg_i, open(pk, 'w') as pk_i, open(cml, 'w') as cml_r:
            # calculate the values for the first line
            values = [float(v) for v in first_line.split()]
            total_val = sum(values)
            avg_i.write('{}\n'.format(total_val / wea_len))
            pk_i.write('{}\n'.format(max(values)))
            cml_r.write('{}\n'.format(total_val / (timestep * 1000)))

            # write rest of the lines
            for line in input_file:
                try:
                    values = [float(v) for v in line.split()]
                    total_val = sum(values)
                    pk_i.write('{}\n'.format(max(values)))
                    avg_i.write('{}\n'.format(total_val / wea_len))
                    cml_r.write('{}\n'.format(total_val / (timestep * 1000)))
                except ValueError:
                    pass  # last line of the file

    # create info for honeybee-vtk results visualization
    config_file = os.path.join(metrics_folder, 'config.json')
    cfg = _annual_irradiance_config()
    with open(config_file, 'w') as outf:
        json.dump(cfg, outf)

    return metrics_folder


def _annual_irradiance_config():
    """Return vtk-config for annual irradiance. """
    cfg = {
        "data": [
            {
                "identifier": "Cumulative Radiation",
                "object_type": "grid",
                "unit": "kW/m2",
                "path": 'cumulative_radiation',
                "hide": False,
                "legend_parameters": {
                    "hide_legend": False,
                    "color_set": "original",
                    "min": 0,
                    "max": 1400,
                    "label_parameters": {
                        "color": [34, 247, 10],
                        "size": 0,
                        "bold": True
                    }
                }
            },
            {
                "identifier": "Peak Irradiance",
                "object_type": "grid",
                "unit": "W/m2",
                "path": 'peak_irradiance',
                "hide": False,
                "legend_parameters": {
                    "hide_legend": False,
                    "color_set": "original",
                    "min": 0,
                    "max": 200,
                    "label_parameters": {
                        "size": 0,
                        "color": [34, 247, 10],
                        "bold": True
                    }
                }
            },
            {
                "identifier": "Average Irradiance",
                "object_type": "grid",
                "unit": "W/m2",
                "path": 'average_irradiance',
                "hide": False,
                "legend_parameters": {
                    "hide_legend": False,
                    "color_set": "original",
                    "min": 0,
                    "max": 200,
                    "label_parameters": {
                        "color": [34, 247, 10],
                        "size": 0,
                        "bold": True
                    }
                }
            }
        ]
    }

    return cfg
