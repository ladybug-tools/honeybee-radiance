"""honeybee radiance daylight coefficient / contribution commands."""
import click
import sys
import logging

from honeybee_radiance.config import folders
from honeybee_radiance_command.rcontrib import Rcontrib, RcontribOptions
from honeybee_radiance_command._command_util import run_command
from honeybee_radiance_command.options.rfluxmtx import RfluxmtxOptions
from honeybee_radiance.reader import sensor_count_from_file


_logger = logging.getLogger(__name__)


@click.group(help='Commands to run daylight contribution calculations in Radiance.')
def dc():
    pass


@dc.command('scontrib')
@click.argument(
    'octree', type=click.Path(exists=True, file_okay=True, resolve_path=True)
)
@click.argument(
    'sensor-grid', type=click.Path(exists=True, file_okay=True, resolve_path=True)
)
@click.argument(
    'modifiers', type=click.Path(exists=True, file_okay=True, resolve_path=True)
)
@click.option(
    '--sensor-count', type=click.INT, show_default=True,
    help='Number of sensors in sensor grid file. Number of sensors will be parsed form'
    ' the sensor file if not provided.'
)
@click.option(
    '--rad-params', show_default=True, help='Radiance parameters.'
)
@click.option(
    '--rad-params-locked', show_default=True, help='Protected Radiance parameters. '
    'These values will overwrite user input rad parameters.'
)
@click.option(
    '--output', '-o', show_default=True, help='Path to output file. If a relative path'
    ' is provided it should be relative to project folder.'
)
@click.option(
    '--coeff/--value', is_flag=True, default=True, help='Switch between daylight '
    ' coefficient and values. Default is coeff for calculating coefficient.'
)
@click.option(
    '--conversion', help='conversion as a string which will be passed to rmtxop -c. '
    'This option is useful to post-process the results from 3 RGB components into one '
    'as part of this command.'
)
@click.option(
    '--multiply-by', help='A value to multiply by all the results. This input is '
    'helpful to adjust the values for runs with different timesteps if required. '
    'This value will be multiplied by the values provided by converstion input.',
    type=click.FLOAT, default=1
)
@click.option(
    '--output-format', help='Output type for converted results. Valid inputs are a, f '
    'and d for ASCII, float or double. If conversion is not provided you can change the '
    'output type using rad-params options.', type=click.Choice(['a', 'f', 'd']),
    default='a', show_default=True, show_choices=True
)
@click.option(
    '--order-by-sensor/--order-by-datetime', is_flag=True, default=True,
    show_default=True, help='An option to change how results are ordered in each row. '
    'By default each row are the results for a sensor during all the sun-up hours. '
    'You can change that by using --order-by-datetime flag to get the results for a '
    'single datetime in each row.'
)
@click.option(
    '--keep-header/--remove-header', ' /-h-', is_flag=True, default=True,
    help='A flag to keep or remove the header from the output file.'
)
@click.option(
    '--dry-run', is_flag=True, default=False, show_default=True,
    help='A flag to show the command without running it.'
)
def rcontrib_command_with_postprocess(
        octree, sensor_grid, modifiers, sensor_count, rad_params, rad_params_locked,
        output, coeff, conversion, multiply_by, output_format, order_by_sensor,
        keep_header, dry_run
):
    """Run rcontrib command for an input octree and a sensor grid.

    \b
    Args:
        octree: Path to octree file.
        sensor-grid: Path to sensor grid file.
        modifiers: Path to modifiers file.
    """
    try:
        options = RcontribOptions()
        # parse input radiance parameters
        if rad_params:
            options.update_from_string(rad_params.strip())
        # overwrite input values with protected ones
        if rad_params_locked:
            options.update_from_string(rad_params_locked.strip())

        if not sensor_count:
            sensor_count = sensor_count_from_file(sensor_grid)

        if coeff:
            options.update_from_string('-aa 0.0 -V- -y {}'.format(sensor_count))
        else:
            options.update_from_string('-aa 0.0 -V+ -y {}'.format(sensor_count))

        options.M = modifiers
        # create command.
        rcontrib = Rcontrib(
            options=options, octree=octree, sensors=sensor_grid
        )
        cmd = rcontrib.to_radiance().replace('\\', '/')

        if conversion and conversion.strip():
            if multiply_by != 1:
                conversion = ' '.join(str(c * multiply_by) for c in conversion.split())
            # pass the values to rmtxop
            cmd = '{command} | rmtxop -f{output_format} - -c {conversion}'.format(
                command=cmd, output_format=output_format, conversion=conversion
            )
        elif multiply_by != 1:
            conversion = '{mult} {mult} {mult}'.format(mult=multiply_by)
            cmd = '{command} | rmtxop -f{output_format} - -c {conversion}'.format(
                command=cmd, output_format=output_format, conversion=conversion
            )

        if order_by_sensor is not True:
            cmd = cmd + ' -t '
        if not keep_header:
            cmd = cmd + ' | getinfo - '
        if output:
            cmd = '{command} > {output}'.format(command=cmd, output=output)

        if dry_run:
            click.echo(cmd)
        else:
            # rcontrib.run(env=env)
            run_command(cmd, env=folders.env)
    except Exception:
        _logger.exception('Failed to run ray-tracing command.')
        sys.exit(1)
    else:
        sys.exit(0)


