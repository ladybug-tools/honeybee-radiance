"""honeybee radiance sky commands."""
import click
import sys
import os
import logging
import json

import honeybee_radiance.lightsource.sky as hbsky

from honeybee_radiance.config import folders
from honeybee_radiance_command.gendaymtx import Gendaymtx, GendaymtxOptions
from honeybee_radiance_command._command_util import run_command


_logger = logging.getLogger(__name__)


@click.group(help='Commands to generate Radiance skies.')
def sky():
    pass


@sky.command('illuminance')
@click.argument('illum', default=100000, type=float)
@click.option('--folder', help='Output folder.', default='.', show_default=True)
@click.option('--name', help='Sky file name.', default=None, show_default=True)
def sky_with_certain_illum(illum, folder, name):
    """Generate an overcast / cloudy sky with certain illuminance value.

    illum: Desired illuminance value in lux. [default: 100000].
    """
    try:
        c_sky = hbsky.CertainIrradiance.from_illuminance(illum)
        c_sky.to_file(folder, name, True)
    except Exception:
        _logger.exception('Failed to generate sky.')
        sys.exit(1)


@sky.command('skydome')
@click.option('--folder', help='Output folder.', default='.', show_default=True)
@click.option('--name', help='Sky file name.', default=None, show_default=True)
def sky_dome(folder, name):
    """Virtual skydome for daylight coefficient studies with constant radiance.

    Use this sky to calculate daylight matrix.
    """
    try:
        c_sky = hbsky.SkyDome()
        c_sky.to_file(folder, name, True)
    except Exception:
        _logger.exception('Failed to generate sky.')
        sys.exit(1)


@sky.command('mtx')
@click.argument('wea', type=click.Path(
    exists=True, file_okay=True, dir_okay=False, resolve_path=True))
@click.option(
    '--north', default=0, type=float, show_default=True,
    help='Angle to north (0-360). 90 is west and 270 is east')
@click.option(
    '--sky-type', type=click.Choice(['sun-only', 'no-sun', 'total']),
    default='total'
)
@click.option(
    '--output-format', type=click.Choice(['float', 'double', 'ASCII']),
    default='ASCII'
)
@click.option(
    '--hourly/--cumulative', is_flag=True, default=True, help='Flag to generate a '
    'cumulative or hourly sky.'
)
@click.option(
    '--visible/--solar', is_flag=True, default=True, help='A flag to indicate the '
    'output type. Visible is equal to -O0 and solar is -O1 in gendaymtx options. '
    'Default: visible.'
    )
@click.option(
    '--all-hours/--sun-up-hours', is_flag=True, default=True, help='A flag to indicate '
    'if only sun up hours should be included in the sky. By default all the hours from '
    'the input wea file will be included.'
)
@click.option('--folder', type=click.Path(
    exists=False, file_okay=False, dir_okay=True, resolve_path=True), default='.',
    help='Output folder.')
@click.option('--name', default='sky', help='File name.')
@click.option(
    '--log-file', help='Optional log file to output the name of the newly'
    ' created modifier files. By default the list will be printed out to stdout',
    type=click.File('w'), default='-')
@click.option(
    '--dry-run', is_flag=True, default=False, show_default=True,
    help='A flag to show the command without running it.'
)
def sunpath_from_wea_rad(
    wea, north, sky_type, output_format, hourly, visible, all_hours, folder, name,
    log_file, dry_run
        ):
    """Generate a climate-based sky matrix from a Wea file using radiance's gendaymtx.

    \b
    Args:
        wea: Path to a wea file.

    """
    try:
        if not os.path.exists(folder):
            os.makedirs(folder)
        output = os.path.join(folder, '%s.mtx' % name)
        opt = GendaymtxOptions()
        opt.r = north
        opt.O = '0' if visible else '1'
        if sky_type == 'total':
            pass
        elif sky_type == 'sun-only':
            opt.d = True
        elif sky_type == 'no-sun':
            opt.s = True

        if output_format == 'ASCII':
            pass
        elif output_format == 'float':
            opt.o = 'f'
        elif output_format == 'double':
            opt.o = 'd'

        if not hourly:
            opt.A = True

        if not all_hours:
            opt.u = True

        cmd = Gendaymtx(wea=wea, options=opt, output=output)
        if dry_run:
            print(cmd.to_radiance())
            sys.exit(0)

        run_command(cmd.to_radiance(), env=folders.env)
        files = [{'path': os.path.relpath(output, folder), 'full_path': output}]
        log_file.write(json.dumps(files))

    except Exception:
        _logger.exception('Failed to generate sunpath.')
        sys.exit(1)
    else:
        sys.exit(0)
