"""Test sky subcommands."""

from click.testing import CliRunner
from honeybee_radiance.cli.sky import sky_cie, sky_climate_based, \
    sky_with_certain_irrad, sky_with_certain_illum, sky_dome, leed_illuminance
from ladybug.futil import nukedir

import uuid
import os
import json


def test_sky_cie():
    folder = './tests/assets/temp'
    runner = CliRunner()

    name = str(uuid.uuid4()) + '.sky'
    args = ['21', 'Jun', '12:00', '-lat', '41.78', '-lon', '-87.75',
            '-type', '2', '--folder', folder, '--name', name]
    result = runner.invoke(sky_cie, args)
    assert result.exit_code == 0
    assert os.path.isfile(os.path.join(folder, name))

    args = ['-alt', '45', '-az', '180', '-type', '2', '--folder', folder, '--name', name]
    result = runner.invoke(sky_cie, args)
    assert result.exit_code == 0


def test_sky_climate_based():
    folder = './tests/assets/temp'
    runner = CliRunner()

    name = str(uuid.uuid4()) + '.sky'
    cb_s = 'ClimateBased, 21 Jun 12:00, lat:41.78, lon:-87.75, dni:800, dhi:120'
    args = ['21', 'Jun', '12:00', '-lat', '41.78', '-lon', '-87.75',
            '-dni', '800', '-dhi', '120', '--folder', folder, '--name', name]
    result = runner.invoke(sky_climate_based, args)
    assert result.exit_code == 0
    assert os.path.isfile(os.path.join(folder, name))

    args = ['-alt', '45', '-az', '180', '-dni', '800', '-dhi', '120',
            '--folder', folder, '--name', name]
    result = runner.invoke(sky_climate_based, args)
    assert result.exit_code == 0


def test_sky_with_certain_irrad():
    folder = './tests/assets/temp'
    runner = CliRunner()

    name = str(uuid.uuid4()) + '.sky'
    result = runner.invoke(
        sky_with_certain_irrad, ['800', '-g', '0.3', '--folder', folder, '--name', name])
    assert result.exit_code == 0
    assert os.path.isfile(os.path.join(folder, name))


def test_illuminance_sky():
    name = str(uuid.uuid4()) + '.sky'
    folder = './tests/assets/temp'
    runner = CliRunner()
    result = runner.invoke(
        sky_with_certain_illum,
        ['100000', '--folder', folder, '--name', name]
    )
    assert result.exit_code == 0
    # check the file is created
    assert os.path.isfile(os.path.join(folder, name))


def test_illuminance_sky_fail():
    name = str(uuid.uuid4()) + '.sky'
    folder = './tests/assets/temp'
    runner = CliRunner()
    result = runner.invoke(
        sky_with_certain_illum,
        ['c', '--folder', folder, '--name', name]
    )
    # input error
    assert result.exit_code == 2


def test_sky_dome():
    name = str(uuid.uuid4()) + '.sky'
    folder = './tests/assets/temp'
    runner = CliRunner()
    result = runner.invoke(
        sky_dome, ['--folder', folder, '--name', name, '--sky-density', 2]
    )
    assert result.exit_code == 0
    # check the file is created
    assert os.path.isfile(os.path.join(folder, name))


def test_leed_illuminance():
    wea_file = './tests/assets/wea/denver.wea'
    folder = './tests/assets/temp/leed'
    runner = CliRunner()
    result = runner.invoke(
        leed_illuminance, [wea_file, '--folder', folder]
    )
    assert result.exit_code == 0
    out_files = json.loads(result.output)
    # check the files are created
    for sky in out_files:
        assert os.path.isfile(sky['full_path'])
    nukedir(folder)
