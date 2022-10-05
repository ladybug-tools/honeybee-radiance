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
@click.argument('folder', type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option(
    '--output', '-o', show_default=True, help='Path to output file (.oct). If a relative path'
    ' is provided it should be relative to project folder.'
)
@click.option(
    '--default/--black', ' /-b', default=True, show_default=True,
    help='Flag to note whether the octree should be created completely with '
    'black materials.'
)
@click.option(
    '--include-aperture/--exclude-aperture', ' /-xa', default=True,
    show_default=True,
    help='Flag to note whether static apertures should be included in the octree.'
)
@click.option(
    '--black-groups/--exclude-groups', ' /-xg', default=True, show_default=True,
    help='Flag to note whether dynamic aperture groups should blacked-out in '
    'the octree or they should simply be excluded, letting light pass through.'
)
@click.option(
    '--first-shade-state/--exclude-shade-groups', ' /-xs', help='Flag to note whether '
    'dynamic shade groups should be included in the octree as the first shade state '
    'or they should simply be excluded.', default=True, show_default=True
)
@click.option(
    '--include-ies/--exclude-ies', ' /-xi', default=True,
    show_default=True,
    help='Flag to note whether IES files should be included in the octree.'
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
    folder, output, default, include_aperture, black_groups, first_shade_state,
    include_ies, add_before, add_after, dry_run
):
    """Generate a static octree from a folder.

    \b
    Args:
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
            except Exception:
                pass  # no apertures available in the model
        if black_groups:
            try:
                group_files = model_folder.aperture_group_files_black()
                scene_files += group_files
            except Exception:
                pass  # no aperture groups available in the model
        if first_shade_state:
            try:
                dyn_folder = model_folder.dynamic_scene_folder(full=True)
                dyn_shades = model_folder.dynamic_scene()
                shd_g_files = [os.path.join(dyn_folder, grp.states[0].default)
                               for grp in dyn_shades]
                scene_files += shd_g_files
            except Exception:
                pass  # no shade groups available in the model
        if include_ies:
            try:
                ies_folder = model_folder.ies_folder()
                for fp in os.listdir(ies_folder):
                    if fp.endswith('rad'):
                        scene_files += os.path.join(ies_folder, fp)
            except Exception:
                pass  # no aperture groups available in the model
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
@click.argument('folder', type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option(
    '--sun-path',
    type=click.Path(exists=True, file_okay=True, dir_okay=False, resolve_path=True),
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

    \b
    Args:
        folder: Path to a Radiance model folder.
    """
    model_folder = ModelFolder.from_model_folder(folder)

    # check if sunpath file exist - otherwise continue without it
    if sun_path and not os.path.isfile(sun_path):
        sun_path = None

    if phase == '5' and not sun_path:
        raise RuntimeError(
            'To generate octrees for a 5 Phase study you must provide a sunpath.'
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
                info, commands = _generate_octrees_info(
                    state, output_folder, study, sun_path)
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


@octree.command('from-abstracted-groups')
@click.argument('folder', type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option(
    '--sun-path', '-sp',
    type=click.Path(exists=True, file_okay=True, dir_okay=False, resolve_path=True),
    default=None, show_default=True,
    help='Path for a sun-path file that will be added to octrees for direct sunlight '
    'studies. If sunpath is provided an extra octree for direct_sun will be created.'
)
@click.option('--output-folder', help='Output folder relative to the model folder into '
              'which the files be written.', default='octree', show_default=True)
def create_octree_from_abstracted_groups(folder, sun_path, output_folder):
    """Generate a set of octrees from a folder containing abstracted aperture groups.

    This command assumes that each aperture group in the radiance folder contains
    only two states. The first is a 100 percent transmittance specular (or beam)
    representation of the aperture group and the second is a 100 percent transmittance
    diffuse representation of the aperture group. This abstracted representation is
    intended to simulate contributions of dynamic groups when an external source
    is able to provide specular and diffuse transmittances at each timestep.
    For example, EnergyPlus can provide such values, which together can account
    for several types of complex dynamic fenestration types.

    Each aperture group will get at least two octrees (one with specular and one
    with diffuse). If a sun-path is provided, a third octree will be added with
    the suns included.

    \b
    Args:
        folder: Path to a Radiance model folder.
    """
    model_folder = ModelFolder.from_model_folder(folder)
    try:
        # first, check to see if there are any aperture groups in the model
        output_folder = os.path.join(model_folder.folder, output_folder)
        if not os.path.isdir(output_folder):
            os.mkdir(output_folder)
        group_info_file = os.path.join(output_folder, 'group_info.json')
        group_info, groups_exist = [], True
        try:
            grp_folder = model_folder.aperture_group_folder()
            ap_groups = model_folder.aperture_groups()
            if len(ap_groups) == 0:
                groups_exist = False
        except Exception:
            groups_exist = False

        if groups_exist:
            # get the static scene files with blacked-out apertures
            scene_files = model_folder.scene_files(black_out=False)
            try:
                aperture_files = model_folder.aperture_files(black_out=True)
                scene_files += aperture_files
            except Exception:
                pass  # no apertures available in the model

            # get the environment variables
            env = None
            if folders.env != {}:
                env = folders.env
            env = dict(os.environ, **env) if env else None

            # loop through the aperture groups and create the octrees
            for i, a_grp in enumerate(ap_groups):
                # create a sub-folder and get black versions of all other aperture groups
                sub_folder = os.path.join(output_folder, a_grp.identifier)
                if not os.path.isdir(sub_folder):
                    os.mkdir(sub_folder)
                blk_grp = [_model_rel(grp_folder, ag.states[0].black)
                           for j, ag in enumerate(ap_groups) if j != i]
                blk_grp = [bg.replace('\\', '/') for bg in blk_grp]
                grp_scene_files = scene_files + blk_grp
                # command for the octree for specular transmittance
                spec_file = os.path.join(sub_folder, 'spec.oct')
                spec_scene_files = grp_scene_files + \
                    [_model_rel(grp_folder, a_grp.states[0].default)]
                cmd_s = Oconv(output=spec_file, inputs=spec_scene_files)
                # command for the octree for diffuse transmittance
                diff_file = os.path.join(sub_folder, 'diff.oct')
                diff_scene_files = grp_scene_files + \
                    [_model_rel(grp_folder, a_grp.states[1].default)]
                cmd_d = Oconv(output=diff_file, inputs=diff_scene_files)
                cmds = [cmd_s, cmd_d]
                # add info about the generated files
                grp_info_dict = {
                    'identifier': a_grp.identifier,
                    'spec': os.path.basename(spec_file),
                    'diff': os.path.basename(diff_file)
                }
                # command for the octree with suns
                if sun_path and os.path.isfile(sun_path):
                    spec_sun_file = os.path.join(sub_folder, 'spec_sun.oct')
                    spec_sun_scene_files = [sun_path] + spec_scene_files
                    cmd_ss = Oconv(output=spec_sun_file, inputs=spec_sun_scene_files)
                    cmds.append(cmd_ss)
                    grp_info_dict['sun'] = os.path.basename(spec_sun_file)
                # run all of the commands to create the octrees
                for cmd in cmds:
                    cmd.options.f = True
                    cmd.run(env=env, cwd=model_folder.folder)
                group_info.append(grp_info_dict)

        # write out a JSON with information about the octrees and groups
        with open(group_info_file, 'w') as fp:
            json.dump(group_info, fp, indent=2)
    except Exception:
        _logger.exception('Failed to generate abstracted group octrees.')
        sys.exit(1)
    else:
        sys.exit(0)


@octree.command('from-shade-trans-groups')
@click.argument('folder', type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option(
    '--sun-path', '-sp',
    type=click.Path(exists=True, file_okay=True, dir_okay=False, resolve_path=True),
    default=None, show_default=True,
    help='Path for a sun-path file that will be added to octrees for direct sunlight '
    'studies. If sunpath is provided an extra octree for direct_sun will be created.'
)
@click.option('--output-folder', help='Output folder relative to the model folder into '
              'which the files be written.', default='octree', show_default=True)
def create_octree_from_shade_trans_groups(folder, sun_path, output_folder):
    """Generate a set of octrees from a folder containing shade transmittance groups.

    This command assumes that each shade group in the radiance folder contains
    only two states. The first is a completely opaque representation of the shade
    group and the second is a completely transparent representation of the shade
    group. This abstracted representation is intended to simulate dynamic shade
    transmittance that changes at each timestep.

    Each shade group will get an octree. If a sun-path is provided, an additional
    octree will be added for each group.

    \b
    Args:
        folder: Path to a Radiance model folder.
    """
    model_folder = ModelFolder.from_model_folder(folder)
    try:
        # first, check to see if there are any shade groups in the model
        output_folder = os.path.join(model_folder.folder, output_folder)
        if not os.path.isdir(output_folder):
            os.mkdir(output_folder)
        group_info_file = os.path.join(output_folder, 'trans_info.json')
        group_info, groups_exist = [], True
        try:
            grp_folder = model_folder.dynamic_scene_folder()
            shd_groups = model_folder.dynamic_scene()
            if len(shd_groups) == 0:
                groups_exist = False
        except Exception:
            groups_exist = False

        if groups_exist:
            # get the static scene files
            scene_files = model_folder.scene_files(black_out=False)
            try:
                aperture_files = model_folder.aperture_files(black_out=False)
                scene_files += aperture_files
            except Exception:
                pass  # no apertures available in the model

            # get the environment variables
            env = None
            if folders.env != {}:
                env = folders.env
            env = dict(os.environ, **env) if env else None

            # loop through the shade groups and create the octrees
            for i, s_grp in enumerate(shd_groups):
                # gather files to represent the transparent shade group
                dyn_grp = [_model_rel(grp_folder, sg.states[0].default)
                           for j, sg in enumerate(shd_groups) if j != i]
                dyn_grp = [sg.replace('\\', '/') for sg in dyn_grp]
                grp_scene_files = scene_files + dyn_grp
                oct_file = os.path.join(output_folder, '{}.oct'.format(s_grp.identifier))
                # command for the octree
                cmds = [Oconv(output=oct_file, inputs=grp_scene_files)]
                # add info about the generated files
                grp_info_dict = {
                    'identifier': s_grp.identifier,
                    'default': os.path.basename(oct_file)
                }
                # command for the octree with suns
                if sun_path and os.path.isfile(sun_path):
                    sun_file = os.path.join(
                        output_folder, '{}_sun.oct'.format(s_grp.identifier))
                    sun_scene_files = [sun_path] + grp_scene_files
                    cmd_ss = Oconv(output=sun_file, inputs=sun_scene_files)
                    cmds.append(cmd_ss)
                    grp_info_dict['sun'] = os.path.basename(sun_file)
                # run all of the commands to create the octrees
                for cmd in cmds:
                    cmd.options.f = True
                    cmd.run(env=env, cwd=model_folder.folder)
                group_info.append(grp_info_dict)

        # write out a JSON with information about the octrees and groups
        with open(group_info_file, 'w') as fp:
            json.dump(group_info, fp, indent=2)
    except Exception:
        _logger.exception('Failed to generate shade trans group octrees.')
        sys.exit(1)
    else:
        sys.exit(0)


def _model_rel(folder, rel_file):
    """Get a file path relative to a model folder."""
    return os.path.join(folder, os.path.normpath(rel_file)).replace('\\', '/')


def _generate_octrees_info(state, output_folder='octree', study='two_phase',
                           sun_path=None):
    """Get octree information for default, direct, and direct sun. The functions also
    generates the Radiance commands (oconv) for creating the octrees.

    Example of valid argument 'state':
    {
        'light_path': '__static_apertures__',
        'identifier': '__static_apertures__',
        'scene_files': ['model/scene/envelope.mat', 'model/scene/envelope.rad'],
        'scene_files_direct': ['model/scene/envelope.mat', 'model/scene/envelope.rad'],
        'scene_files_direct': ['model/scene/envelope.mat', 'model/scene/envelope.rad'],
    }

    Args:
        state: A state as a dictionary with information about which files to include in
            each octree.
        output_folder: Folder name to where the octrees will we generated.
        study: A string of the study. There are either 'two_phase', 'three_phase', or
            'five_phase'.
        sun_path: Path for a sun-path file that will be added to octrees for direct
            sunlight studies. If sunpath is provided an extra octree for direct_sun
            will be created.

    Returns:
        Two elements:
            - octree information as dictionary
            - oconv commands as a list
    """
    commands = []
    info = {
        'identifier': state['identifier'],
        'light_path': state['light_path']}

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
        scene_files_direct = state['scene_files_direct']
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

    return info, commands
