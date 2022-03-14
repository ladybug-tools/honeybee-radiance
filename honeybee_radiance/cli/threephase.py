import os

import click
import sys
import logging
import json

from honeybee_radiance_command.dctimestep import Dctimestep, DctimestepOptions
from honeybee_radiance_command.rmtxop import Rmtxop, RmtxopOptions
from honeybee_radiance_command.getinfo import Getinfo, GetinfoOptions
from honeybee_radiance.config import folders
from honeybee_radiance_command._command_util import run_command

_logger = logging.getLogger(__name__)


@click.group(help='Commands to do matrix operations for three-phase.')
def three_phase():
    pass


@three_phase.command('multiplication')
@click.argument(
    'sky-vector', type=click.Path(exists=True, dir_okay=False, resolve_path=True))
@click.argument(
    'view-matrix', type=click.Path(exists=True, dir_okay=False, resolve_path=True))
@click.argument(
    't-matrix', type=click.Path(exists=True, dir_okay=False, resolve_path=True))
@click.argument(
    'daylight-matrix', type=click.Path(exists=True, dir_okay=False, resolve_path=True))
@click.argument(
    'output-matrix',
    type=click.Path(
        exists=False, file_okay=True, dir_okay=False, resolve_path=True
    ),
)
@click.option(
    '--options', help='a string that will be passed to dctimestep for setting options '
    'such as output file format (-o), input data format(-i) etc.')
@click.option(
    '--dry-run', is_flag=True, default=False, show_default=True,
    help='A flag to show the command without running it.'
)
def three_phase_calc(sky_vector, view_matrix, t_matrix, daylight_matrix, output_matrix,
                     options, dry_run):
    """Matrix multiplication for view matrix, transmission matrix, daylight matrix and
    sky matrix."""

    try:
        base_options = DctimestepOptions()
        options = options.strip() if options else None
        if options:
            base_options.update_from_string(options)

        cmd = Dctimestep.three_phase_calc(sky_vector=sky_vector, view_matrix=view_matrix,
                                          t_matrix=t_matrix,
                                          daylight_matrix=daylight_matrix,
                                          output=output_matrix, options=base_options)
        if dry_run:
            click.echo(cmd)
        else:
            run_command(cmd.to_radiance(), env=folders.env)
    except OSError:
        os.system(cmd.to_radiance())
    except Exception:
        _logger.exception('Failed to run matrix multiplication calculations with '
                          'dctimestep')
        sys.exit(1)
    else:
        sys.exit(0)


@three_phase.command('rmtxop')
@click.argument(
    'view-matrix', type=click.Path(exists=True, dir_okay=False, resolve_path=True))
@click.argument(
    't-matrix', type=click.Path(exists=True, dir_okay=False, resolve_path=True))
@click.argument(
    'daylight-matrix', type=click.Path(exists=True, dir_okay=False, resolve_path=True))
@click.argument(
    'sky-vector', type=click.Path(exists=True, dir_okay=False, resolve_path=True))
@click.argument(
    'output-matrix',
    type=click.Path(
        exists=False, file_okay=True, dir_okay=False, resolve_path=True
    ),
)
@click.option(
    '--output-format', help='Output format for output matrix. Valid inputs are a, f, d '
    'and c for ASCII, float, double or RGBE colors. If conversion is not provided you '
    'can change the output type using rad-params options.',
    type=click.Choice(['a', 'f', 'd', 'c']), default='a', show_default=True,
    show_choices=True
)
@click.option(
    '--illuminance/--raw', is_flag=True, default=True, show_default=True,
    help='A flag to convert the result to illuminance.'
)
@click.option(
    '--remove-header/--keep-header', is_flag=True, default=True,
    help='A flag to keep or remove the header from the output file.'
)
@click.option(
    '--dry-run', is_flag=True, default=False, show_default=True,
    help='A flag to show the command without running it.'
)
def three_phase_rmtxop(
    view_matrix, t_matrix, daylight_matrix, sky_vector, output_matrix, output_format,
    illuminance, remove_header, dry_run
):
    """Matrix multiplication for view matrix, transmission matrix, daylight matrix and
    sky matrix."""

    try:
        options = RmtxopOptions()
        options.f = output_format
        matrices = [view_matrix, t_matrix, daylight_matrix, sky_vector]

        if illuminance:
            # rmtxop concatenation
            calc = Rmtxop(matrices=matrices)

            cmd = Rmtxop(options=options)
            cmd.transforms = [['47.4', '119.9', '11.6']]
            cmd.matrices = calc
        else:
            cmd = Rmtxop(options=options, matrices=matrices)

        if remove_header:
            getinfo = Getinfo.remove_header(output=output_matrix)
            cmd.pipe_to = getinfo
        else:
            cmd.output = output_matrix

        if dry_run:
            click.echo(cmd)
        else:
            run_command(cmd.to_radiance(), env=folders.env)
    except OSError:
        os.system(cmd.to_radiance())
    except Exception:
        _logger.exception(
            'Failed to run matrix multiplication calculations with rmtxop')
        sys.exit(1)
    else:
        sys.exit(0)


