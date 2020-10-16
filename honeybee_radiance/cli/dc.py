"""honeybee radiance daylight coefficient / contribution commands."""

try:
    import click
except ImportError:
    raise ImportError(
        'click is not installed. Try `pip install honeybee-radiance[cli]` command.'
    )

import sys
import logging

from honeybee_radiance.config import folders
from honeybee_radiance_command.rcontrib import Rcontrib, RcontribOptions
from honeybee_radiance_command._command_util import run_command
from honeybee_radiance_command.options.rfluxmtx import RfluxmtxOptions


_logger = logging.getLogger(__name__)


@click.group(help='Commands to run daylight contribution calculations in Radiance.')
def dc():
    pass

# this command includes rmtxop postprocessing
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
    '--dry-run', is_flag=True, default=False, show_default=True,
    help='A flag to show the command without running it.'
)
def rcontrib_command_with_postprocess(
        octree, sensor_grid, modifiers, sensor_count, rad_params, rad_params_locked,
        output, coeff, dry_run
):
    """Run rcontrib command for an input octree and a sensor grid.

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
            raise ValueError('for time-being sensor count must be provided.')

        if coeff:
            options.update_from_string('-aa 0.0 -V- -faf -y {}'.format(sensor_count))
        else:
            options.update_from_string('-aa 0.0 -V+ -faf -y {}'.format(sensor_count))

        options.M = modifiers
        # create command.
        rcontrib = Rcontrib(
            options=options, octree=octree, sensors=sensor_grid
        )
        rcontrib.output = output
        cmd = rcontrib.to_radiance().replace('\\', '/')
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


# this command includes dctimestep for postprocessing
@dc.command('scoeff')
@click.argument(
    'octree', type=click.Path(exists=True, file_okay=True, resolve_path=True)
)
@click.argument(
    'sensor-grid', type=click.Path(exists=True, file_okay=True, resolve_path=True)
)
@click.argument(
    'sky-dome', type=click.Path(exists=True, file_okay=True, resolve_path=True)
)
@click.argument(
    'sky-mtx', type=click.Path(exists=True, file_okay=True, resolve_path=True)
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
    '--dry-run', is_flag=True, default=False, show_default=True,
    help='A flag to show the command without running it.'
)
def rfluxmtx_command_with_postprocess(
        octree, sensor_grid, sky_dome, sky_mtx, sensor_count, rad_params,
        rad_params_locked, output, dry_run
):
    """Run rtrace command for an input octree and a sensor grid.

    octree: Path to octree file.

    sensor-grid: Path to sensor grid file.

    sky-dome: Path to sky dome for coefficient calculation.

    sky-mtx: Path to sky matrix for dctimstep input.

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
            raise ValueError('for time-being sensor count must be provided.')

        options.update_from_string('-aa 0.0 -faf -y {}'.format(sensor_count))

        # create command.
        cmd_template = 'rfluxmtx {rad_params} - {sky_dome} -i {octree} < ' \
            '{sensors} | rmtxop -ff - {sky_mtx}'

        if output:
            cmd_template = cmd_template + ' > {output}'.format(output=output)

        cmd = cmd_template.format(
            rad_params=options.to_radiance(), sky_dome=sky_dome, octree=octree,
            sensors=sensor_grid, sky_mtx=sky_mtx
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

# TODO: add test
# rfluxmtx -aa 0.0 -ss 0.0 -st 0.85 -I -fad -y 174 -ab 1 -ad 5000 -lw 2e-06 -as 128 -dc 0.25 -dj 0.0 -dp 64 -ds 0.5 -dr 0 -dt 0.5 -lr 4 - sky.dome -i scene.oct < grid.pts > flux.dc && dctimestep -of flux.dc sky.mtx | rmtxop -c 47.4 119.9 11.6 -fa - > results.ill
