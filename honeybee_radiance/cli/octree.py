"""honeybee radiance octree commands."""
import click
import sys
import logging
import os
import json

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
        if include_aperture:  # no black out here
            try:
                aperture_files = model_folder.aperture_files()
                scene_files += aperture_files
            except FileNotFoundError:
                pass  # no apertures available in the model
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


@octree.command('from-folder-multiphase')
@click.argument('folder', type=click.STRING)
@click.option(
    '--sun-path',
    type=click.Path(exists=True, file_okay=True,
                    dir_okay=False, resolve_path=True),
    default=None, show_default=True,
    help='Path for a sun-path file that will be added to octrees for direct sunlight '
    'studies. If sunpath is provided an extra octree for direct_sun will be created.'
)
@click.option(
    '--phase', type=click.Choice(['2', '3', '5']), default='5', show_default=True,
    help='Select a multiphase study for which octrees will be created. 3-phase includes '
    '2-phase, and 5-phase includes 3-phase and 2-phase.'
)
@click.option("--output-folder", help="Output folder into which the files be written.",
              default="octree", show_default=True)
def create_octree_from_folder_multiphase(folder, sun_path, phase, output_folder):
    """Generate a set of octrees from a folder.

    This command will generate octrees for both default and direct studies. It will do so
    for static apertures and aperture groups, creating one octree for each light path,
    i.e., all other light paths are blacked.

    folder: Path to a Radiance model folder.
    """
    model_folder = ModelFolder.from_model_folder(folder)

    # check if sunpath file exist - otherwise continue without it
    if sun_path and not os.path.isfile(sun_path):
        sun_path = None

    if phase == '5' and not sun_path:
        raise RuntimeError(
            'To generated octrees for a 5 Phase study you must provide a sunpath.'
        )

    phases = {
        '2': ['two_phase'],
        '3': ['two_phase', 'three_phase'],
        '5': ['two_phase', 'three_phase', 'five_phase']
    }

    try:
        scene_mapping = model_folder.octree_scene_mapping()
        if not os.path.isdir(output_folder):
            os.mkdir(output_folder)
        octree_mapping = []
        for study, states in scene_mapping.items():
            if study not in phases[phase]:
                continue
            study_type = []
            for state in states:
                commands = []
                info = {'identifier': state['identifier']}
                # default
                if 'scene_files' in state:
                    scene_files = state['scene_files']
                    octree_name = state['identifier']
                    output = os.path.join(
                        output_folder, '%s.oct' % octree_name)
                    cmd = Oconv(output=output, inputs=scene_files)
                    cmd.options.f = True
                    commands.append(cmd)

                    info['octree'] = '%s.oct' % octree_name

                # direct - don't add them for 5 phase
                if 'scene_files_direct' in state and study != 'five_phase':
                    scene_files_direct = state['scene_files_direct']
                    octree_direct_name = '%s_direct' % state['identifier']
                    output_direct = os.path.join(
                        output_folder, '%s.oct' % octree_direct_name)
                    cmd = Oconv(output=output_direct,
                                inputs=scene_files_direct)
                    cmd.options.f = True
                    commands.append(cmd)

                    info['octree_direct'] = '%s.oct' % octree_direct_name

                # direct sun - don't add them for 3-phase
                if sun_path and study != 'three_phase':
                    scene_files_direct_sun = [sun_path] + scene_files_direct
                    octree_direct_sun_name = '%s_direct_sun' % state['identifier']
                    output_direct = \
                        os.path.join(output_folder, '%s.oct' %
                                     octree_direct_sun_name)
                    cmd = Oconv(output=output_direct,
                                inputs=scene_files_direct_sun)
                    cmd.options.f = True
                    commands.append(cmd)

                    info['octree_direct_sun'] = '%s.oct' % octree_direct_sun_name

                study_type.append(info)

                for cmd in commands:
                    env = None
                    if folders.env != {}:
                        env = folders.env
                    env = dict(os.environ, **env) if env else None
                    cmd.run(env=env, cwd=model_folder.folder)

            octree_mapping.append({study: study_type})
            octree_output = os.path.join(
                model_folder.folder, output_folder, '%s.json' % study
            )
            with open(octree_output, 'w') as fp:
                json.dump(study_type, fp, indent=2)

        octree_output = os.path.join(
            model_folder.folder, output_folder, 'multi_phase.json'
        )
        with open(octree_output, 'w') as fp:
            json.dump(octree_mapping, fp, indent=2)

    except Exception:
        _logger.exception('Failed to generate octrees.')
        sys.exit(1)
    else:
        sys.exit(0)
