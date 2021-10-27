"""Test cli translate module."""
import os

from click.testing import CliRunner

from ladybug.futil import nukedir

from honeybee_radiance.cli.multiphase import view_matrix_command


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
