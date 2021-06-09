"""honeybee radiance rpict command."""
import click
import sys
import logging
import os
import shutil

from honeybee_radiance.config import folders
from honeybee_radiance_command.rpict import Rpict, RpictOptions


_logger = logging.getLogger(__name__)


@click.group(help='Commands to run rpict in Radiance.')
def rpict():
    pass


@rpict.command('rpict')
@click.argument(
    'octree', type=click.Path(exists=True, file_okay=True, resolve_path=True)
)
@click.argument(
    'view', type=click.Path(exists=True, file_okay=True, resolve_path=True)
)
@click.option(
    '--rad-params', help='Radiance parameters.'
)
@click.option(
    '--rad-params-locked', help='Protected Radiance parameters. These values will '
    'overwrite user input rad parameters.'
)
@click.option(
    '--metric', '-m', default='luminance', show_default=True,
    help='Text for the type of metric to be output from the calculation. Choose from: '
    'illuminance, irradiance, luminance, radiance.'
)
@click.option(
    '--resolution', '-r', default=None, type=int, show_default=True,
    help='An integer for the maximum dimension of the image in pixels (either '
    'width/height depending on the input view angle and type). This will '
    'overwrite the -x and -y option in any input radiance parameters if specified. '
    'The default value for Radiance is 512 pixels.'
)
@click.option(
    '--scale-factor', '-s', default=1, type=float, show_default=True,
    help='A number that will be multiplied by the input resolution to scale the '
    'dimensions of the output image. This is useful in workflows if one plans to '
    're-scale the image after the ray tracing calculation to improve anti-aliasing.'
)
@click.option(
    '--output', '-o', help='Path to output file. If a relative path is provided it '
    'should be relative to project folder.'
)
@click.option(
    '--dry-run', is_flag=True, default=False, show_default=True,
    help='A flag to show the command without running it.'
)
def rpict_command(
        octree, view, rad_params, rad_params_locked, metric, resolution, scale_factor,
        output, dry_run):
    """Run rpict command for an input octree and a view file.

    Note that, if an ambient cache file (.amb) is found next to the view file,
    and it is determined to be valid (with a non-zero size) it will be
    automatically used within the rpict command.

    \b
    Args:
        octree: Path to octree file.
        view: Path to view file.

    """
    try:
        options = RpictOptions()
        # parse input radiance parameters
        if rad_params:
            options.update_from_string(rad_params.strip())
        # overwrite input values with protected ones
        if rad_params_locked:
            options.update_from_string(rad_params_locked.strip())
        # overwrite the -i attribute depending on the metric to be calculated
        if metric in ('illuminance', 'irradiance'):
            options.i = True
        elif metric in ('luminance', 'radiance'):
            options.i = False
        else:
            raise ValueError('Metric "{}" is not recognized.'.format(metric))
        # overwrite the -x and -y attribute depending on the input resolution
        if resolution:
            options.x = int(resolution * scale_factor)
            options.y = int(resolution * scale_factor)
        # sense wether there is an ambient cache file next to the view
        for base_file in os.listdir(os.path.dirname(view)):
            if base_file.endswith('.amb'):
                full_amb_path = os.path.join(os.path.dirname(view), base_file)
                if os.stat(full_amb_path).st_size != 0:
                    options.af = os.path.join(os.path.dirname(view), base_file)
                    break

        # write the metric type into the view name such that it's in the HDR header
        metric_view = os.path.basename(view).replace('.vf', '_{}.vf'.format(metric))
        full_metric_view = os.path.join(os.path.dirname(view), metric_view)
        shutil.copyfile(view, full_metric_view)

        # create command.
        rpict = Rpict(
            options=options, output=output, octree=octree, view=full_metric_view
        )

        if dry_run:
            click.echo(rpict)
        else:
            env = None
            if folders.env != {}:
                env = folders.env
            env = dict(os.environ, **env) if env else None
            rpict.run(env=env)
        os.remove(full_metric_view)
    except Exception:
        _logger.exception('Failed to run rpict command.')
        sys.exit(1)
    else:
        sys.exit(0)