@dc.command('scoeff')
@click.argument(
    'octree', type=click.Path(exists=True, file_okay=True)
)
@click.argument(
    'sensor-grid', type=click.Path(exists=True, file_okay=True)
)
@click.argument(
    'sky-dome', type=click.Path(exists=True, file_okay=True)
)
@click.argument(
    'sky-mtx', type=click.Path(exists=True, file_okay=True)
)
@click.option(
    '--sensor-count', type=click.INT, show_default=True,
    help='Number of sensors in sensor grid file. Number of sensors will be parsed form'
    ' the sensor file if not provided.'
)
@click.option(
    '--rad-params', show_default=True, help='Radiance parameters.'
)
@click.option(
    '--rad-params-locked', show_default=True, help='Protected Radiance parameters. '
    'These values will overwrite user input rad parameters.'
)
@click.option(
    '--output', '-o', show_default=True, help='Path to output file. If a relative path'
    ' is provided it should be relative to project folder.'
)
@click.option(
    '--conversion', help='conversion as a string which will be passed to rmtxop -c. '
    'This option is useful to post-process the results from 3 RGB components into one '
    'as part of this command.'
)
@click.option(
    '--multiply-by', help='A value to multiply by all the results. This input is '
    'helpful to adjust the values for runs with different timesteps if required. '
    'This value will be multiplied by the values provided by converstion input.',
    type=click.FLOAT, default=1
)
@click.option(
    '--output-format', help='Output type for converted results. Valid inputs are a, f '
    'and d for ASCII, float or double.', type=click.Choice(['a', 'f', 'd']), default='f',
    show_default=True, show_choices=True
)
@click.option(
    '--order-by-sensor/--order-by-datetime', is_flag=True, default=True,
    show_default=True, help='An option to change how results are ordered in each row. '
    'By default each row are the results for a sensor during all the sun-up hours. '
    'You can change that by using --order-by-datetime flag to get the results for a '
    'single datetime in each row.'
)
@click.option(
    '--keep-header/--remove-header', ' /-h-', is_flag=True, default=True,
    help='A flag to keep or remove the header from the output file.'
)
@click.option(
    '--dry-run', is_flag=True, default=False, show_default=True,
    help='A flag to show the command without running it.'
)
def rfluxmtx_command_with_postprocess(
    octree, sensor_grid, sky_dome, sky_mtx, sensor_count, rad_params, rad_params_locked,
    output, conversion, multiply_by, output_format, order_by_sensor, keep_header, dry_run
):
    """Run rfluxmtx command and pass the results to rmtxop.

    octree: Path to octree file.

    sensor-grid: Path to sensor grid file.

    sky-dome: Path to sky dome for coefficient calculation.

    sky-mtx: Path to sky matrix.

    """
    try:
        options = RfluxmtxOptions()
        # parse input radiance parameters
        if rad_params.strip():
            options.update_from_string(rad_params.strip())
        # overwrite input values with protected ones
        if rad_params_locked.strip():
            options.update_from_string(rad_params_locked.strip())

        if not sensor_count:
            sensor_count = sensor_count_from_file(sensor_grid)

        options.update_from_string('-aa 0.0 -faf -y {}'.format(sensor_count))

        # create command.
        cmd_template = 'rfluxmtx {rad_params} - "{sky_dome}" -i """{octree}""" < ' \
            '"{sensors}" | rmtxop -f{output_format} - "{sky_mtx}"'

        if conversion and conversion.strip():
            if multiply_by != 1:
                conversion = ' '.join(str(c * multiply_by) for c in conversion.split())
            cmd_template = cmd_template + ' -c %s' % conversion
        elif multiply_by != 1:
            conversion = '{mult} {mult} {mult}'.format(mult=multiply_by)
            cmd_template = cmd_template + ' -c %s' % conversion

        if not order_by_sensor:
            cmd_template = cmd_template + ' -t '
    
        if not keep_header:
            cmd_template = cmd_template + ' | getinfo - '
        if output:
            cmd_template = cmd_template + ' > "{output}"'.format(output=output)

        cmd = cmd_template.format(
            rad_params=options.to_radiance(), sky_dome=sky_dome, octree=octree,
            sensors=sensor_grid, output_format=output_format, sky_mtx=sky_mtx
        )

        if dry_run:
            click.echo(cmd)
        else:
            run_command(cmd, env=folders.env)
    except Exception:
        _logger.exception('Failed to run rfluxmtx command.')
        sys.exit(1)
    else:
        sys.exit(0)
