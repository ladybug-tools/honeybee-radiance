"""honeybee radiance daylight postprocessing commands."""
import click
import sys
import os
import logging
from honeybee_radiance.postprocess.annualdaylight import metrics_to_folder
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
    '--output', '-o', help='Optional path to output file to output the name of the newly'
    ' created matrix. By default the list will be printed out to stdout',
    type=click.File('w'), default='-')
def sum_matrix_rows(input_matrix, output):
    """Postprocess a Radiance matrix and add all the numbers in each row.

    \b
    This command is useful for translating Radiance results to outputs like radiation
    to total radiation. Input matrix must be in ASCII format. The header in the input
    file will be ignored.

    """
    try:
        first_line, input_file = remove_header(input_matrix)
        value = sum(float(v) for v in first_line.split())
        output.write('%s\n' % value)
        for line in input_file:
            # write sum to a new file
            value = sum(float(v) for v in line.split())
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
    '--grids_filter', '-gf', help='A pattern to filter the grids.', default='*',
    show_default=True
)
@click.option(
    '--sub_folder', '-sf', help='Optional relative path for subfolder to copy output'
    'files.', default='metrics'
)
def annual_metrics(
    folder, schedule, threshold, lower_threshold, upper_threshold, grids_filter,
    sub_folder
        ):
    """Compute annual metrics in a folder and write them in a subfolder.

    \b
    This command generates 5 files for each input grid.
        {grid-name}.da -> Daylight Autonomy
        {grid-name}.cda -> Continuos Daylight Autonomy
        {grid-name}.udi -> Useful Daylight Illuminance
        {grid-name}_upper.udi -> Upper Useful Daylight Illuminance
        {grid-name}_lower.udi -> Lower Useful Daylight Illuminance

    \b
    Args:
        results_folder: Results folder. This folder is an output folder of annual
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
