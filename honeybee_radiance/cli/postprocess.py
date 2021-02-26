"""honeybee radiance daylight postprocessing commands."""
import click
import sys
import os
import logging
from honeybee_radiance.postprocess.annualdaylight import metrics_to_folder

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
def convert_matrix_to_binary(input_matrix, output):
    """Postprocess a Radiance matrix and convert it to 0-1 values.

    \b
    This command is useful for translating Radiance results to outputs like sunlight
    hours. Input matrix must be in ASCII format. The header in the input file will be
    ignored.

    """
    try:
        with open(input_matrix) as inf:
            first_line = next(inf)
            if first_line[:10] == '#?RADIANCE':
                for line in inf:
                    if line[:7] == 'FORMAT=':
                        # pass next empty line
                        next(inf)
                        break
                    continue
            else:
                values = [
                    '0' if float(v) == 0 else '1' for v in first_line.split()
                ]
                output.write('\t'.join(values) + '\n')
            for line in inf:
                # write binary values to new file
                values = [
                    '0' if float(v) == 0 else '1' for v in line.split()
                ]
                output.write('\t'.join(values) + '\n')
    except Exception:
        _logger.exception('Failed to convert the input file to binary format.')
        sys.exit(1)
    else:
        sys.exit(0)


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
        with open(input_matrix) as inf:
            first_line = next(inf)
            if first_line[:10] == '#?RADIANCE':
                for line in inf:
                    if line[:7] == 'FORMAT=':
                        # pass next empty line
                        next(inf)
                        break
                    continue
            else:
                value = sum(float(v) for v in first_line.split())
                output.write('%s\n' % value)
            for line in inf:
                # write sum to a new file
                value = sum(float(v) for v in line.split())
                output.write('%s\n' % value)
    except Exception:
        _logger.exception('Failed to convert the input file to binary format.')
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
