"""Test cli postprocess module."""
import os
import json

from click.testing import CliRunner

from ladybug.futil import nukedir

from honeybee_radiance.cli.postprocess import annual_irradiance, leed_illuminance, \
    daylight_fatcor_config, point_in_time_config, cumulative_radiation_config, \
    direct_sun_hours_config, sky_view_config


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


def test_df_config():
    runner = CliRunner()
    cfg_file = 'tests/assets/temp/df_config.json'
    cmd_args = ['-o', cfg_file, '-f', 'results']

    result = runner.invoke(daylight_fatcor_config, cmd_args)
    assert result.exit_code == 0
    assert os.path.isfile(cfg_file)
    with open(cfg_file) as inf:
        result_dict = json.load(inf)
    assert result_dict['data'][0]['path'] == 'results'
    os.unlink(cfg_file)


def test_point_in_time_config():
    runner = CliRunner()
    cfg_file = 'tests/assets/temp/pit_config.json'
    cmd_args = ['-o', cfg_file, '-f', 'results']

    result = runner.invoke(point_in_time_config, cmd_args)
    assert result.exit_code == 0
    assert os.path.isfile(cfg_file)
    with open(cfg_file) as inf:
        result_dict = json.load(inf)
    assert result_dict['data'][0]['path'] == 'results'
    os.unlink(cfg_file)


def test_cumulative_radiation_config():
    runner = CliRunner()
    cfg_file = 'tests/assets/temp/rad_config.json'
    cmd_args = ['-o', cfg_file]

    result = runner.invoke(cumulative_radiation_config, cmd_args)
    assert result.exit_code == 0
    assert os.path.isfile(cfg_file)
    with open(cfg_file) as inf:
        result_dict = json.load(inf)
    assert result_dict['data'][0]['path'] == 'cumulative_radiation'
    os.unlink(cfg_file)


def test_direct_sun_hours_config():
    runner = CliRunner()
    cfg_file = 'tests/assets/temp/sun_config.json'
    cmd_args = ['-o', cfg_file, '-f', 'results']

    result = runner.invoke(direct_sun_hours_config, cmd_args)
    assert result.exit_code == 0
    assert os.path.isfile(cfg_file)
    with open(cfg_file) as inf:
        result_dict = json.load(inf)
    assert result_dict['data'][0]['path'] == 'results'
    os.unlink(cfg_file)


def test_sky_view_config():
    runner = CliRunner()
    cfg_file = 'tests/assets/temp/sv_config.json'
    cmd_args = ['-o', cfg_file, '-f', 'results']

    result = runner.invoke(sky_view_config, cmd_args)
    assert result.exit_code == 0
    assert os.path.isfile(cfg_file)
    with open(cfg_file) as inf:
        result_dict = json.load(inf)
    assert result_dict['data'][0]['path'] == 'results'
    os.unlink(cfg_file)
