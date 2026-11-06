"""Test cli postprocess module."""
import os
import json

from click.testing import CliRunner

from ladybug.futil import nukedir
from ladybug.analysisperiod import AnalysisPeriod
from ladybug.location import Location
from ladybug.wea import Wea

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


def test_annual_irradiance_epw():
    runner = CliRunner()
    input_folder = './tests/assets/irrad_result'
    wea_file = './tests/assets/epw/denver.epw'
    sub_folder = 'metrics'
    result_dir = os.path.join(input_folder, sub_folder)
    cmd_args = [input_folder, wea_file, '--sub-folder', sub_folder]

    result = runner.invoke(annual_irradiance, cmd_args)
    assert result.exit_code == 0
    assert os.path.isdir(result_dir)
    nukedir(result_dir, rmdir=True)


def test_annual_irradiance_timestep():
    runner = CliRunner()
    input_folder = './tests/assets/temp/irrad_timestep'
    if not os.path.isdir(input_folder):
        os.makedirs(input_folder)
    timestep = 4
    location = Location('Tel Aviv', latitude=32, longitude=34.8, time_zone=2)
    wea = Wea.from_ashrae_clear_sky(location, timestep=timestep)
    wea = wea.filter_by_analysis_period(AnalysisPeriod(6, 21, 0, 6, 21, 23, timestep))
    wea_file = wea.write(os.path.join(input_folder, 'one_day.wea'))
    with open(os.path.join(input_folder, 'grid.ill'), 'w') as ill_file:
        ill_file.write(' '.join(['100'] * len(wea)) + '\n')
    with open(os.path.join(input_folder, 'grids_info.json'), 'w') as info_file:
        json.dump([{'identifier': 'grid', 'full_id': 'grid', 'count': 1}], info_file)
    cmd_args = [input_folder, wea_file, '--timestep', str(timestep)]

    result = runner.invoke(annual_irradiance, cmd_args)
    assert result.exit_code == 0
    metrics = os.path.join(input_folder, 'metrics')
    with open(os.path.join(metrics, 'average_irradiance', 'grid.res')) as avg_file:
        assert float(avg_file.read()) == 100
    with open(os.path.join(metrics, 'cumulative_radiation', 'grid.res')) as cml_file:
        assert float(cml_file.read()) == 2.4
    nukedir(input_folder, rmdir=True)


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
