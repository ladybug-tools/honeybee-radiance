"""Test cli translate module."""
import os
import json

from click.testing import CliRunner

from ladybug.futil import nukedir

from honeybee_radiance.cli.raytrace import rtrace_with_df_post_process, \
    rtrace_with_pit_post_process


def test_rtrace_with_df_post_process():
    runner = CliRunner()
    input_oct = './tests/assets/octree/scene.oct'
    input_grid = './tests/assets/grid/sensor_grid_merge_0000.pts'
    cmd_args = [input_oct, input_grid, '--rad-params', '"-ab 10 -ad 1433 -I"',
                '--rad-params-locked', '"-I"', '--output', 'grid.res',
                '--sky-illum', '1000', '--dry-run']

    result = runner.invoke(rtrace_with_df_post_process, cmd_args)
    assert result.exit_code == 0
    cmd_output = result.output
    assert '17900/1000' in cmd_output


def test_rtrace_with_pit_post_process():
    runner = CliRunner()
    input_oct = './tests/assets/octree/scene.oct'
    input_grid = './tests/assets/grid/sensor_grid_merge_0000.pts'
    cmd_args = [input_oct, input_grid, '--rad-params', '-ab 2 -aa 0.1 -ad 2048 -ar 64',
                '--rad-params-locked', '-h',
                '--output', 'grid.res', '--metric', 'illuminance', '--dry-run']

    result = runner.invoke(rtrace_with_pit_post_process, cmd_args)
    assert result.exit_code == 0
    cmd_output = result.output
    assert '*179' in cmd_output
