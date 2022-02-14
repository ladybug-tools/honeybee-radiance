"""honeybee radiance sunpath commands."""
import click
import sys

from honeybee_radiance.config import folders
from honeybee_radiance_command.gendaymtx import Gendaymtx, GendaymtxOptions
from honeybee_radiance_command._command_util import run_command

from honeybee_radiance.lightsource.sunpath import Sunpath
from ladybug.location import Location
from ladybug.wea import Wea
import logging
import json
import os

from .util import get_hoys

_logger = logging.getLogger(__name__)


@click.group(help='Commands to generate Radiance Sunpath.')
def sunpath():
    pass


@sunpath.command('location')
@click.option(
    '--lat', default=0, type=float, show_default=True,
    help='The latitude of the location in degrees. Values must be between -90 and 90.'
    ' Default is set to the equator.')
@click.option(
    '--lon', default=0, type=float, show_default=True,
    help='The longitude of the location in degrees')
@click.option(
    '--tz', default=0, type=float, show_default=True,
    help='A number representing the time zone of the location you are constructing. This'
    ' can improve the accuracy of the resulting sun plot.  The time zone should follow'
    ' the epw convention and should be between -12 and +12, where 0 is at Greenwich, UK,'
    ' positive values are to the East of Greenwich and negative values are to the West.')
@click.option(
    '--north', default=0, type=float, show_default=True,
    help='Angle to north (0-360). 90 is west and 270 is east')
@click.option(
    '--start-date', default='JAN-01', show_default=True,
    help='Start date as MMM-DD (e.g JUL-21). Start date itself will also be included.')
@click.option(
    '--start-time', default='00:00', show_default=True,
    help='Start time as HH:MM (e.g 14:10). Start time itself will also be included.')
@click.option(
    '--end-date', default='DEC-31', show_default=True,
    help='End date as MMM-DD (e.g JUL-21). End date itself will also be included.')
@click.option(
    '--end-time', default='23:00', show_default=True,
    help='End time as HH:MM (e.g 18:30). End time itself will also be included.')
@click.option(
    '--timestep', default=1, type=int, show_default=True,
    help='An optional integer to set the number of time steps per hour. Default is 1'
    ' for one value per hour.')
@click.option('--leap-year/--full-year', ' /-fy',
              help='Flag for whether to use a leap year.')
@click.option('--folder', default='.', help='Output folder.')
@click.option('--name', default='sunpath', help='File name.')
@click.option(
    '--log-file', help='Optional log file to output the name of the newly created'
    ' modifier files. By default the list will be printed out to stdout',
    type=click.File('w'), default='-')
@click.option(
    '--reverse-vectors', is_flag=True,
    help='Reverse sun vectors to go from ground to sky.')
def sunpath_from_location(
    lat, lon, tz, north, folder, name, log_file, start_date, start_time, end_date,
        end_time, timestep, leap_year, reverse_vectors):
    """Generate a non climate-based sunpath for a location.

    This command also generates a mod file which includes all the modifiers in sunpath.
    mod file is usually used with rcontrib command to indicate the list of modifiers.
    Since rcontrib command has a hard limit of 10,000 modifiers in a single run the files
    will be broken down into multiple files if number of modifiers is more than 10000
    modifiers.
    """
    location = Location()
    location.latitude = lat
    location.longitude = lon
    location.time_zone = tz
    try:
        sp = Sunpath(location, north)
        hoys = get_hoys(start_date, start_time, end_date, end_time, timestep, leap_year)
        sp_files = sp.to_file(
            folder, name, hoys=hoys, leap_year=leap_year, reverse_vectors=reverse_vectors
        )

        files = [
            {'path': os.path.relpath(path, folder), 'full_path': path}
            for path in sp_files['suns']
        ]

        log_file.write(json.dumps(files))
    except Exception:
        _logger.exception('Failed to generate sunpath.')
        sys.exit(1)
    else:
        sys.exit(0)


@sunpath.command('wea')
@click.argument('wea', type=click.Path(
    exists=True, file_okay=True, dir_okay=False, resolve_path=True))
