"""Test grid subcommands."""
import os
import json
from click.testing import CliRunner

from honeybee_radiance.cli.grid import split_grid, merge_grid, from_rooms
from honeybee_radiance.sensorgrid import SensorGrid


def test_split_grid():
    input_grid = './tests/assets/grid/sensor_grid_split.pts'
    output_folder = './tests/assets/temp'
    runner = CliRunner()
    result = runner.invoke(split_grid, [input_grid, '5', '--folder', output_folder])
    assert result.exit_code == 0
    # check the file is created
    for count in range(4):
        pts_file = os.path.join(output_folder, 'sensor_grid_split_%04d.pts' % count)
        assert os.path.isfile(pts_file)
        grid = SensorGrid.from_file(pts_file)
        if count != 3:
            assert grid.count == 5
        else:
            assert grid.count == 6


def test_split_grid_single():
    input_grid = './tests/assets/grid/sensor_grid_single.pts'
    output_folder = './tests/assets/temp'
    runner = CliRunner()
    result = runner.invoke(split_grid, [input_grid, '100', '--folder', output_folder])
    assert result.exit_code == 0
    # check the file is created and named correctly
    pts_file = os.path.join(output_folder, 'sensor_grid_single_0000.pts')
    assert os.path.isfile(pts_file)
    grid = SensorGrid.from_file(pts_file)
    assert grid.count == 21


def test_merge_grid():
    base_name = 'sensor_grid_merge'
    input_folder = './tests/assets/grid'
    output_folder = './tests/assets/temp'
    runner = CliRunner()
    result = runner.invoke(
        merge_grid, [input_folder, base_name, '--folder', output_folder]
    )
    assert result.exit_code == 0
    # check the file is created
    pts_file = os.path.join(output_folder, base_name + '.pts')
    assert os.path.isfile(pts_file)
    grid = SensorGrid.from_file(pts_file)
    assert grid.count == 21


def test_merge_grid_with_header():
    base_name = 'grid'
    input_folder = './tests/assets/grid'
    output_folder = './tests/assets/temp'
    runner = CliRunner()
    result = runner.invoke(
        merge_grid, [input_folder, base_name, '.ill', '--folder', output_folder]
    )
    assert result.exit_code == 0
    # check the file is created
    res_file = os.path.join(output_folder, base_name + '.ill')
    assert os.path.isfile(res_file)
    with open(res_file) as inf:
        for count, _ in enumerate(inf):
            pass

    assert count == 160 - 1


def test_from_rooms():
    runner = CliRunner()
    input_hb_model = './tests/assets/model/model_radiance_dynamic_states.hbjson'

    result = runner.invoke(from_rooms, [input_hb_model])
    assert result.exit_code == 0
    sg_dict = json.loads(result.output)
    new_grids = [SensorGrid.from_dict(sg) for sg in sg_dict]
    assert len(new_grids) == 2
    assert all(isinstance(sg, SensorGrid) for sg in new_grids)
