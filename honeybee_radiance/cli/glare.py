"""honeybee radiance dcglare command."""
import click
import sys
import logging
import os

from honeybee_radiance.config import folders
from honeybee_radiance_command.dcglare import Dcglare, DcglareOptions


_logger = logging.getLogger(__name__)


@click.group(help='Commands to run dcglare in Radiance.')
def dcglare():
    pass


@dcglare.command('two-phase')
@click.argument(
    'dc-direct', type=click.Path(exists=True, dir_okay=False, resolve_path=True))
@click.argument(
    'dc-total', type=click.Path(exists=True, dir_okay=False, resolve_path=True))
@click.argument(
    'sky-mtx', type=click.Path(exists=True, dir_okay=False, resolve_path=True))
@click.argument(
    'view-rays', type=click.Path(exists=True, dir_okay=False, resolve_path=True)
)
@click.option(
    '--glare-limit', '-l', type=float,
    help='When this option is provided, the program calculates glare autonomy, where '
    'any DGP value at or above the limit indicates the presence of glare. If the option '
    'is not provided, the program calculates DGP under each sky condition in the sky '
    'matrix instead.'
)
@click.option(
    '--threshold-factor', '-b', type=float,
    help='If larger than 100, it is used as constant threshold in cd/m2. If less than '
    'or equal to 100, this factor multiplied by the average luminance in each view will '
    'be used as threshold for detecting the glare sources (not recommended). The '
    'default value is 2000 (fixed threshold method).'
)
@click.option(
    '--occupancy-schedule', '-sf',
    type=click.Path(exists=False, dir_okay=False, resolve_path=True),
    help='In the event that the sky matrix includes unoccupied hours that should not '
    'contribute to the glare autonomy calculation, file will be read to determine which '
    'entries from the sky file matrix will be included in this calculation. Each line '
    'of file is expected to contain a numeric value at the end of a comma-delimited '
    'list, with zero corresponding to unoccupied. This argument is used only if '
    '--glare-limit (or -l) is specified.'
)
@click.option(
    '--output', '-o', help='Path to output file. If a relative path is provided it '
    'should be relative to project folder.'
)
@click.option(
    '--dry-run', is_flag=True, default=False, show_default=True,
    help='A flag to show the command without running it.'
)
def two_phase_command(
        dc_direct, dc_total, sky_mtx, view_rays, glare_limit, threshold_factor,
        occupancy_schedule, output, dry_run):
    """Run dcglare command for dcdirect and dctotal.

    \b
    Args:
        dc-direct: Path to direct contribution matrix calculated with a single ambient
            bounce.
        dc-total: Path to total contribution matrix.
        sky-mtx: Path to sky mtx.
        view-rays: Path to file of view rays.

    """
    occupancy_schedule = None if \
        (occupancy_schedule and not os.path.isfile(occupancy_schedule)) \
        else occupancy_schedule
    try:
        options = DcglareOptions()
        options.vf = view_rays
        if glare_limit:
            options.l = glare_limit
        if threshold_factor:
            options.b = threshold_factor
        if occupancy_schedule:
            options.sf = occupancy_schedule

        # create command.
        dcglare = Dcglare(
            options=options, output=output, dc_direct=dc_direct, dc_total=dc_total,
            sky_matrix=sky_mtx
        )

        if dry_run:
            click.echo(dcglare)
        else:
            env = None
            if folders.env != {}:
                env = folders.env
            env = dict(os.environ, **env) if env else None
            dcglare.run(env=env)

    except Exception:
        _logger.exception('Failed to run dcglare command.')
        sys.exit(1)
    else:
        sys.exit(0)
