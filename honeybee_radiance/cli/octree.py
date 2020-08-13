"""honeybee radiance octree commands."""

try:
    import click
except ImportError:
    raise ImportError(
        'click is not installed. Try `pip install honeybee-radiance[cli]` command.'
    )

import sys
import logging
import os

from honeybee_radiance_folder import ModelFolder
from honeybee_radiance_command.oconv import Oconv
from honeybee_radiance.config import folders

_logger = logging.getLogger(__name__)


@click.group(help='Commands to generate Radiance octree.')
def octree():
    pass


@octree.command('from-folder')
@click.argument('folder', type=click.STRING)
@click.option(
    '--output', '-o', show_default=True, help='Path to output file. If a relative path'
    ' is provided it should be relative to project folder.'
)
@click.option(
    '--default/--black', is_flag=True, default=True, show_default=True,
    help='Flag to note wheather the octree should be created with black materials.'
)
@click.option(
    '--include-aperture/--exclude-aperture', is_flag=True, default=True,
    show_default=True,
    help='Flag to note wheather apertures should be included in the octree.'
)
@click.option(
    '--add-before', type=click.STRING, multiple=True, default=None, show_default=True,
    help='Path for a file to be added to octree before scene files.'
)
@click.option(
    '--add-after', type=click.STRING, multiple=True, default=None, show_default=True,
    help='Path for a file to be added to octree after scene files.'
)
@click.option(
    '--dry-run', is_flag=True, default=False, show_default=True,
    help='A flag to show the command without running it.'
)
def create_octree_from_folder(
        folder, output, include_aperture, default, add_before, add_after, dry_run):
    """Generate a static octree from a folder.

    folder: Path to a Radiance model folder.
    """
    model_folder = ModelFolder.from_model_folder(folder)
    try:
        black_out = False if default else True
        scene_files = model_folder.scene_files(black_out=black_out)
        if include_aperture:
            # no black out here
            aperture_files = model_folder.aperture_files()
            scene_files += aperture_files
        if add_after:
            scene_files += list(add_after)
        if add_before:
            scene_files = list(add_before) + scene_files
        cmd = Oconv(output=output, inputs=scene_files)
        cmd.options.f = True
        if dry_run:
            click.echo(cmd)
        else:
            env = None
            if folders.env != {}:
                env = folders.env
            env = dict(os.environ, **env) if env else None
            cmd.run(env=env, cwd=model_folder.folder)
    except Exception:
        _logger.exception('Failed to generate octree.')
        sys.exit(1)
    else:
        sys.exit(0)
