"""Test cli view module."""
import os
from click.testing import CliRunner

from ladybug.futil import nukedir

from honeybee_radiance.cli.viewfactor import create_view_factor_modifiers, \
    rcontrib_command_with_view_postprocess


def test_view_factor():
    runner = CliRunner()
    input_model = './tests/assets/view_factor/model.hbjson'
    input_grid = './tests/assets/view_factor/TestRoom_1.pts'
    output_folder = './tests/assets/view_factor/results/'
    cmd_args = [input_model, '--include-sky', '--grouped-shades',
                '--folder', output_folder]
    result = runner.invoke(create_view_factor_modifiers, cmd_args)
    print(result.output)
    assert result.exit_code == 0

    oct_file = os.path.join(output_folder, 'scene.oct')
    mod_file = os.path.join(output_folder, 'scene.mod')
    assert os.path.isfile(oct_file)
    assert os.path.isfile(mod_file)

    cmd_args = [oct_file, input_grid, mod_file, '--folder', output_folder]
    result = runner.invoke(rcontrib_command_with_view_postprocess, cmd_args)
    assert result.exit_code == 0
    vf_file = os.path.join(output_folder, 'view_factor.csv')
    assert os.path.isfile(vf_file)

    nukedir(output_folder, rmdir=True)
