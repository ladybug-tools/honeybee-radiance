"""Commands to work with Radiance matrix using rmtxopt and rcollate."""
import click
import sys
import os
import logging

from honeybee_radiance.config import folders
from honeybee_radiance_command._command_util import run_command

from .util import handle_operator


_logger = logging.getLogger(__name__)


@click.group(help='Commands to work with Radiance matrix using rmtxop.')
def mtxop():
    pass


@mtxop.command('operate-two')
@click.argument(
    'first-mtx', type=click.Path(exists=True, dir_okay=False, resolve_path=True)
)
@click.argument(
    'second-mtx', type=click.Path(exists=True, dir_okay=False, resolve_path=True)
)
@click.option(
    '--operator', type=click.Choice(['+', '-', '/', '*']), default='+',
    help='operation between the two matrices.'
)
@click.option(
    '--keep-header/--remove-header', is_flag=True, default=True,
    help='A flag to keep or remove the header from the output file.'
)
@click.option(
    '--conversion', help='conversion as a string which will be passed to rmtxop -c. '
    'This option is useful to post-process the results from 3 RGB components into one '
    'as part of this command.'
)
@click.option(
    '--output-mtx',
    type=click.Path(
        exists=False, file_okay=True, dir_okay=False, resolve_path=True
    ),
    help='Output matrix.'
)
@click.option(
    '--output-format', help='Output format for output matrix. Valid inputs are a, f, d '
    'and c for ASCII, float, double or RGBE colors. If conversion is not provided you '
    'can change the output type using rad-params options.',
    type=click.Choice(['a', 'f', 'd', 'c']), default='a', show_default=True,
    show_choices=True
)
@click.option(
    '--dry-run', is_flag=True, default=False, show_default=True,
    help='A flag to show the command without running it.'
)
def two_matrix_operations(
    first_mtx, second_mtx, operator, keep_header, conversion, output_mtx,
    output_format, dry_run
):
    """Operations between two Radiance matrices.

    \b
    Args:
        first-mtx: Path to fist matrix.
        second-mtx: Path to second matrix.
    """
    try:
        # first check to be sure there are sun-up hours; if so, write a blank file
        if os.path.getsize(first_mtx) == 0 or os.path.getsize(second_mtx) == 0:
            if output_mtx is not None:
                with open(output_mtx, 'w') as wf:
                    wf.write('')
            return

        cmd = 'rmtxop -f{output_format} "{first_mtx}" {operator} "{second_mtx}"'.format(
            output_format=output_format, first_mtx=first_mtx,
            operator=handle_operator(operator), second_mtx=second_mtx
        )

        if conversion and conversion.strip():
            cmd = cmd + ' -c {conversion}'.format(conversion=conversion)

        if not keep_header:
            cmd = cmd + ' | getinfo - '
        if output_mtx:
            cmd = cmd + ' > "%s"' % output_mtx
        if dry_run:
            click.echo(cmd)
            sys.exit(0)

        run_command(cmd, env=folders.env)
    except Exception:
        _logger.exception('Operation on two Radiance matrix failed.')
        sys.exit(1)
    else:
        sys.exit(0)


@mtxop.command('operate-three')
@click.argument(
    'first-mtx', type=click.Path(exists=True, dir_okay=False, resolve_path=True)
)
@click.argument(
    'second-mtx', type=click.Path(exists=True, dir_okay=False, resolve_path=True)
)
@click.argument(
    'third-mtx', type=click.Path(exists=True, dir_okay=False, resolve_path=True)
)
@click.option(
    '--operator-one', type=click.Choice(['+', '-', '/', '*']), default='+',
    help='operation between the two matrices.'
)
@click.option(
    '--operator-two', type=click.Choice(['+', '-', '/', '*']), default='+',
    help='operation between the two matrices.'
)
@click.option(
    '--keep-header/--remove-header', is_flag=True, default=True,
    help='A flag to keep or remove the header from the output file.'
)
@click.option(
    '--conversion', help='conversion as a string which will be passed to rmtxop -c. '
    'This option is useful to post-process the results from 3 RGB components into one '
    'as part of this command.'
)
@click.option(
    '--output-mtx',
    type=click.Path(
        exists=False, file_okay=True, dir_okay=False, resolve_path=True
    ),
    help='Output matrix.'
)
@click.option(
    '--output-format', help='Output format for output matrix. Valid inputs are a, f, d '
    'and c for ASCII, float, double or RGBE colors. If conversion is not provided you '
    'can change the output type using rad-params options.',
    type=click.Choice(['a', 'f', 'd', 'c']), default='a', show_default=True,
    show_choices=True
)
@click.option(
    '--dry-run', is_flag=True, default=False, show_default=True,
    help='A flag to show the command without running it.'
)
def three_matrix_operations(
    first_mtx, second_mtx, third_mtx, operator_one, operator_two, keep_header,
    conversion, output_mtx, output_format, dry_run
        ):
    """Operations between two Radiance matrices.

    \b
    Args:
        first-mtx: Path to fist matrix.
        second-mtx: Path to second matrix.
        third-mtx: Path to third matrix.
    """
    try:
        # first check to be sure there are sun-up hours; if so, write a blank file
        if os.path.getsize(first_mtx) == 0 or os.path.getsize(second_mtx) == 0 \
                or os.path.getsize(third_mtx) == 0:
            if output_mtx is not None:
                with open(output_mtx, 'w') as wf:
                    wf.write('')
            return

        cmd = 'rmtxop -f{output_format} "{first_mtx}" {operator_one} "{second_mtx}" ' \
            ' {operator_two} "{third_mtx}"'.format(
                output_format=output_format, first_mtx=first_mtx,
                operator_one=handle_operator(operator_one), second_mtx=second_mtx,
                operator_two=handle_operator(operator_two), third_mtx=third_mtx
            )

        if conversion and conversion.strip():
            cmd = cmd + ' -c {conversion}'.format(conversion=conversion)

        if not keep_header:
            cmd = cmd + ' | getinfo - '

        if output_mtx:
            cmd = cmd + ' > "%s"' % output_mtx

        if dry_run:
            click.echo(cmd)
            sys.exit(0)

        run_command(cmd, env=folders.env)
    except Exception:
        _logger.exception('Operation on three Radiance matrix failed.')
        sys.exit(1)
    else:
        sys.exit(0)


@mtxop.command('transpose')
@click.argument(
    'input-mtx', type=click.Path(exists=True, dir_okay=False, resolve_path=True)
)
@click.option('--output-mtx', type=click.Path(
        exists=False, file_okay=True, dir_okay=False, resolve_path=True
    ), help='Output matrix.')
@click.option(
    '--dry-run', is_flag=True, default=False, show_default=True,
    help='A flag to show the command without running it.'
)
def transpose_mtx(input_mtx, output_mtx, dry_run):
    """Transpose a Radiance matrix.

    \b
    Args:
        input_mtx: Path to input matrix file.
    """
    try:
        cmd = 'rcollate -t "%s" ' % input_mtx
        if output_mtx:
            cmd = cmd + ' > "%s"' % output_mtx
        if dry_run:
            click.echo(cmd)
            sys.exit(0)
        run_command(cmd, env=folders.env)
    except Exception:
        _logger.exception('Matrix transpose command failed.')
        sys.exit(1)
    else:
        sys.exit(0)
