"""Test cli postprocess module."""
import os
import json

from click.testing import CliRunner

from ladybug.futil import nukedir

from honeybee_radiance.cli.postprocess import annual_irradiance, leed_illuminance


def test_annual_irradiance():
    runner = CliRunner()
    input_folder = './tests/assets/irrad_result'
    wea_file = './tests/assets/wea/denver.wea'
    sub_folder = 'metrics'
    result_dir = os.path.join(input_folder, sub_folder)
    cmd_args = [input_folder, wea_file, '--sub-folder', sub_folder]

    result = runner.invoke(annual_irradiance, cmd_args)
    assert result.exit_code == 0
    assert os.path.isdir(result_dir)
    nukedir(result_dir, rmdir=True)


def test_leed_illuminance():
    runner = CliRunner()
    input_folder = './tests/assets/leed'
    sub_folder = 'pass_fail'
    result_dir = os.path.join(input_folder, sub_folder)
    cmd_args = [input_folder, '--sub-folder', sub_folder]

    result = runner.invoke(leed_illuminance, cmd_args)
    assert result.exit_code == 0
    assert os.path.isdir(result_dir)
    result_dict = json.loads(result.output)
    assert round(result_dict['percentage_passing']) == 24
    nukedir(result_dir, rmdir=True)
