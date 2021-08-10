"""honeybee radiance sky commands."""
import click
import sys
import os
import logging
import json

from ladybug.dt import DateTime
from ladybug.futil import write_to_file_by_name
from ladybug.wea import Wea
from honeybee_radiance_command.gendaymtx import Gendaymtx, GendaymtxOptions
from honeybee_radiance_command._command_util import run_command

import honeybee_radiance.lightsource.sky as hbsky
from honeybee_radiance.config import folders


_logger = logging.getLogger(__name__)


@click.group(help='Commands to generate Radiance skies.')
def sky():
    pass


@sky.command('cie')
@click.argument('day', type=int, default=21)
@click.argument('month', type=str, default='Jun')
@click.argument('time', type=str, default='12:00')
@click.option('--latitude', '-lat', type=float, default=0, show_default=True,
              help='Location latitude between -90 (south) and 90 (north).')
@click.option('--longitude', '-lon', type=float, default=0, show_default=True,
              help='Location longitude between -180 (west) and 180 (east).')
@click.option('--time-zone', '-tz', type=int, default=None,
              help='Time zone between -12 hours (west) and +14 hours (east). If '
              'unspecified, the time will be interpreted as solar time at the '
              'given longitude.')
@click.option('--sky-type', '-type', type=int, default=0, show_default=True, help='An '
              'integer from 0..5 to indicate CIE Sky Type. 0 = Sunny with sun, 1 = Sunny'
              ' without sun, 2 = Intermediate with sun, 3 = Intermediate without sun, '
              '4 = Cloudy sky, 5 = Uniform cloudy sky.')
@click.option('--north', '-n', type=float, default=0, show_default=True, help='A '
              'number between -360 and 360 for the counterclockwise difference between '
              'the North and the positive Y-axis in degrees. 90 is West; 270 is East')
@click.option('--ground', '-g', type=float, default=0.2, show_default=True,
              help='Fractional value for ground reflectance.')
@click.option('--altitude', '-alt', type=float, default=None,
              help='Solar altitude measured in degrees above the horizon.')
@click.option('--azimuth', '-az', type=float, default=None,
              help='Solar azimuth measured in degrees east of North. East is 90, South '
              'is 180 and West is 270. Note that this is different from Radiance '
              'convention where the azimuth degrees are measured in west of South.')
@click.option('--folder', help='Output folder.', default='.', show_default=True)
@click.option('--name', help='Sky file name.', default=None, show_default=True)
def sky_cie(day, month, time, latitude, longitude, time_zone, sky_type,
            north, ground, altitude, azimuth, folder, name):
    """Get a CIE sky file from parameters.

    These can be a minimal representation of the sky through altitude and azimuth (eg.
    "cie -alt 71.6 -az 185.2 -type 0"). Or it can be a detailed specification of
    time and location (eg. "cie 21 Jun 12:00 -lat 41.78 -lon -87.75 -type 0").
    Both the altitude and azimuth must be specified for the minimal representation
    to be used. Otherwise, this command defaults to the detailed specification
    of time and location.

    \b
    Args:
        day: An intger for the day of the month (between 1 and 28-31).
        month: Text for the 3-letter abbreviation of the month of the year (eg. "Mar").
        time: Text for the time of day (from 0:00 to 23:59).
    """
    try:
        if altitude is not None and azimuth is not None:
            sky_obj = hbsky.CIE(altitude, azimuth, sky_type, ground)
        else:
            dtime = DateTime.from_date_time_string('{} {} {}'.format(day, month, time))
            sky_obj = hbsky.CIE.from_lat_long(
                latitude, longitude, time_zone, dtime.month, dtime.day, dtime.float_hour,
                sky_type, north, ground)
        sky_obj.to_file(folder, name, True)
    except Exception:
        _logger.exception('Failed to generate sky.')
        sys.exit(1)


@sky.command('climate-based')
@click.argument('day', type=int, default=21)
@click.argument('month', type=str, default='Jun')
@click.argument('time', type=str, default='12:00')
@click.option('--latitude', '-lat', type=float, default=0, show_default=True,
              help='Location latitude between -90 (south) and 90 (north).')
@click.option('--longitude', '-lon', type=float, default=0, show_default=True,
              help='Location longitude between -180 (west) and 180 (east).')
