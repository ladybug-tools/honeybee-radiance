"""Test cli glare module."""
import os

from click.testing import CliRunner

from ladybug.futil import nukedir

from honeybee_radiance.cli.glare import two_phase_command


def test_two_phase_command_dgp():
    runner = CliRunner()
    dc_direct = './tests/assets/glare/dc1.mtx'
    dc_total = './tests/assets/glare/dc8.mtx'
    sky_mtx = './tests/assets/glare/sky.smx'
    view_rays = './tests/assets/glare/screenviews.ray'
    output = './tests/assets/temp/screenviews.dgp'
    output_folder = './tests/assets/temp'
    cmd_args = [
        dc_direct, dc_total, sky_mtx, view_rays, 
        '--output', output
    ]

    result = runner.invoke(two_phase_command, cmd_args)
    assert result.exit_code == 0
    assert os.path.isfile(output)
    nukedir(output_folder)

def test_two_phase_command_dgp_ga():
    runner = CliRunner()
    dc_direct = './tests/assets/glare/dc1.mtx'
    dc_total = './tests/assets/glare/dc8.mtx'
    sky_mtx = './tests/assets/glare/sky.smx'
    view_rays = './tests/assets/glare/screenviews.ray'
    occupancy_schedule = './tests/assets/glare/8to6withDST.60min.occ.csv'
    output = './tests/assets/temp/occupied.ga'
    output_folder = './tests/assets/temp'
    cmd_args = [
        dc_direct, dc_total, sky_mtx, view_rays,
        '--glare-limit', 0.4,
        '--occupancy-schedule', occupancy_schedule,
        '--output', output
    ]

    result = runner.invoke(two_phase_command, cmd_args)
    assert result.exit_code == 0
    assert os.path.isfile(output)
    nukedir(output_folder)
