"""honeybee radiance view commands."""
import click
import sys
import os
import logging
import re
import json
import shutil

from ladybug.futil import write_to_file_by_name
from honeybee.model import Model
from honeybee_radiance_command.rpict import Rpict, RpictOptions
from honeybee_radiance_command.pcompos import Pcompos
from honeybee_radiance_command.pfilt import Pfilt
from honeybee_radiance_command.getinfo import Getinfo

from honeybee_radiance.view import View
from honeybee_radiance.config import folders

_logger = logging.getLogger(__name__)


@click.group(help='Commands for generating and modifying views.')
def view():
    pass


@view.command('split-count')
@click.argument(
    'view-info-file',
    type=click.Path(exists=True, file_okay=True, dir_okay=False, resolve_path=True)
)
@click.argument('cpu-count', type=int)
@click.option(
    '--output-file', '-f', help='Optional file to output the integer for the number '
    'of times to split the view. By default this will be printed to stdout',
    type=click.File('w'), default='-', show_default=True
)
def split_count_from_cpu_count(view_info_file, cpu_count, output_file):
    """Get the number of times to split each view in a model using a CPU count.

    Args:
        view_info_file: Input view info file.
        cpu_count: Number of processes that will be used to run
            the simulations in parallel.
    """
    try:
        with open(view_info_file) as inf:
            view_count = len(json.load(inf))
        opt_split = int(cpu_count / view_count)
        opt_split = 1 if opt_split == 0 else opt_split
        output_file.write(str(opt_split))
    except Exception:
        _logger.exception('Failed to compute the view split-count from cpu-count.')
        sys.exit(1)
    else:
        sys.exit(0)


@view.command('split')
@click.argument(
    'view', type=click.Path(
        exists=True, file_okay=True, dir_okay=False, resolve_path=True)
)
@click.argument('count', type=int)
@click.option(
    '--skip-overture/--overture', ' /-o', help='Flag to note whether an ambient '
    'file (.amb) should be generated for an overture calculation before the view is '
    'split into smaller views. The .amb file will have the same name as the view-file. '
    'With an overture calculation, the ambient file (aka ambient cache) is first '
    'populated with values. Thereby ensuring that - when reused to create an image - '
    'Radiance uses interpolation between already calculated values rather than less '
    'reliable extrapolation. The overture calculation has comparatively small '
    'computation time to full rendering but is single core can become time '
    'consuming in situations with very high numbers of rendering multiprocessors.',
    default=True, show_default=True
)
@click.option(
    '--resolution', '-r', default=None, type=int, show_default=True,
    help='An optional integer for the maximum dimension of the image in pixels. '
    'Specifying a value here will automatically lower the input --count to ensure '
    'the resulting images can be combined to meet this dimension. If unspecified, '
    'the --count will always be respected and the resulting images might not be '
    'combine-able to meet a specific target dimension.'
)
@click.option(
    '--octree', '-oct', help='Octree file for the overture calculation. This must be '
    'specified when the overture is not skipped.', default=None, show_default=True,
    type=click.Path(file_okay=True, dir_okay=False, resolve_path=True)
)
@click.option(
    '--rad-params', '-rp', help='Radiance parameters for the overture calculation. '
    'If unspecified, default rpict paramters will be used.'
)
@click.option(
    '--folder', '-f', help='Output folder.', default='.', show_default=True,
    type=click.Path(file_okay=False, dir_okay=True, resolve_path=True)
)
@click.option(
    '--log-file', '-log', help='Optional log file to output the name of the newly'
    ' created views. By default the list will be printed out to stdout',
    type=click.File('w'), default='-'
)
def split_view(view, count, resolution, skip_overture, octree, rad_params,
               folder, log_file):
    """Split a radiance view file into smaller views based on count.

    \b
    Args:
        view: Full path to input sensor view file.
        count: Maximum number of sensors in new files. The number will be rounded to
            closest round number for each file. For example if the input file has 21
            sensors and input count is set to 5 this command will generate 4 files where
            the first three files will have 5 sensors and the last file will have 6.
    """
    try:
        # correct the count to meet the target resolution
        if resolution is not None and resolution % count != 0:
            while resolution % count != 0:
                count =  count - 1

        # split the view into smaller views
        view_obj = View.from_file(view)
        views = view_obj.grid(y_div_count=count)
        views_info = []
        for c, v in enumerate(views):
            name = '%s_%04d' % (view_obj.identifier, c)
            path = '%s.vf' % name
            full_path = os.path.join(folder, path)
            v.to_file(folder, path, mkdir=True)
            views_info.append({
                'name': name,
                'path': path,
                'full_path': full_path
            })

        # create the ambient cache file if specified
        amb_file = os.path.join(folder, os.path.basename(view).replace('.vf', '.amb'))
        if not skip_overture:
            options = RpictOptions()
            if rad_params:
                options.update_from_string(rad_params.strip())
            # overwrite default image size to be small for the ambient cache (64 x 64)
            options.x = 64
            options.y = 64
            options.af = amb_file

            # create command and run it to get the .amb file
            assert octree is not None, \
                'Octree  must be specified for an overture calculation.'
            out_file = os.path.join(
                folder, os.path.basename(view).replace('.vf', '.unf'))
            rpict = Rpict(options=options, output=out_file, octree=octree, view=view)
            env = None
            if folders.env != {}:
                env = folders.env
            env = dict(os.environ, **env) if env else None
            rpict.run(env=env)
            os.remove(out_file)

        # record all of the view files that were generated
        log_file.write(json.dumps(views_info))
    except Exception:
        _logger.exception('Failed to split view file.')
        sys.exit(1)
    else:
        sys.exit(0)


