"""honeybee radiance ray-tracing command commands."""
import click
import sys
import logging
import os

from honeybee_radiance.config import folders
from honeybee_radiance_command.rtrace import Rtrace, RtraceOptions
from honeybee_radiance_command.rcalc import Rcalc

_logger = logging.getLogger(__name__)


@click.group(help='Commands to run ray-tracing in Radiance.')
def raytrace():
    pass


@raytrace.command('rtrace')
@click.argument(
    'octree', type=click.Path(exists=True, file_okay=True, resolve_path=True)
)
@click.argument(
    'sensor-grid', type=click.Path(exists=True, file_okay=True, resolve_path=True)
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
def rtrace_command(
        octree, sensor_grid, rad_params, rad_params_locked, output, dry_run):
    """Run rtrace command for an input octree and a sensor grid.

    \b
    Args:
        octree: Path to octree file.
        sensor_grid: Path to sensor grid file.
    """
    try:
        options = RtraceOptions()
        # parse input radiance parameters
        if rad_params:
            options.update_from_string(rad_params.strip())
        # overwrite input values with protected ones
        if rad_params_locked:
            options.update_from_string(rad_params_locked.strip())

        # create command.
        rtrace = Rtrace(
            options=options, output=output, octree=octree, sensors=sensor_grid
        )

        if dry_run:
            click.echo(rtrace)
        else:
            env = None
            if folders.env != {}:
                env = folders.env
            env = dict(os.environ, **env) if env else None
            rtrace.run(env=env)
    except Exception:
        _logger.exception('Failed to run ray-tracing command.')
        sys.exit(1)
    else:
        sys.exit(0)


@raytrace.command('daylight-factor')
@click.argument(
    'octree', type=click.Path(exists=True, file_okay=True, resolve_path=True)
)
@click.argument(
    'sensor-grid', type=click.Path(exists=True, file_okay=True, resolve_path=True)
)
@click.option(
    '--rad-params', show_default=True, help='Radiance parameters.'
)
@click.option(
    '--rad-params-locked', show_default=True, help='Protected Radiance parameters. '
    'These values will overwrite user input rad parameters.'
)
@click.option(
    '--sky-illum', '-i', default=100000, show_default=True, help='Sky illuminance value'
    '. The post-processed results will be divided by this number.'
)
@click.option(
    '--output', '-o', show_default=True, help='Path to output file. If a relative path'
    ' is provided it should be relative to project folder.'
)
@click.option(
    '--dry-run', is_flag=True, default=False, show_default=True,
    help='A flag to show the command without running it.'
)
def rtrace_with_df_post_process(
        octree, sensor_grid, rad_params, rad_params_locked, sky_illum, output, dry_run):
    """Run rtrace command with rcalc post-processing for daylight factor studies.

    \b
    Args:
        octree: Path to octree file.
        sensor_grid: Path to sensor grid file.
    """
    try:
        options = RtraceOptions()
        # parse input radiance parameters
        if rad_params:
            options.update_from_string(rad_params.strip())
        # overwrite input values with protected ones
        if rad_params_locked:
            options.update_from_string(rad_params_locked.strip())

        # create command.
        rtrace = Rtrace(options=options, octree=octree, sensors=sensor_grid)

        # add rcalc post-procing
        rcalc = Rcalc(output=output)
        rcalc.options.e = '$1=(0.265*$1+0.67*$2+0.065*$3)*17900/{}'.format(sky_illum)
        rtrace.pipe_to = rcalc

        if dry_run:
            click.echo(rtrace)
        else:
            env = None
            if folders.env != {}:
                env = folders.env
            env = dict(os.environ, **env) if env else None
            rtrace.run(env=env)
    except Exception:
        _logger.exception('Failed to run daylight-factor ray-tracing.')
        sys.exit(1)
    else:
        sys.exit(0)


@raytrace.command('point-in-time')
@click.argument(
    'octree', type=click.Path(exists=True, file_okay=True, resolve_path=True)
)
@click.argument(
    'sensor-grid', type=click.Path(exists=True, file_okay=True, resolve_path=True)
)
@click.option(
    '--rad-params', show_default=True, help='Radiance parameters.'
)
@click.option(
    '--rad-params-locked', show_default=True, help='Protected Radiance parameters. '
    'These values will overwrite user input rad parameters.'
)
@click.option(
    '--metric', '-m', default='illuminance', show_default=True,
    help='Text for the type of metric to be output from the calculation. Choose from: '
    'illuminance, irradiance, luminance, radiance.'
)
@click.option(
    '--output', '-o', show_default=True, help='Path to output file. If a relative path'
    ' is provided it should be relative to project folder.'
)
@click.option(
    '--dry-run', is_flag=True, default=False, show_default=True,
    help='A flag to show the command without running it.'
)
def rtrace_with_pit_post_process(
        octree, sensor_grid, rad_params, rad_params_locked, metric, output, dry_run):
    """Run rtrace command with rcalc post-processing for point-in-time studies.

    \b
    Args:
        octree: Path to octree file.
        sensor_grid: Path to sensor grid file.
    """
    try:
        options = RtraceOptions()
        # parse input radiance parameters
        if rad_params:
            options.update_from_string(rad_params.strip())
        # overwrite input values with protected ones
        if rad_params_locked:
            options.update_from_string(rad_params_locked.strip())
        # overwrite the -I attribute depending on the metric to be calculated
        if metric in ('illuminance', 'irradiance'):
            options.I = True
        elif metric in ('luminance', 'radiance'):
            options.I = False
        else:
            raise ValueError('Metric "{}" is not recognized.'.format(metric))

        # create command.
        rtrace = Rtrace(options=options, octree=octree, sensors=sensor_grid)

        # add rcalc post-procing
        rcalc = Rcalc(output=output)
        rcalc.options.e = '$1=(0.265*$1+0.67*$2+0.065*$3)*179' if metric in \
            ('illuminance', 'luminance') else '$1=(0.265*$1+0.67*$2+0.065*$3)'
        rtrace.pipe_to = rcalc

        if dry_run:
            click.echo(rtrace)
        else:
            env = None
            if folders.env != {}:
                env = folders.env
            env = dict(os.environ, **env) if env else None
            rtrace.run(env=env)
    except Exception:
        _logger.exception('Failed to run point-in-time ray-tracing.')
        sys.exit(1)
    else:
        sys.exit(0)