@three_phase.command('combinations')
@click.argument(
    'sender-info', type=click.Path(exists=True, dir_okay=False, resolve_path=True))
@click.argument(
    'receiver-info', type=click.Path(exists=True, dir_okay=False, resolve_path=True))
@click.argument(
    'states_info', type=click.Path(exists=True, dir_okay=False, resolve_path=True))
@click.option(
    '--folder',
    help='Path to target folder. The command will create two JSON files in this folder.',
    type=click.Path(exists=False, file_okay=False, dir_okay=True, resolve_path=True),
    default='.', show_default=True
)
@click.option(
    '--combinations-name', '-cn', help='Output file name for 3 phase multiplication '
    'combinations.', type=click.STRING, default='3phase_multiplication_info',
    show_default=True
)
@click.option(
    '--result-mapper-name', '-rn', help='Output file name for results mapper file.',
    type=click.STRING, default='3phase_results_info', show_default=True
)
def three_phase_combinations(
    sender_info, receiver_info, states_info, folder, combinations_name,
    result_mapper_name
):
    """Matrix multiplication for view matrix, transmission matrix, daylight matrix and
    sky matrix.

    \b
    args:
        sender_info: A JSON file that includes the information for senders. This file
            is created as an output of the daylight matrix grouping command.
        receiver_info: A JSON file that includes the information for receivers. This
            file is written to model/receiver folder.
        states_info: A JSON file that includes the state information for all the
            aperture groups. This file is created under model/aperture_groups.

    """
    def _read_json_content(json_file):
        with open(json_file) as inf:
            return json.loads(inf.read())
    try:
        rec_data = _read_json_content(receiver_info)
        send_data = _read_json_content(sender_info)
        states = _read_json_content(states_info)

        dmtx_info = {}

        grid_mapper = {}
        for grid in rec_data:
            grid_mapper[grid['identifier']] = {}
            for apt in grid['aperture_groups']:
                for group in send_data:
                    if apt in group['aperture_groups']:
                        dmtx_info[apt] = group['identifier']
                        break
                else:
                    # this should never happen for a valid radiance folder
                    raise ValueError('Unrecognizable aperture group: %s' % apt)

                grid_mapper[grid['identifier']][apt] = \
                    [s['identifier'] for s in states[apt]]

        # create all the possible combinations
        # TODO: find a more generic approach to created the names. Using white_glow
        # is assuming that we will never change the modifier.
        matrix_combinations = []
        for grid in rec_data:
            for apt in grid['aperture_groups']:
                vmtx = '%s..white_glow_%s.vtmx' % (grid['identifier'], apt)
                dmtx = '%s.dmtx' % dmtx_info[apt]
                for info in states[apt]:
                    matrix_combinations.append(
                        dict(
                            # create an identifier from the mix of grid and state
                            identifier='%s..%s' % (
                                grid['identifier'], info['identifier']
                            ),
                            grid_id = grid['identifier'],
                            state_id = info['identifier'],
                            tmtx=info['tmtx'],
                            vmtx=vmtx,
                            dmtx=dmtx
                        )
                    )

        # write the files to folder
        if not os.path.isdir(folder):
            os.mkdir(folder)

        comb_file = os.path.join(folder, '%s.json' % combinations_name)
        res_file = os.path.join(folder, '%s.json' % result_mapper_name)

        with open(comb_file, 'w') as outf:
            json.dump(matrix_combinations, outf, indent=2)

        with open(res_file, 'w') as outf:
            json.dump(grid_mapper, outf, indent=2)

    except Exception:
        _logger.exception(
            'Failed to calculate the mapper file for 3 phase studies.')
        sys.exit(1)
    else:
        sys.exit(0)
