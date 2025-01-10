"""Test cli translate module."""
import json
from click.testing import CliRunner

from honeybee.model import Model

from honeybee_radiance.cli.edit import add_room_sensors, add_face3d_sensors, \
    mirror_model_sensors, reset_resource_ids


def test_reset_resource_ids():
    runner = CliRunner()
    input_hb_model = './tests/assets/model/shoe_box_mod_set.hbjson'

    c_args = [input_hb_model, '-uuid']
    result = runner.invoke(reset_resource_ids, c_args)
    assert result.exit_code == 0
    model_dict = json.loads(result.output)
    new_model = Model.from_dict(model_dict)
    new_con_set = new_model.properties.radiance.modifier_sets[0]
    old_id = 'ClimateZone_2_ModifierSet'
    assert new_con_set.identifier.startswith(old_id)
    assert new_con_set.identifier != old_id


def test_add_room_sensors():
    runner = CliRunner()
    input_hb_model = './tests/assets/model/model_radiance_dynamic_states.hbjson'

    result = runner.invoke(add_room_sensors, [input_hb_model])
    assert result.exit_code == 0
    model_dict = json.loads(result.output)
    new_model = Model.from_dict(model_dict)
    assert len(new_model.properties.radiance.sensor_grids) == 2


def test_add_face3d_sensors():
    runner = CliRunner()
    input_hb_model = './tests/assets/model/model_radiance_dynamic_states.hbjson'
    input_file = './tests/assets/model/face3d_array.json'

    result = runner.invoke(add_face3d_sensors, [input_hb_model, input_file])
    assert result.exit_code == 0
    model_dict = json.loads(result.output)
    new_model = Model.from_dict(model_dict)
    assert len(new_model.properties.radiance.sensor_grids) == 1


def test_mirror_model_sensors():
    runner = CliRunner()
    input_hb_model = './tests/assets/model/two_rooms.hbjson'

    result = runner.invoke(mirror_model_sensors, [input_hb_model])
    assert result.exit_code == 0
    model_dict = json.loads(result.output)
    new_model = Model.from_dict(model_dict)
    assert len(new_model.properties.radiance.sensor_grids) == 4
