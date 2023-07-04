"""Test cli lib module."""
from click.testing import CliRunner
from honeybee_radiance.cli.lib import modifiers, modifier_sets, \
    modifier_by_id, modifier_set_by_id, modifiers_by_id, modifier_sets_by_id, \
    add_to_lib, purge_lib

from honeybee_radiance.modifier.material import Plastic, Glass
from honeybee_radiance.modifierset import ModifierSet

import os
import json


def test_lib_object_existence():
    """Test the existence of modifier and modifier set objects in the library."""
    runner = CliRunner()

    result = runner.invoke(modifiers)
    assert result.exit_code == 0

    result = runner.invoke(modifier_sets)
    assert result.exit_code == 0


def test_object_from_lib():
    """Test getting an object from the library."""
    runner = CliRunner()

    result = runner.invoke(modifier_by_id, ['generic_wall_0.50'])
    assert result.exit_code == 0
    mat_dict = json.loads(result.output)
    assert isinstance(Plastic.from_dict(mat_dict), Plastic)

    result = runner.invoke(modifier_by_id, ['generic_exterior_window_vis_0.64'])
    assert result.exit_code == 0
    mat_dict = json.loads(result.output)
    assert isinstance(Glass.from_dict(mat_dict), Glass)

    result = runner.invoke(modifier_set_by_id, ['Generic_Interior_Solar_Modifier_Set'])
    assert result.exit_code == 0
    con_dict = json.loads(result.output)
    assert isinstance(ModifierSet.from_dict(con_dict), ModifierSet)


def test_objects_from_lib():
    """Test getting several objects from the library."""
    runner = CliRunner()

    result = runner.invoke(
        modifiers_by_id, ['generic_wall_0.50', 'generic_floor_0.20'])
    assert result.exit_code == 0
    mat_dict = json.loads(result.output)
    assert isinstance(Plastic.from_dict(mat_dict[0]), Plastic)

    result = runner.invoke(modifier_sets_by_id, ['Generic_Interior_Solar_Modifier_Set'])
    assert result.exit_code == 0
    con_dict = json.loads(result.output)
    assert isinstance(ModifierSet.from_dict(con_dict[0]), ModifierSet)


def test_add_to_lib():
    """Test the add_to_lib command."""
    runner = CliRunner()

    resource_file = './tests/assets/model/sample_radiance_properties.json'
    result = runner.invoke(add_to_lib, [resource_file])
    assert result.exit_code == 0
    assert 'Modifier: ClimateZone_2_Window' in result.output
    assert 'Modifier Set: ClimateZone_2_ModifierSet' in result.output


def test_purge_lib():
    """Test the purge_lib command."""
    runner = CliRunner()

    result = runner.invoke(purge_lib)
    assert result.exit_code == 0
