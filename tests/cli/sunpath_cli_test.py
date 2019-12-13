"""Test sky subcommands."""

from click.testing import CliRunner
from honeybee_radiance.cli.sunpath import sunpath_from_location, \
    sunpath_from_epw
from honeybee_radiance.cli.util import get_hoys
import uuid
import os


def test_get_hoys():
    output = [489, 500, 510, 520, 530, 540, 550, 560, 570, 580, 590]
    hoys = get_hoys('JAN-01', '08:10', 'JAN-01', '09:50', 6, False)
    moy = [int(h * 60) for h in hoys]
    assert moy == output


def test_sunpath_climate_based():
    folder = './tests/assets/temp'
    runner = CliRunner()
    result = runner.invoke(
        sunpath_from_epw,
        [
            './tests/assets/epw/denver.epw', '--folder', folder,
            '--start-date', 'JAN-01', '--end-date', 'JAN-01', '--name', 'sunpath_cli_cb'
        ]
    )
    assert result.exit_code == 0


def test_sunpath():
    folder = './tests/assets/temp'
    runner = CliRunner()
    result = runner.invoke(
        sunpath_from_location,
        ['--lat', '39.76', '--lon', '-104.86', '--tz', '-7', '--folder', folder,
        '--start-date', 'JAN-01', '--end-date', 'JAN-01', '--name', 'sunpath_cli']
    )
    assert result.exit_code == 0


def test_sunpath_climate_based_reversed():
    folder = './tests/assets/temp'
    runner = CliRunner()
    result = runner.invoke(
        sunpath_from_epw,
        [
            './tests/assets/epw/denver.epw', '--folder', folder,
            '--start-date', 'JAN-01', '--end-date', 'JAN-01', '--name',
            'sunpath_cli_cb_r', '--reverse-vectors'
        ]
    )
    assert result.exit_code == 0


def test_sunpath_reversed():
    folder = './tests/assets/temp'
    runner = CliRunner()
    result = runner.invoke(
        sunpath_from_location,
        ['--lat', '39.76', '--lon', '-104.86', '--tz', '-7', '--folder', folder,
        '--start-date', 'JAN-01', '--end-date', 'JAN-01', '--name', 'sunpath_cli_r',
        '--reverse-vectors']
    )
    assert result.exit_code == 0