@click.option(
    '--north', default=0, type=float, show_default=True,
    help='Angle to north (0-360). 90 is west and 270 is east')
@click.option(
    '--timestep', default=1, type=int, show_default=True,
    help='An integer to set the number of time steps per hour in the wea. Default is 1'
    ' for one value per hour.')
@click.option(
    '--leap-year/--full-year', ' /-fy',
    help='Flag for whether input wea is for a leap year.'
)
@click.option('--folder', default='.', help='Output folder.')
@click.option('--name', default='sunpath', help='File name.')
@click.option(
    '--log-file', help='Optional log file to output the name of the newly'
    ' created modifier files. By default the list will be printed out to stdout',
    type=click.File('w'), default='-')
@click.option(
    '--reverse-vectors', is_flag=True,
    help='Reverse sun vectors to go from ground to sky.')
def sunpath_from_wea(wea, north, folder, name, log_file, timestep, leap_year,
                     reverse_vectors):
    """Generate a climate-based sunpath from a Wea file.

    This command also generates a mod file which includes all the modifiers in sunpath.
    mod file is usually used with rcontrib command to indicate the list of modifiers.
    Since rcontrib command has a hard limit of 10,000 modifiers in a single run the files
    will be broken down into multiple files if number of modifiers is more than 10000
    modifiers.

    wea: Path to a wea file.
    """
    try:
        wea = Wea.from_file(wea, timestep=timestep, is_leap_year=leap_year)
        sp = Sunpath(wea.location, north)
        hoys = wea.hoys
        sp_files = sp.to_file(
            folder, name, wea=wea, hoys=hoys, leap_year=leap_year,
            reverse_vectors=reverse_vectors
        )

        files = [
            {'path': os.path.relpath(path, folder), 'full_path': path}
            for path in sp_files['suns']
        ]

        log_file.write(json.dumps(files))
    except Exception:
        _logger.exception('Failed to generate sunpath.')
        sys.exit(1)
    else:
        sys.exit(0)


@sunpath.command('radiance')
@click.argument('wea', type=click.Path(
    exists=True, file_okay=True, dir_okay=False, resolve_path=True))
@click.option(
    '--north', default=0, type=float, show_default=True,
    help='Angle to north (0-360). 90 is west and 270 is east')
@click.option('--folder', type=click.Path(
    exists=False, file_okay=False, dir_okay=True, resolve_path=True), default='.',
    help='Output folder.')
@click.option('--name', default='sunpath', help='File name.')
@click.option(
    '--visible/--solar', is_flag=True, default=True, help='A flag to indicate the '
    'output type. Visible is equal to -O0 and solar is -O1 in gendaymtx options. '
    'Default: visible.'
    )
@click.option(
    '--log-file', help='Optional log file to output the name of the newly'
    ' created modifier files. By default the list will be printed out to stdout',
    type=click.File('w'), default='-')
@click.option(
    '--dry-run', is_flag=True, default=False, show_default=True,
    help='A flag to show the command without running it.'
)
def sunpath_from_wea_rad(wea, north, folder, name, visible, log_file, dry_run):
    """Generate a climate-based sunpath from a Wea file using radiance's gendaymtx.

    This command also generates a mod file which includes all the modifiers in sunpath.
    mod file is usually used with rcontrib command to indicate the list of modifiers.
    Since rcontrib command has a hard limit of 10,000 modifiers in a single run the files
    will be broken down into multiple files if number of modifiers is more than 10000
    modifiers.

    \b
    Args:
        wea: Path to a wea file.

    """
    try:
        if not os.path.exists(folder):
            os.makedirs(folder)
        opt = GendaymtxOptions()
        opt.n = True
        opt.D = os.path.join(folder, name + '.mtx').replace('\\', '//')
        opt.M = os.path.join(folder, name + '.mod').replace('\\', '//')
        opt.r = north
        opt.O = '0' if visible else '1'

        cmd = Gendaymtx(wea=wea, options=opt)

        if dry_run:
            print(cmd.to_radiance())
            sys.exit(0)

        run_command(cmd.to_radiance(), env=folders.env)
        files = [
            {'path': os.path.relpath(path, folder), 'full_path': path}
            for path in (opt.D.value, opt.M.value)
        ]

        log_file.write(json.dumps(files))
    except Exception:
        _logger.exception('Failed to generate sunpath.')
        sys.exit(1)
    else:
        sys.exit(0)


