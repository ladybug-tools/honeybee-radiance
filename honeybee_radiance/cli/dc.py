"""honeybee radiance daylight coefficient / contribution commands."""

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
from honeybee_radiance_command.rcontrib import Rcontrib, RcontribOptions
from honeybee_radiance_command._command_util import run_command


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
    """Run rtrace command for an input octree and a sensor grid.

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
            options.update_from_string('-aa 0.0 -V- -y {}'.format(sensor_count))
        else:
            options.update_from_string('-aa 0.0 -V+ -y {}'.format(sensor_count))

        options.M = modifiers
        # create command.
        rcontrib = Rcontrib(
            options=options, octree=octree, sensors=sensor_grid
        )

        # this is a hack until we add rmtxop command
        if output:
            cmd_template = '{rcontrib_cmd} | rmtxop -c 47.4 119.9 11.6 -fa - > {output}'
            cmd = cmd_template.format(
                rcontrib_cmd=rcontrib.to_radiance().replace('\\', '/'),
                output=output
            )
        else:
            cmd_template = '{rcontrib_cmd} | rmtxop -c 47.4 119.9 11.6 -fa -'
            cmd = cmd_template.format(
                rcontrib_cmd=rcontrib.to_radiance().replace('\\', '/'),
            )
        if dry_run:
            click.echo(cmd)
        else:
            env = None
            if folders.env != {}:
                env = folders.env
            env = dict(os.environ, **env) if env else None
            # rcontrib.run(env=env)
            run_command(cmd, env)
    except Exception:
        _logger.exception('Failed to run ray-tracing command.')
        sys.exit(1)
    else:
        sys.exit(0)
