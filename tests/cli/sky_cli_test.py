"""Test sky subcommands."""

from click.testing import CliRunner
from honeybee_radiance.cli.sky import sky_with_certain_illum, sky_dome
import uuid
import os


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
    result = runner.invoke(sky_dome, ['--folder', folder, '--name', name])
    assert result.exit_code == 0
    # check the file is created
    assert os.path.isfile(os.path.join(folder, name))
