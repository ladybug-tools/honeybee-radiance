"""Test cli multiphase module."""
import os
import json
from click.testing import CliRunner

from ladybug.futil import nukedir
from ladybug.commandutil import run_command_function
from honeybee.model import Model

from honeybee_radiance.cli.multiphase import view_matrix_command, \
    flux_transfer_command, aperture_group_cli, aperture_group


def test_view_matrix_command():
    runner = CliRunner()
    receiver_file = './tests/assets/multi_phase/class_room..receiver.rad'
    input_oct = './tests/assets/multi_phase/scene.oct'
    input_grid = './tests/assets/multi_phase/class_room.pts'
    output_folder = './tests/assets/temp'
    nukedir(output_folder)
    cmd_args = [
        receiver_file, input_oct, input_grid,
        '--sensor-count', '72',
        '--rad-params', '-ab 3 -ad 1000 -lw 1e-05'
    ]

    result = runner.invoke(view_matrix_command, cmd_args)
    assert result.exit_code == 0
    assert os.path.isfile(
        os.path.join(output_folder, 'east_window_classroom..class_room.vmx')
    )
    assert os.path.isfile(os.path.join(output_folder, 'skylight..class_room.vmx'))
    nukedir(output_folder)


def test_flux_transfer_command():
    runner = CliRunner()
    sender_file = './tests/assets/multi_phase/east_window_classroom..sender.rad'
    receiver_file = './tests/assets/multi_phase/rflux_sky.sky'
    input_oct = './tests/assets/multi_phase/scene.oct'
    output_folder = './tests/assets/temp'
    output = './tests/assets/temp/east_window_classroom.dmx'
    nukedir(output_folder)
    cmd_args = [
        sender_file, receiver_file, input_oct,
        '--rad-params', '-ab 1 -ad 100 -lw 1e-03 -c 100',
        '--output', output
    ]
    result = runner.invoke(flux_transfer_command, cmd_args)
    assert result.exit_code == 0
    assert os.path.isfile(output)
    assert os.path.getsize(output) > 0
    nukedir(output_folder)


def test_aperture_group_cli():
    runner = CliRunner()
    input_model = './tests/assets/model/two_rooms_no_grids.hbjson'
    output_folder = './tests/assets/multi_phase/test_aperture_group'
    result = runner.invoke(
        aperture_group_cli, [input_model, '--output-folder', output_folder])
    assert result.exit_code == 0
    model_dict = json.loads(result.output)
    new_model = Model.from_dict(model_dict)
    assert len(new_model.properties.radiance.dynamic_subface_groups) == 7
    nukedir(output_folder)


def test_aperture_group():
    input_model = './tests/assets/model/two_rooms_no_grids.hbjson'
    cmd_args = [input_model]
    model_str = run_command_function(aperture_group, cmd_args)
    model_dict = json.loads(model_str)
    new_model = Model.from_dict(model_dict)
    assert len(new_model.properties.radiance.dynamic_subface_groups) == 7