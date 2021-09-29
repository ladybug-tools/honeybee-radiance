"""honeybee radiance daylight postprocessing commands."""
import click
import sys
import os
import json
import shutil
import logging

from ladybug.wea import Wea

from honeybee_radiance.postprocess.annualdaylight import metrics_to_folder
from honeybee_radiance.postprocess.leed import leed_illuminance_to_folder
from honeybee_radiance.postprocess.solartracking import post_process_solar_tracking
from honeybee_radiance.cli.util import get_compare_func, remove_header

_logger = logging.getLogger(__name__)


@click.group(help='Commands to post-process Radiance results.')
def post_process():
    pass


@post_process.command('convert-to-binary')
@click.argument(
    'input-matrix', type=click.Path(exists=True, file_okay=True, resolve_path=True)
)
@click.option(
    '--output', '-o', help='Optional path to output file to output the name of the newly'
    ' created matrix. By default the list will be printed out to stdout',
    type=click.File('w'), default='-')
@click.option(
    '--minimum', type=float, default='-inf', help='Minimum range for values to be '
    'converted to 1.'
)
@click.option(
    '--maximum', type=float, default='+inf', help='Maximum range for values to be '
    'converted to 1.'
)
@click.option(
    '--include-max/--exclude-max', is_flag=True, help='A flag to include the maximum '
    'threshold itself. By default the threshold value will be included.', default=True
)
@click.option(
    '--include-min/--exclude-min', is_flag=True, help='A flag to include the minimum '
    'threshold itself. By default the threshold value will be included.', default=True
)
@click.option(
    '--comply/--reverse', is_flag=True, help='A flag to reverse the selection logic. '
    'This is useful for cases that you want to all the values outside a certain range '
    'to be converted to 1. By default the input logic will be used as is.', default=True
)
def convert_matrix_to_binary(
    input_matrix, output, minimum, maximum, include_max, include_min, comply
):
    """Postprocess a Radiance matrix and convert it to 0-1 values.

    \b
    This command is useful for translating Radiance results to outputs like sunlight
    hours. Input matrix must be in ASCII format. The header in the input file will be
    ignored.

    """

    compare = get_compare_func(include_min, include_max, comply)
    minimum = float(minimum)
    maximum = float(maximum)
    try:
        first_line, input_file = remove_header(input_matrix)
        values = [
            '1' if compare(float(v), minimum, maximum) else '0'
            for v in first_line.split()
        ]
        output.write('\t'.join(values) + '\n')
        for line in input_file:
            # write binary values to new file
            values = [
                '1' if compare(float(v), minimum, maximum) else '0'
                for v in line.split()
            ]
            output.write('\t'.join(values) + '\n')
    except Exception:
        _logger.exception('Failed to convert the input file to binary format.')
        sys.exit(1)
    else:
        sys.exit(0)
    finally:
        input_file.close()


@post_process.command('count')
@click.argument(
    'input-matrix', type=click.Path(exists=True, file_okay=True, resolve_path=True)
)
@click.option(
    '--output', '-o', help='Optional path to output file to output the name of the newly'
    ' created matrix. By default the list will be printed out to stdout',
    type=click.File('w'), default='-')
@click.option(
    '--minimum', type=float, default='-inf', help='Minimum range for values to be '
    'converted to 1.'
)
@click.option(
    '--maximum', type=float, default='+inf', help='Maximum range for values to be '
    'converted to 1.'
)
@click.option(
    '--include-max/--exclude-max', is_flag=True, help='A flag to include the maximum '
    'threshold itself. By default the threshold value will be included.', default=True
)
@click.option(
    '--include-min/--exclude-min', is_flag=True, help='A flag to include the minimum '
    'threshold itself. By default the threshold value will be included.', default=True
)
@click.option(
    '--comply/--reverse', is_flag=True, help='A flag to reverse the selection logic. '
    'This is useful for cases that you want to all the values outside a certain range '
    'to be converted to 1. By default the input logic will be used as is.', default=True
)
def count_values(
    input_matrix, output, minimum, maximum, include_max, include_min, comply
):
    """Count values in a row that meet a certain criteria.

    \b
    This command is useful for post processing results like the number of sensors
    which receive more than X lux at any timestep.

    """
    compare = get_compare_func(include_min, include_max, comply)
    minimum = float(minimum)
    maximum = float(maximum)
    try:
        first_line, input_file = remove_header(input_matrix)
        value = sum(
            1 if compare(float(v), minimum, maximum) else 0
            for v in first_line.split()
        )
        output.write('%d\n' % value)
        for line in input_file:
            # write binary values to new file
            value = sum(
                1 if compare(float(v), minimum, maximum) else 0
                for v in line.split()
            )
            output.write('%d\n' % value)
    except Exception:
        _logger.exception('Failed to convert the input file to binary format.')
        sys.exit(1)
    else:
        sys.exit(0)
    finally:
        input_file.close()


