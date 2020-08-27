"""honeybee radiance ray-tracing command commands."""

try:
    import click
except ImportError:
    raise ImportError(
        'click is not installed. Try `pip install honeybee-radiance[cli]` command.'
    )

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

    octree: Path to octree file.
    sensor-grid: Path to sensor grid file.
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
    '--sky-illum', '-i', default=100000, show_default=True, help='Sky illumincance value'
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
def rtrace_with_post_process(
        octree, sensor_grid, rad_params, rad_params_locked, sky_illum, output, dry_run):
    """Run rtrace command with rcalc post-processing.

    octree: Path to octree file.
    sensor-grid: Path to sensor grid file.
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

        # add post-procing to rcalc
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

# TODO: add test
# honeybee-radiance raytrace daylight-factor .\tests\assets\octree\scene.oct .\tests\assets\grid\sensor_grid_merge_0000.pts --rad-params "-ab 10 -ad 1433 -I" --rad-params-locked "-I-" --output grid.res --sky-illum 1000 --dry-run