@sunpath.command('epw')
@click.argument('epw', type=click.Path(
    exists=True, file_okay=True, dir_okay=False, resolve_path=True))
@click.option(
    '--north', default=0, type=float, show_default=True,
    help='Angle to north (0-360). 90 is west and 270 is east')
@click.option(
    '--start-date', default='JAN-01', show_default=True,
    help='Start date as MMM-DD (e.g JUL-21). Start date itself will also be included.')
@click.option(
    '--start-time', default='00:00', show_default=True,
    help='Start time as HH:MM (e.g 14:10). Start time itself will also be included.')
@click.option(
    '--end-date', default='DEC-31', show_default=True,
    help='End date as MMM-DD (e.g JUL-21). End date itself will also be included.')
@click.option(
    '--end-time', default='23:00', show_default=True,
    help='End time as HH:MM (e.g 18:30). End time itself will also be included.')
@click.option(
    '--timestep', default=1, type=int, show_default=True,
    help='An optional integer to set the number of time steps per hour. Default is 1'
    ' for one value per hour.')
@click.option(
    '--leap-year/--full-year', ' /-fy',
    help='Flag for whether input epw is for a leap year.'
)
@click.option('--folder', default='.', help='Output folder.')
@click.option('--name', default='sunpath', help='File name.', type=str)
@click.option(
    '--log-file', help='Optional log file to output the name of the newly'
    ' created modifier files. By default the list will be printed out to stdout',
    type=click.File('w'), default='-')
@click.option(
    '--reverse-vectors', is_flag=True,
    help='Reverse sun vectors to go from ground to sky.')
def sunpath_from_epw(
        epw, north, folder, name, log_file, start_date, start_time, end_date, end_time,
        timestep, leap_year, reverse_vectors):
    """Generate a climate-based sunpath from an epw weather file.

    This command also generates a mod file which includes all the modifiers in sunpath.
    mod file is usually used with rcontrib command to indicate the list of modifiers.
    Since rcontrib command has a hard limit of 10,000 modifiers in a single run the files
    will be broken down into multiple files if number of modifiers is more than 10000
    modifiers.

    epw: Path to a epw file.
    """
    try:
        wea = Wea.from_epw_file(epw)
        sp = Sunpath(wea.location, north)
        hoys = get_hoys(start_date, start_time, end_date, end_time, timestep, leap_year)
        sp_files = sp.to_file(
            folder, name, wea=wea, hoys=hoys, leap_year=leap_year,
            reverse_vectors=reverse_vectors
        )

        files = [
            {'path': os.path.relpath(path, folder), 'full_path': path}
            for path in sp_files['suns']
        ]

        log_file.write(json.dumps(files))
    except Exception:
        _logger.exception('Failed to generate sunpath.')
        sys.exit(1)
    else:
        sys.exit(0)


@sunpath.command('parse-hours')
@click.argument('suns', type=click.File(mode='r'))
@click.option('--timestep', default=1, type=int, show_default=True,
              help='This input is not used and is deprecated.')
@click.option('--leap-year/--full-year', ' /-fy',
              help='This input is not used and is deprecated.')
@click.option('--folder', default='.', help='Output folder.')
@click.option('--name', default='hours.txt', help='Output file name.')
def parse_hours_from_suns(suns, timestep, leap_year, folder, name):
    """Parse hours of the year from a suns modifier file generated by Radiance's
    gendaymtx.

    suns: Path to a suns modifiers file.
    """
    try:
        hours = []
        for line in suns:
            hours.append(int(line.split('solar')[1]) / 60)
        # write the new file to hoys
        with open(os.path.join(folder, name), 'w') as hf:
            for h in hours:
                hf.write('%s\n' % h)
    except Exception:
        _logger.exception('Failed to parse the hours.')
        sys.exit(1)
    else:
        sys.exit(0)