@post_process.command('sum-row')
@click.argument(
    'input-matrix', type=click.Path(exists=True, file_okay=True, resolve_path=True)
)
@click.option(
    '--divisor', type=float, default=1, help='An optional number, that the summed '
    'row will be divided by. For example, this can be a timestep, which can be used '
    'to ensure that a summed row of irradiance yields cumulative radiation over '
    'the entire time period of the matrix.'
)
@click.option(
    '--output', '-o', help='Optional path to output file to output the name of the newly'
    ' created matrix. By default the list will be printed out to stdout',
    type=click.File('w'), default='-')
def sum_matrix_rows(input_matrix, divisor, output):
    """Postprocess a Radiance matrix and add all the numbers in each row.

    \b
    This command is useful for translating Radiance results to outputs like radiation
    to total radiation. Input matrix must be in ASCII format. The header in the input
    file will be ignored.
    """
    try:
        first_line, input_file = remove_header(input_matrix)
        value = sum(float(v) for v in first_line.split()) / divisor
        output.write('%s\n' % value)
        for line in input_file:
            # write sum to a new file
            value = sum(float(v) for v in line.split()) / divisor
            output.write('%s\n' % value)
    except Exception:
        _logger.exception('Failed to sum numbers in each row.')
        sys.exit(1)
    else:
        sys.exit(0)
    finally:
        input_file.close()


@post_process.command('average-row')
@click.argument(
    'input-matrix', type=click.Path(exists=True, file_okay=True, resolve_path=True)
)
@click.option(
    '--output', '-o', help='Optional path to output file to output the name of the newly'
    ' created matrix. By default the list will be printed out to stdout',
    type=click.File('w'), default='-')
def average_matrix_rows(input_matrix, output):
    """Postprocess a Radiance matrix and average the numbers in each row.

    \b
    This command is useful for translating Radiance results to outputs like radiation
    to average radiation. Input matrix must be in ASCII format. The header in the input
    file will be ignored.
    """
    try:
        first_line, input_file = remove_header(input_matrix)

        # calculate the values for the first line
        values = [float(v) for v in first_line.split()]
        count = len(values)
        output.write('%s\n' % sum(values) / count)

        # write rest of the lines
        for line in input_file:
            # write sum to a new file
            value = sum(float(v) for v in line.split())
            output.write('%s\n' % value / count)

    except Exception:
        _logger.exception('Failed to average the numbers in each row.')
        sys.exit(1)
    else:
        sys.exit(0)
    finally:
        input_file.close()


@post_process.command('cumulative-radiation')
@click.argument(
    'average-irradiance', type=click.Path(exists=True, file_okay=True, resolve_path=True)
)
@click.argument(
    'wea', type=click.Path(exists=True, file_okay=True, resolve_path=True)
)
@click.option(
    '--timestep', type=int, default=1, help='The timestep of the Wea file, which '
    'is used to to compute cumulative radiation over the time period of the Wea.'
)
@click.option(
    '--output', '-o', help='Optional path to output file to output the name of the newly'
    ' created matrix. By default the list will be printed out to stdout',
    type=click.File('w'), default='-')
def cumulative_radiation(average_irradiance, wea, timestep, output):
    """Postprocess average irradiance (W/m2) into cumulative radiation (kWh/m2).

    \b
    Args:
        average_irradiance: A single-column matrix of average irradiance values.
            This input matrix must be in ASCII format.
        wea: The .wea file that was used in the irradiance simulation. This
            will be used to determine the duration of the analysis for computing
            cumulative radiation.
    """
    try:
        # parse the Wea and the average_irradiance matrix
        conversion = Wea.count_timesteps(wea) / (timestep * 1000)
        first_line, input_file = remove_header(average_irradiance)
        # calculate the value for the first line
        output.write('%s\n' % (float(first_line) * conversion))
        # write rest of the lines
        for line in input_file:
            output.write('%s\n' % (float(line) * conversion))
    except Exception:
        _logger.exception('Failed to compute cumulative radiation.')
        sys.exit(1)
    else:
        sys.exit(0)
    finally:
        input_file.close()


