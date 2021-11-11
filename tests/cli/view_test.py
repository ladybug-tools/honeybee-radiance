"""Test cli view module."""
import os
import json

from click.testing import CliRunner

from ladybug.futil import nukedir

from honeybee_radiance.cli.view import split_view, merge_view


def test_split_view_overture():
    runner = CliRunner()
    input_oct = './tests/assets/octree/scene.oct'
    input_view = './tests/assets/view/indoorview.vf'
    output_folder = './tests/assets/view/split_view_amb/'
    cmd_args = [input_view, '4', '--overture',
                '--rad-params', '-ab 2 -aa 0.1 -ad 2048 -ar 64', '--octree', input_oct,
                '--folder', output_folder]

    result = runner.invoke(split_view, cmd_args)
    assert result.exit_code == 0
    assert os.path.isfile(os.path.join(output_folder, 'indoorview.amb'))
    nukedir(output_folder, rmdir=True)


def test_split_view():
    runner = CliRunner()
    input_oct = './tests/assets/octree/scene.oct'
    input_view = './tests/assets/view/indoorview.vf'
    output_folder = './tests/assets/view/split_view/'
    cmd_args = [input_view, '4', '--skip-overture', '--folder', output_folder]

    result = runner.invoke(split_view, cmd_args)
    assert result.exit_code == 0
    cmd_output = result.output
    vf_list = json.loads(cmd_output)
    assert len(vf_list) == 4
    nukedir(output_folder, rmdir=True)


def test_merge_view():
    runner = CliRunner()
    input_folder = './tests/assets/hdr/'
    out_folder = './tests/assets/hdr/hdr_result/'
    cmd_args = [input_folder, 'unnamed', '--folder', out_folder, '--name', 'unnamed']

    result = runner.invoke(merge_view, cmd_args)
    assert result.exit_code == 0
    out_image = os.path.join(out_folder, 'unnamed.HDR')
    assert os.path.isfile(os.path.join(out_folder, 'unnamed.HDR'))
    nukedir(out_folder, rmdir=True)


def test_merge_view_org_view():
    """Test merge view with additional input that doesn't exist"""
    runner = CliRunner()
    input_folder = './tests/assets/hdr/'
    out_folder = './tests/assets/hdr/hdr_result/'
    cmd_args = [
        input_folder, 'unnamed', '--folder', out_folder, '--name', 'unnamed',
        '--view', 'not-a-view.vf'
    ]

    result = runner.invoke(merge_view, cmd_args)
    assert result.exit_code == 0
    out_image = os.path.join(out_folder, 'unnamed.HDR')
    assert os.path.isfile(os.path.join(out_folder, 'unnamed.HDR'))
    nukedir(out_folder, rmdir=True)
