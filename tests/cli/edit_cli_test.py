"""Test cli translate module."""
import json
from click.testing import CliRunner

from honeybee.model import Model

from honeybee_radiance.cli.edit import add_room_sensors, mirror_model_sensors


def test_add_room_sensors():
    runner = CliRunner()
    input_hb_model = './tests/assets/model/model_radiance_dynamic_states.hbjson'

    result = runner.invoke(add_room_sensors, [input_hb_model])
    assert result.exit_code == 0
    model_dict = json.loads(result.output)
    new_model = Model.from_dict(model_dict)
    assert len(new_model.properties.radiance.sensor_grids) == 2


def test_mirror_model_sensors():
    runner = CliRunner()
    input_hb_model = './tests/assets/model/two_rooms.hbjson'

    result = runner.invoke(mirror_model_sensors, [input_hb_model])
    assert result.exit_code == 0
    model_dict = json.loads(result.output)
    new_model = Model.from_dict(model_dict)
    assert len(new_model.properties.radiance.sensor_grids) == 4