@click.option('--time-zone', '-tz', type=int, default=None,
              help='Time zone between -12 hours (west) and +14 hours (east). If '
              'unspecified, the time will be interpreted as solar time at the '
              'given longitude.')
@click.option('--direct-normal-irradiance', '-dni', type=float, default=0,
              show_default=True, help='Direct normal irradiance (W/m2).')
@click.option('--diffuse_horizontal_irradiance', '-dhi', type=float, default=0,
              show_default=True, help='Diffuse horizontal irradiance (W/m2).')
@click.option('--north', '-n', type=float, default=0, show_default=True, help='A '
              'number between -360 and 360 for the counterclockwise difference between '
              'the North and the positive Y-axis in degrees. 90 is West; 270 is East')
@click.option('--ground', '-g', type=float, default=0.2, show_default=True,
              help='Fractional value for ground reflectance.')
@click.option('--altitude', '-alt', type=float, default=None,
              help='Solar altitude measured in degrees above the horizon.')
@click.option('--azimuth', '-az', type=float, default=None,
              help='Solar azimuth measured in degrees east of North. East is 90, South '
              'is 180 and West is 270. Note that this is different from Radiance '
              'convention where the azimuth degrees are measured in west of South.')
@click.option('--folder', help='Output folder.', default='.', show_default=True)
@click.option('--name', help='Sky file name.', default=None, show_default=True)
def sky_climate_based(
        day, month, time, latitude, longitude, time_zone, direct_normal_irradiance,
        diffuse_horizontal_irradiance, north, ground, altitude, azimuth, folder, name):
    """Get a ClimateBased sky file from parameters.

    These can be a minimal representation of the sky through altitude and azimuth (eg.
    "climate-based -alt 71.6 -az 185.2 -dni 800 -dhi 120"). Or it can be a detailed
    specification of time and location (eg. "climate-based 21 Jun 12:00 -lat 41.78
    -lon -87.75 -dni 800 -dhi 120"). Both the altitude and azimuth must be specified
    for the minimal representation to be used. Otherwise, this command defaults
    to the detailed specification of time and location.

    \b
    Args:
        day: An intger for the day of the month (between 1 and 28-31).
        month: Text for the 3-letter abbreviation of the month of the year (eg. "Mar").
        time: Text for the time of day (from 0:00 to 23:59).
    """
    try:
        if altitude is not None and azimuth is not None:
            sky_obj = hbsky.ClimateBased(
                altitude, azimuth, direct_normal_irradiance,
                diffuse_horizontal_irradiance, ground)
        else:
            dtime = DateTime.from_date_time_string('{} {} {}'.format(day, month, time))
            sky_obj = hbsky.ClimateBased.from_lat_long(
                latitude, longitude, time_zone, dtime.month, dtime.day, dtime.float_hour,
                direct_normal_irradiance, diffuse_horizontal_irradiance,
                north, ground)
        sky_obj.to_file(folder, name, True)
    except Exception:
        _logger.exception('Failed to generate sky.')
        sys.exit(1)


@sky.command('irradiance')
@click.argument('irrad', default=558.659, type=float)
@click.option('--ground', '-g', type=float, default=0.2, show_default=True,
              help='Fractional value for ground reflectance.')
@click.option('--cloudy/--uniform', '-u', default=True,
              help='Flag to note whether the sky is uniform instead of cloudy.')
@click.option('--folder', help='Output folder.', default='.', show_default=True)
@click.option('--name', help='Sky file name.', default=None, show_default=True)
def sky_with_certain_irrad(irrad, ground, cloudy, folder, name):
    """Generate an overcast / cloudy sky with certain irradiance value.

    \b
    Args:
        irrad: Desired irradiance value in W/m2. (Default: 558.659).
    """
    try:
        uniform = not cloudy
        c_sky = hbsky.CertainIrradiance(irrad, ground, uniform)
        c_sky.to_file(folder, name, True)
    except Exception:
        _logger.exception('Failed to generate sky.')
        sys.exit(1)


@sky.command('illuminance')
@click.argument('illum', default=100000, type=float)
@click.option('--ground', '-g', type=float, default=0.2, show_default=True,
              help='Fractional value for ground reflectance.')
