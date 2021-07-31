"""Test cli translate module."""
import os
import json

from click.testing import CliRunner

from ladybug.futil import nukedir

from honeybee_radiance.cli.translate import (
    model_to_rad_folder,
    model_to_rad,
    modifier_to_rad,
    modifier_from_rad,
    model_radiant_enclosure_info,
)


def test_model_to_rad_folder():
    runner = CliRunner()
    input_hb_model = "./tests/assets/model/model_radiance_dynamic_states.hbjson"
    output_hb_model = "./tests/assets/model/model"

    result = runner.invoke(model_to_rad_folder, [input_hb_model])
    assert result.exit_code == 0
    assert os.path.isdir(output_hb_model)
    nukedir(output_hb_model, True)


def test_rfluxmtx_control_params():
    runner = CliRunner()
    input_hb_model = "./tests/assets/model/room_w_dynamic_skylight.hbjson"
    output_hb_model = "./tests/assets/model/model"

    result = runner.invoke(model_to_rad_folder, [input_hb_model])
    assert result.exit_code == 0
    assert os.path.isdir(output_hb_model)
    skylight_file = os.path.join(output_hb_model, 'aperture_group', 'skylight..mtx.rad')
    assert os.path.isfile(skylight_file)
    with open(skylight_file) as s_file:
        content = s_file.read()
        assert '#@rfluxmtx h=kf u=0.0,1.0,0.0' in content \
            or '#@rfluxmtx h=kf u=0.0,-1.0,0.0' in content
    nukedir(output_hb_model)


def test_model_to_rad_folder_joined_grid():
    runner = CliRunner()
    input_hb_model = "./tests/assets/model/two_rooms_same_grid_identifier.hbjson"
    output_hb_model = "./tests/assets/model/model"

    result = runner.invoke(model_to_rad_folder, [input_hb_model])
    assert result.exit_code == 0
    assert os.path.isdir(output_hb_model)

    # TODO: check illuminance file exist
    # check number of sensors
    grid_file = "./tests/assets/model/model/grid/illuminance_grid.pts"
    assert os.path.isfile(grid_file)
    with open(grid_file) as gf:
        sensors = gf.readlines()
    assert len(sensors) == 221
    nukedir(output_hb_model, True)


def test_model_to_rad_folder_model_grid_info():
    runner = CliRunner()
    input_hb_model = "./tests/assets/model/dup_grid_id.hbjson"
    output_hb_model = "./tests/assets/model/model"

    result = runner.invoke(model_to_rad_folder, [input_hb_model])
    assert result.exit_code == 0
    assert os.path.isdir(output_hb_model)

    # check number of sensors
    grid_file = "./tests/assets/model/model/grid/perimeter.pts"
    assert os.path.isfile(grid_file)
    with open(grid_file) as gf:
        sensors = gf.readlines()
    assert len(sensors) == 520

    # check _model_grids_info.json
    info_file = "./tests/assets/model/model/grid/_info.json"
    with open(info_file) as _info:
        inf = json.load(_info)

    assert inf == [
        {
            "name": "core",
            "identifier": "core",
            "count": 640,
            "group": "",
            "full_id": "core",
        },
        {
            "name": "perimeter",
            "identifier": "perimeter",
            "count": 520,
            "group": "",
            "full_id": "perimeter",
        },
    ]

    model_info_file = "./tests/assets/model/model/grid/_model_grids_info.json"
    with open(model_info_file) as _info:
        inf = json.load(_info)

    assert inf == [
        {
            "name": "perimeter",
            "identifier": "perimeter",
            "count": 300,
            "group": "",
            "full_id": "perimeter",
            "start_ln": 0,
        },
        {
            "name": "perimeter",
            "identifier": "perimeter",
            "count": 220,
            "group": "",
            "full_id": "perimeter",
            "start_ln": 300,
        },
        {
            "name": "core",
            "identifier": "core",
            "count": 640,
            "group": "",
            "full_id": "core",
            "start_ln": 0,
        },
    ]
    nukedir(output_hb_model, True)


def test_model_to_rad_folder_no_grids():
    runner = CliRunner()
    input_hb_model = "./tests/assets/model/two_rooms_no_grids.hbjson"
    output_hb_model = "./tests/assets/model/model"

    result = runner.invoke(model_to_rad_folder, [input_hb_model, "--grid-check"])
    assert result.exit_code == 1
    nukedir(output_hb_model, True)


def test_model_to_rad_folder_grid_filter():
    runner = CliRunner()
    input_hb_model = "./tests/assets/model/sample_room_with_grid_group.hbjson"
    output_hb_model = "./tests/assets/temp/model"

    result = runner.invoke(
        model_to_rad_folder,
        [input_hb_model, "--folder", output_hb_model, "-g", "?pertures/*"],
    )
    assert result.exit_code == 0
    assert os.path.isdir(os.path.join(output_hb_model, "model"))
    assert os.path.isdir(os.path.join(output_hb_model, "model", "grid", "apertures"))
    assert not os.path.isdir(
        os.path.join(output_hb_model, "model", "grid", "occ_regions")
    )

    nukedir(output_hb_model, True)


def test_model_to_rad():
    runner = CliRunner()
    input_hb_model = "./tests/assets/model/model_complete_multiroom_radiance.hbjson"

    result = runner.invoke(model_to_rad, [input_hb_model])
    assert result.exit_code == 0

    output_hb_model = "./tests/assets/model/model_complete_multiroom_radiance.rad"
    result = runner.invoke(
        model_to_rad, [input_hb_model, "--output-file", output_hb_model]
    )
    assert result.exit_code == 0
    assert os.path.isfile(output_hb_model)
    os.remove(output_hb_model)


def test_model_radiant_enclosure_info():
    runner = CliRunner()
    input_hb_model = "./tests/assets/model/two_rooms.hbjson"
    output_enclosure_folder = "./tests/assets/model/enclosure"

    result = runner.invoke(model_radiant_enclosure_info, [input_hb_model])
    assert result.exit_code == 0
    assert os.path.isdir(output_enclosure_folder)
    nukedir(output_enclosure_folder, True)


def test_modifier_to_from_rad():
    runner = CliRunner()
    input_hb_mod = "./tests/assets/modifier/modifier_plastic_generic_wall.json"
    output_hb_rad = "./tests/assets/modifier/modifier_plastic_generic_wall.rad"

    result = runner.invoke(
        modifier_to_rad, [input_hb_mod, "--output-file", output_hb_rad]
    )
    assert result.exit_code == 0
    assert os.path.isfile(output_hb_rad)

    result = runner.invoke(modifier_from_rad, [output_hb_rad])
    assert result.exit_code == 0

    os.remove(output_hb_rad)


def test_modifier_to_from_rad_trans():
    runner = CliRunner()
    input_hb_mod = "./tests/assets/modifier/modifier_trans_tree_foliage.json"
    output_hb_rad = "./tests/assets/modifier/modifier_trans_tree_foliage.rad"

    result = runner.invoke(
        modifier_to_rad, [input_hb_mod, "--output-file", output_hb_rad]
    )
    assert result.exit_code == 0
    assert os.path.isfile(output_hb_rad)

    result = runner.invoke(modifier_from_rad, [output_hb_rad])
    assert result.exit_code == 0

    os.remove(output_hb_rad)
