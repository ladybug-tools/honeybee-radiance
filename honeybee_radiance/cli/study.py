"""honeybee radiance study command."""
import click
import sys
import logging
import os
import json

from ladybug.wea import Wea


_logger = logging.getLogger(__name__)


@click.group(help='Commands to create info files for studies.')
def study():
    pass


@study.command('study-info')
@click.argument(
    'wea', type=click.Path(exists=True, dir_okay=False, resolve_path=True))
@click.argument('timestep', type=click.INT)
@click.option('--folder', '-f', help='Output folder.', default='.', show_default=True)
@click.option(
    '--name', '-n', help='Output file name study info.',
    type=click.STRING, default='study_info', show_default=True
)
def study_info(wea, timestep, folder, name):
    """Create a study info file.

    This command generates a study info file with the timestep and the hoys of
    the wea.

    \b
    Args:
        wea: Path to wea file.
        timestep: Timestep of the study.
    """
    try:
        study_info = {}
        with open(wea) as inf:
            first_word = inf.read(5)
        is_wea = True if first_word == 'place' else False
        if not is_wea:
            _wea_file = os.path.join(os.path.dirname(wea), 'epw_to_wea.wea')
            wea = Wea.from_epw_file(wea).write(_wea_file)
        wea = Wea.from_file(wea, timestep=timestep)
        study_info['timestep'] = timestep
        study_info['study_hours'] = wea.hoys

        if not os.path.isdir(folder):
            os.makedirs(folder)

        # write JSON
        file_path = os.path.join(folder, '%s.json' % name)
        with open(file_path, 'w') as fp:
            json.dump(study_info, fp)

    except Exception:
        _logger.exception('Failed to generate study info file.')
        sys.exit(1)
    else:
        sys.exit(0)