@click.option('--cloudy/--uniform', '-u', default=True,
              help='Flag to note whether the sky is uniform instead of cloudy.')
@click.option('--folder', help='Output folder.', default='.', show_default=True)
@click.option('--name', help='Sky file name.', default=None, show_default=True)
def sky_with_certain_illum(illum, ground, cloudy, folder, name):
    """Generate an overcast / cloudy sky with certain illuminance value.

    \b
    Args:
        illum: Desired illuminance value in lux. (Default: 100000).
    """
    try:
        uniform = not cloudy
        c_sky = hbsky.CertainIrradiance.from_illuminance(illum, ground, uniform)
        c_sky.to_file(folder, name, True)
    except Exception:
        _logger.exception('Failed to generate sky.')
        sys.exit(1)


@sky.command('skydome')
@click.option(
    '--sky-density', type=int, help='Sky patch subdivision density. This values is '
    'similar to -m option in gendaymtx command. Default is 1 which means 145 sky '
    'patches and 1 patch for the ground. One can add to the resolution typically by '
    'factors of two (2, 4, 8, ...) which yields a higher resolution sky using the '
    'Reinhart patch subdivision', default=1, show_default=True)
@click.option('--folder', help='Output folder.', default='.', show_default=True)
@click.option('--name', help='Sky file name.', default=None, show_default=True)
def sky_dome(sky_density, folder, name):
    """Virtual skydome for daylight coefficient studies with constant radiance.

    Use this sky to calculate daylight matrix.
    """
    try:
        c_sky = hbsky.SkyDome(sky_density=sky_density)
        c_sky.to_file(folder, name, True)
    except Exception:
        _logger.exception('Failed to generate sky.')
        sys.exit(1)


@sky.command('uniform-sky')
@click.option('--ground-emittance', '-g', type=float, help='Ground emittance value.',
              default=0.2, show_default=True)
@click.option('--folder', help='Output folder.', default='.', show_default=True)
@click.option('--name', help='Sky file name.', default='uniform_sky', show_default=True)
def uniform_sky(ground_emittance, folder, name):
    """Virtual skydome with uniform characteristics.

    This sky is usually used to create an octree that is sent to rcontrib command.
    """
    try:
        c_sky = hbsky.UniformSky(ground_emittance=ground_emittance)
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
    '--sky-density', type=int, default=1, help='The density of generated sky. This '
    'input corresponds to gendaymtx -m option. -m 1 generates 146 patch starting with '
    '0 for the ground and continuing to 145 for the zenith. Increasing the -m parameter '
    'yields a higher resolution sky using the Reinhart patch subdivision. For example, '
    'setting -m 4 yields a sky with 2305 patches plus one patch for the ground.'
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
    wea, north, sky_type, sky_density, output_format, hourly, visible, all_hours,
    folder, name, log_file, dry_run
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
        if sky_density > 1:
            opt.m = sky_density

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


@sky.command('adjust-for-metric')
@click.argument('sky', type=click.Path(
    exists=True, file_okay=True, dir_okay=False, resolve_path=True))
@click.option(
    '--metric', '-m', default='illuminance', show_default=True,
    help='Text for the type of metric to be output from the calculation. Choose from: '
    'illuminance, irradiance, luminance, radiance.'
)
@click.option('--folder', help='Output folder.', default='.', show_default=True)
@click.option('--name', help='Sky file name.', default=None, show_default=True)
def adjust_sky_for_metric(sky, metric, folder, name):
    """Adjust a sky file to ensure it is suitable for a given metric.

    Specifcally, this ensures that skies being created with gendaylit have a -O
    option that aligns with visible vs. solar energy.

    \b
    Args:
        sky: Path to a .sky file to be adjusted based on the metric.
    """
    try:
        with open(sky) as inf:
            content = inf.read()
        if content.startswith('!gendaylit'):
            split_content = content.split('\n')
            first_line = split_content[0].replace('-O 0', '-O 1') if metric in \
                ('irradiance', 'radiance') else split_content[0].replace('-O 1', '-O 0')
            split_content[0] = first_line
            content = '\n'.join(split_content)
        name = '{}.sky'.format(metric) if name is None else name
        write_to_file_by_name(folder, name, content, True)
    except Exception:
        _logger.exception('Failed to adjust sky.')
        sys.exit(1)


