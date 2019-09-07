"""honeybee radiance sky commands.""" 

try:
    import click
except ImportError:
    raise ImportError(
        'click is not installed. Try `pip install . [cli]` command.'
    )

import sys
import honeybee_radiance.lightsource.sky as hbsky
import logging

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
        c_sky =hbsky.CertainIrradiance.from_illuminance(illum)
        c_sky.to_file(folder, name, True)
    except Exception:
        _logger.exception('Failed to generate sky.')
        sys.exit(1)
