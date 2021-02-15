"""honeybee radiance daylight coefficient / contribution commands."""
import click
import sys
import logging


_logger = logging.getLogger(__name__)


@click.group(help='Commands to post-process Radiance results.')
def post_process():
    pass


@post_process.command('convert-to-binary')
@click.argument(
    'input-matrix', type=click.Path(exists=True, file_okay=True, resolve_path=True)
)
@click.option(
    '--output', '-o', help='Optional path to output file to output the name of the newly'
    ' created matrix. By default the list will be printed out to stdout',
    type=click.File('w'), default='-')
def convert_matrix_to_binary(input_matrix, output):
    """Postprocess a Radiance matrix and convert it to 0-1 values.

    \b
    This command is useful for translating Radiance results to outputs like sunlight
    hours. Input matrix must be in ASCII format. The header in the input file will be
    ignored.

    """
    try:
        with open(input_matrix) as inf:
            first_line = next(inf)
            if first_line[:10] == '#?RADIANCE':
                for line in inf:
                    if line[:7] == 'FORMAT=':
                        # pass next empty line
                        next(inf)
                        break
                    continue
            else:
                values = [
                    '0' if float(v) == 0 else '1' for v in first_line.split()
                ]
                output.write('\t'.join(values) + '\n')
            for line in inf:
                # write binary values to new file
                values = [
                    '0' if float(v) == 0 else '1' for v in line.split()
                ]
                output.write('\t'.join(values) + '\n')
    except Exception:
        _logger.exception('Failed to convert the input file to binary format.')
        sys.exit(1)
    else:
        sys.exit(0)


@post_process.command('sum-row')
@click.argument(
    'input-matrix', type=click.Path(exists=True, file_okay=True, resolve_path=True)
)
@click.option(
    '--output', '-o', help='Optional path to output file to output the name of the newly'
    ' created matrix. By default the list will be printed out to stdout',
    type=click.File('w'), default='-')
def sum_matrix_rows(input_matrix, output):
    """Postprocess a Radiance matrix and add all the numbers in each row.

    \b
    This command is useful for translating Radiance results to outputs like radiation
    to total radiation. Input matrix must be in ASCII format. The header in the input
    file will be ignored.

    """
    try:
        with open(input_matrix) as inf:
            first_line = next(inf)
            if first_line[:10] == '#?RADIANCE':
                for line in inf:
                    if line[:7] == 'FORMAT=':
                        # pass next empty line
                        next(inf)
                        break
                    continue
            else:
                value = sum(float(v) for v in first_line.split())
                output.write('%s\n' % value)
            for line in inf:
                # write sum to a new file
                value = sum(float(v) for v in line.split())
                output.write('%s\n' % value)
    except Exception:
        _logger.exception('Failed to convert the input file to binary format.')
        sys.exit(1)
    else:
        sys.exit(0)