@view.command('merge')
@click.argument('input-folder', type=click.Path(
    file_okay=False, dir_okay=True, resolve_path=True))
@click.argument('base-name', type=str)
@click.argument('extension', default='.unf', type=str)
@click.option('--view', '-vf', type=click.Path(
        exists=False, file_okay=True, dir_okay=False, resolve_path=True),
        help='Full path to the original view file.'
)
@click.option(
    '--scale-factor', '-s', default=1, type=float, show_default=True,
    help='A number that will be used to scale the dimensions of the output image '
    'as it is filtered for anti-aliasing.'
)
@click.option('--folder', '-f', help='Optional output folder.',
              default='.', show_default=True)
@click.option('--name', '-n', help='Optional output filename. Default is base-name.')
def merge_view(input_folder, base_name, extension, view, scale_factor, folder, name):
    """Merge several radiance HDR image files into a single file.

    This command will also perform an anti-aliasing operation on the output and
    replace the view information in the header of the merged file if a single .vf
    file is found within the root of the input-folder.

    \b
    Args:
        input_folder: Input folder.
        base_name: File base name. All of the files must start with base name and
            continue with _ and an integer values.
        extension: File extention. [Default: .unf]
    """
    try:
        # view is an optional input. Make sure we can handle the case that the view
        # file doesn't exist
        view = None if (view and not os.path.isfile(view)) else view

        # get all of the files in the folder with the given extension
        pattern = r'{}_\d+{}'.format(base_name, extension)
        images = sorted(f for f in os.listdir(input_folder) if re.match(pattern, f))
        if len(images) == 0:
            raise ValueError('Found no files to merge.')
        name = name or base_name

        # get the new dir name as view name might be group/name
        dirname = os.path.dirname(os.path.normpath(os.path.join(folder, name)))
        if dirname and not os.path.exists(dirname):
            os.makedirs(dirname)
        temp_output = os.path.join(dirname, name + '_temp.HDR')
        output_file = os.path.join(dirname, name + '.HDR')

        # set up the pcompos command
        in_dirname = os.path.normpath(input_folder)
        pcompos = Pcompos(output=temp_output)
        pcompos.input = [os.path.join(in_dirname, img) for img in images]
        pcompos.options.a = 1

        # setup the pfilt command to perform anti-aliasing on the output
        pfilt = Pfilt(input=temp_output)
        pfilt.options.r = 0.6
        if scale_factor != 1:
            pfilt.options.x = '/{}'.format(scale_factor)
            pfilt.options.y = '/{}'.format(scale_factor)

        # search for a single .vf in the folder and, if it's found, grab the info
        views = sorted(f for f in os.listdir(input_folder) if f.endswith('.vf'))
        if view and len(views) != 1:
            view_obj = View.from_file(view)
            getinfo = Getinfo(output=output_file)
            getinfo.options.a = 'VIEW= {}'.format(view_obj)
            pfilt.pipe_to = getinfo
        elif len(views) == 1:  # replace the header with the info in the view
            view_obj = View.from_file(os.path.join(input_folder, views[0]))
            getinfo = Getinfo(output=output_file)
            getinfo.options.a = 'VIEW= {}'.format(view_obj)
            pfilt.pipe_to = getinfo
        else:  # just let the output of pfilt be the final output
            pfilt.output = output_file

        # run the commands in series
        env = None
        if folders.env != {}:
            env = folders.env
        env = dict(os.environ, **env) if env else None
        pcompos.run(env)
        try:
            pfilt.run(env)
        except RuntimeError:  # the image was too bright or dark; just use pcompos output
            shutil.copyfile(temp_output, output_file)
    except Exception:
        _logger.exception('Failed to merge image files.')
        sys.exit(1)
    else:
        sys.exit(0)