@post_process.command('annual-irradiance')
@click.argument(
    'folder',
    type=click.Path(exists=True, file_okay=False, dir_okay=True, resolve_path=True)
)
@click.argument(
    'wea', type=click.Path(exists=True, file_okay=True, resolve_path=True)
)
@click.option(
    '--timestep', type=int, default=1, help='The timestep of the Wea file, which '
    'is used to ensure the summed row of irradiance yields cumulative radiation over '
    'the time period of the Wea.'
)
@click.option(
    '--sub-folder', '-sf', help='Optional relative path for subfolder to write output '
    'metric files.', default='metrics'
)
def annual_irradiance(folder, wea, timestep, sub_folder):
    """Compute irradiance metrics in a folder and write them in a subfolder.

    \b
    This command generates 3 files for each input grid.
        average_irradiance/{grid-name}.res -> Average Irradiance (W/m2)
        peak_irradiance/{grid-name}.res -> Peak Irradiance (W/m2)
        cumulative_radiation/{grid-name}.res -> Cumulative Radiation (kWh/m2)

    \b
    Args:
        folder: Results folder from an annual irradiance recipe.
        wea: The .wea file that was used in the annual irradiance simulation. This
            will be used to determine the duration of the analysis for computing
            cumulative radiation.
    """
    try:
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
    except Exception:
        _logger.exception('Failed to compute irradiance metrics.')
        sys.exit(1)
    else:
        sys.exit(0)


@post_process.command('annual-daylight')
@click.argument(
    'folder',
    type=click.Path(exists=True, file_okay=False, dir_okay=True, resolve_path=True)
)
@click.option(
    '--schedule', '-sch', help='Path to an annual schedule file. Values should be 0-1 '
    'separated by new line. If not provided an 8-5 annual schedule will be created.',
    type=click.Path(exists=False, file_okay=True, dir_okay=False, resolve_path=True)
)
@click.option(
    '--threshold', '-t', help='Threshold illuminance level for daylight autonomy.',
    default=300, type=int, show_default=True
)
@click.option(
    '--lower-threshold', '-lt',
    help='Minimum threshold for useful daylight illuminance.', default=100, type=int,
    show_default=True
)
@click.option(
    '--upper-threshold', '-ut',
    help='Maximum threshold for useful daylight illuminance.', default=3000, type=int,
    show_default=True
)
@click.option(
    '--grids-filter', '-gf', help='A pattern to filter the grids.', default='*',
    show_default=True
)
@click.option(
    '--sub_folder', '-sf', help='Optional relative path for subfolder to write output '
    'metric files.', default='metrics'
)
def annual_metrics(
    folder, schedule, threshold, lower_threshold, upper_threshold, grids_filter,
    sub_folder
):
    """Compute annual metrics in a folder and write them in a subfolder.

    \b
    This command generates 5 files for each input grid.
        da/{grid-name}.da -> Daylight Autonomy
        cda/{grid-name}.cda -> Continuos Daylight Autonomy
        udi/{grid-name}.udi -> Useful Daylight Illuminance
        udi_lower/{grid-name}_upper.udi -> Upper Useful Daylight Illuminance
        udi_upper/{grid-name}_lower.udi -> Lower Useful Daylight Illuminance

    \b
    Args:
        folder: Results folder. This folder is an output folder of annual
        daylight recipe. Folder should include grids_info.json and sun-up-hours.txt.
        The command uses the list in grids_info.json to find the result files for each
        sensor grid.
    """
    # optional input - only check if the file exist otherwise ignore
    if schedule and os.path.isfile(schedule):
        with open(schedule) as hourly_schedule:
            schedule = [int(float(v)) for v in hourly_schedule]
    else:
        schedule = None

    try:
        metrics_to_folder(
            folder, schedule, threshold, lower_threshold, upper_threshold,
            grids_filter, sub_folder
        )
    except Exception:
        _logger.exception('Failed to calculate annual metrics.')
        sys.exit(1)
    else:
        sys.exit(0)


