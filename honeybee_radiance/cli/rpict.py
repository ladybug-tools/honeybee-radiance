"""honeybee radiance rpict command."""
import click
import sys
import logging
import os

from honeybee_radiance.config import folders
from honeybee_radiance_command.rpict import Rpict, RpictOptions


_logger = logging.getLogger(__name__)


@click.group(help='Commands to run rpict in Radiance.')
def rpict():
    pass


@rpict.command('rpict')
@click.argument(
    'octree', type=click.Path(exists=True, file_okay=True, resolve_path=True)
)
@click.argument(
    'view', type=click.Path(exists=True, file_okay=True, resolve_path=True)
)
@click.option(
    '--rad-params', help='Radiance parameters.'
)
@click.option(
    '--rad-params-locked', help='Protected Radiance parameters. These values will '
    'overwrite user input rad parameters.'
)
@click.option(
    '--output', '-o', help='Path to output file. If a relative path is provided it '
    'should be relative to project folder.'
)
@click.option(
    '--dry-run', is_flag=True, default=False, show_default=True,
    help='A flag to show the command without running it.'
)
def rpict_command(
        octree, view, rad_params, rad_params_locked, output, dry_run):
    """Run rpict command for an input octree and a view file.

    \b
    Args:
        octree: Path to octree file.
        view: Path to view file.

    """
    try:
        options = RpictOptions()
        # parse input radiance parameters
        if rad_params:
            options.update_from_string(rad_params.strip())
        # overwrite input values with protected ones
        if rad_params_locked:
            options.update_from_string(rad_params_locked.strip())

        # create command.
        rpict = Rpict(
            options=options, output=output, octree=octree, view=view
        )

        if dry_run:
            click.echo(rpict)
        else:
            env = None
            if folders.env != {}:
                env = folders.env
            env = dict(os.environ, **env) if env else None
            rpict.run(env=env)
    except Exception:
        _logger.exception('Failed to run rpict command.')
        sys.exit(1)
    else:
        sys.exit(0)
