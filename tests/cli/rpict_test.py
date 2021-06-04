"""Test cli rpict module."""
import os
import json

from click.testing import CliRunner

from ladybug.futil import nukedir

from honeybee_radiance.cli.rpict import rpict_command


def test_rpict_command():
    runner = CliRunner()
    input_oct = './tests/assets/octree/scene.oct'
    input_view = './tests/assets/view/indoorview.vf'
    cmd_args = [input_oct, input_view, '--rad-params', '-ab 10 -ad 1433',
                '--output', 'input_view.HDR', '--dry-run']

    result = runner.invoke(rpict_command, cmd_args)
    assert result.exit_code == 0
    cmd_output = result.output
    assert 'rpict -ab 10 -ad 1433 -i-' in cmd_output


def test_rpict_command_detailed():
    runner = CliRunner()
    input_oct = './tests/assets/octree/scene.oct'
    input_view = './tests/assets/view/indoorview.vf'
    cmd_args = [input_oct, input_view, '--metric', 'irradiance', '--resolution', '1000',
                '--scale-factor', '2', '--output', 'input_view.HDR', '--dry-run']

    result = runner.invoke(rpict_command, cmd_args)
    assert result.exit_code == 0
    cmd_output = result.output
    assert 'rpict -i -x 2000 -y 2000' in cmd_output