@post_process.command('leed-illuminance')
@click.argument(
    'folder',
    type=click.Path(exists=True, file_okay=False, dir_okay=True, resolve_path=True)
)
@click.option(
    '--glare-control/--no-glare-control', ' /-ngc', help='Flag to note whether '
    'the model has "view-preserving automatic (with manual override) glare-control '
    'devices," which means that illuminance only needs to be above 300 lux and not '
    'between 300 and 3000 lux.', default=True, show_default=True
)
@click.option(
    '--grids-filter', '-gf', help='A pattern to filter the grids for just the '
    'regularly occupied spaces.', default='*', show_default=True
)
@click.option(
    '--sub-folder', '-sf', help='Optional relative path for a subfolder to write the '
    'pass/fail files for each sensor grid.', default=None
)
@click.option(
    '--output-file', help='Optional JSON file to output a summary of the number '
    'of LEED credits and the percentage of sensor area that meets the criteria. '
    'By default this will be printed out to stdout',
    type=click.File('w'), default='-', show_default=True
)
def leed_illuminance(folder, glare_control, grids_filter, sub_folder, output_file):
    """Estimate LEED daylight credits from two point-in-time illuminance folders.

    \b
    Args:
        folder: Project folder for a LEED illuminance simulation. It should contain
            a HBJSON model and two sub-folders of complete point-in-time illuminance
            simulations labeled "9AM" and "3PM". These two sub-folders should each
            have results folders that include a grids_info.json and .res files with
            illuminance values for each sensor. If Meshes are found for the sensor
            grids in the HBJSON file, they will be used to compute percentages
            of occupied floor area that pass vs. fail. Otherwise, all sensors will
            be assumed to represent an equal amount of floor area.
    """
    try:
        credit_summary = leed_illuminance_to_folder(
            folder, glare_control, grids_filter, sub_folder)
        output_file.write(json.dumps(credit_summary, indent=4))
    except Exception:
        _logger.exception('Failed to calculate LEED daylight metrics.')
        sys.exit(1)
    else:
        sys.exit(0)


@post_process.command('solar-tracking')
@click.argument(
    'folder',
    type=click.Path(exists=True, file_okay=False, dir_okay=True, resolve_path=True)
)
@click.argument(
    'sun-up-hours', type=click.Path(exists=True, file_okay=True, resolve_path=True)
)
@click.argument(
    'wea', type=click.Path(exists=True, file_okay=True, resolve_path=True)
)
@click.option(
    '--north', default=0, type=float, show_default=True,
    help='Angle to north (0-360). 90 is west and 270 is east'
)
@click.option(
    '--tracking-increment', '-t', type=int, default=5, help='An integer for the '
    'increment angle of each state in degrees. (Default: 5).'
)
@click.option(
    '--sub-folder', '-sf', help='Optional relative path for subfolder to write output '
    '.ill files of the dynamic tracking system.', default='final'
)
def solar_tracking(folder, sun_up_hours, wea, north, tracking_increment, sub_folder):
    """Postprocess a list of result folders to account for dynamic solar tracking.

    \b
    This function essentially takes .ill files for each state of a dynamic tracking
    system and produces a single .ill file that models the tracking behavior.

    \b
    Args:
        folder: Results folder containing sub-folders that each represent a state
            of the dynamic solar tracking system. Each sub-folder should contain .ill
            files for that state and the names of these .ill files should be the
            same across all sub-folders.
        sun_up_hours: The .txt file containing the sun-up hours that were simulated.
        wea: The .wea file that was used in the simulation. This will be used to
            determine the solar positions.
    """
    try:
        # load all of the result sub-folders in the folder and sort them
        models = [f for f in os.listdir(folder)
                  if os.path.isdir(os.path.join(folder, f)) and
                  os.path.isfile(os.path.join(folder, f, 'grids_info.json'))]
        model_num = [int(''.join([i for i in f if i.isdigit()])) for f in models]
        sorted_models = [x for _, x in sorted(zip(model_num, models))]
        models = [os.path.join(folder, f) for f in sorted_models]

        dest_folder = os.path.join(folder, sub_folder)
        if len(models) == 1:  # not a dynamic system; just copy the files
            if not os.path.isdir(dest_folder):
                os.mkdir(dest_folder)
            for f in os.listdir(models[0]):
                shutil.copyfile(
                    os.path.join(models[0], f),
                    os.path.join(dest_folder, f))
        else:
            wea_obj = Wea.from_file(wea)
            post_process_solar_tracking(
                models, sun_up_hours, wea_obj.location, north,
                tracking_increment, dest_folder)
    except Exception:
        _logger.exception('Failed to compute irradiance metrics.')
        sys.exit(1)
    else:
        sys.exit(0)