@sky.command('leed-illuminance')
@click.argument('wea', type=click.Path(
    exists=True, file_okay=True, dir_okay=False, resolve_path=True))
@click.option(
    '--north', '-n', type=float, default=0, show_default=True, help='A '
    'number between -360 and 360 for the counterclockwise difference between '
    'the North and the positive Y-axis in degrees. 90 is West; 270 is East')
@click.option('--folder', type=click.Path(
    exists=False, file_okay=False, dir_okay=True, resolve_path=True), default='.',
    help='Output folder for the two generated .sky files.')
@click.option(
    '--name', help='Sky file base name. Each of the two output skies will have this '
    'base name concatenated with 9AM or 3PM', default='', show_default=True)
@click.option(
    '--log-file', help='Optional log file to output the information about the two '
    'generated sky files. By default the list will be printed out to stdout',
    type=click.File('w'), default='-')
def leed_illuminance(wea, north, folder, name, log_file):
    """Generate two climate-based lear skies for LEED v4.1 Daylight Option 2.

    This involves evaluating the input TMY Wea, finding the clearest day within
    15 days of September and March, and using that to generate skies at 9AM and 3PM.

    \b
    Args:
        wea: Path to a Typical Meteorological Year (TMY) .wea file. The file must
            be annual with a timestep of 1 for a non-leap year.
    """
    try:
        # get HOYs for the time around the equinoxes
        mar_9, sep_9 = DateTime(3, 21, 9).hoy, DateTime(9, 21, 9).hoy
        mar_3, sep_3 = DateTime(3, 21, 15).hoy, DateTime(9, 21, 15).hoy
        hoys_mar9 = list(range(int(mar_9 - (15 * 24)), int(mar_9 + (15 * 24)), 24))
        hoys_sep9 = list(range(int(sep_9 - (15 * 24)), int(sep_9 + (15 * 24)), 24))
        hoys_mar3 = list(range(int(mar_3 - (15 * 24)), int(mar_3 + (15 * 24)), 24))
        hoys_sep3 = list(range(int(sep_3 - (15 * 24)), int(sep_3 + (15 * 24)), 24))

        # analyze the Wea file to get the sunniest days around the equinoxes
        wea_obj = Wea.from_file(wea)
        dni = wea_obj.direct_normal_irradiance
        dhi = wea_obj.diffuse_horizontal_irradiance
        irr_mar9 = [x for _, x in sorted(zip([dni[h] for h in hoys_mar9], hoys_mar9))]
        irr_sep9 = [x for _, x in sorted(zip([dni[h] for h in hoys_sep9], hoys_sep9))]
        irr_mar3 = [x for _, x in sorted(zip([dni[h] for h in hoys_mar3], hoys_mar3))]
        irr_sep3 = [x for _, x in sorted(zip([dni[h] for h in hoys_sep3], hoys_sep3))]

        # create the clear sky objects from the averaged irradiance
        dni_9 = (dni[irr_mar9[-1]] + dni[irr_sep9[-1]]) / 2
        dhi_9 = (dhi[irr_mar9[-1]] + dhi[irr_sep9[-1]]) / 2
        dni_3 = (dni[irr_mar3[-1]] + dni[irr_sep3[-1]]) / 2
        dhi_3 = (dhi[irr_mar3[-1]] + dhi[irr_sep3[-1]]) / 2
        sky_obj_9 = hbsky.ClimateBased.from_location(
            wea_obj.location, 3, 21, 9, dni_9, dhi_9, north)
        sky_obj_3 = hbsky.ClimateBased.from_location(
            wea_obj.location, 3, 21, 15, dni_3, dhi_3, north)

        # write out the sky files and the log file
        output_9 = sky_obj_9.to_file(folder, '{}9AM.sky'.format(name), True)
        output_3 = sky_obj_3.to_file(folder, '{}3PM.sky'.format(name), True)
        files = [
            {
                'id': '{}9AM'.format(name),
                'path': os.path.relpath(output_9, folder),
                'full_path': output_9
            },
            {
                'id': '{}3PM'.format(name),
                'path': os.path.relpath(output_3, folder),
                'full_path': output_3
            }
        ]
        log_file.write(json.dumps(files))
    except Exception:
        _logger.exception('Failed to create LEED skies.')
        sys.exit(1)
