from honeybee_radiance.modifierset import ModifierSet, WallModifierSet, FloorModifierSet, \
    RoofCeilingModifierSet, ApertureModifierSet, DoorModifierSet, ShadeModifierSet
from honeybee_radiance.modifier import Modifier
from honeybee_radiance.modifier.material import Plastic, Glass

import pytest


def test_modifierset_init():
    """Test the initialization of ModifierSet and basic properties."""
    default_set = ModifierSet('Default_Set')

    str(default_set)  # test the string representation of the modifier

    assert default_set.identifier == 'Default_Set'
    assert len(default_set.modifiers) == 18
    assert len(default_set.modifiers_unique) == 9
    assert len(default_set.modified_modifiers_unique) == 0

    assert isinstance(default_set.wall_set, WallModifierSet)
    assert isinstance(default_set.floor_set, FloorModifierSet)
    assert isinstance(default_set.roof_ceiling_set, RoofCeilingModifierSet)
    assert isinstance(default_set.aperture_set, ApertureModifierSet)
    assert isinstance(default_set.door_set, DoorModifierSet)
    assert isinstance(default_set.shade_set, ShadeModifierSet)


def test_modifierset_defaults():
    """Test the ModifierSet defaults."""
    default_set = ModifierSet('Default_Set')

    assert len(default_set.wall_set) == 2
    assert len(default_set.floor_set) == 2
    assert len(default_set.roof_ceiling_set) == 2
    assert len(default_set.aperture_set) == 4
    assert len(default_set.door_set) == 3

    for modifier in default_set.wall_set:
        assert isinstance(modifier, Modifier)
    for modifier in default_set.floor_set:
        assert isinstance(modifier, Modifier)
    for modifier in default_set.roof_ceiling_set:
        assert isinstance(modifier, Modifier)
    for modifier in default_set.aperture_set:
        assert isinstance(modifier, Modifier)
    for modifier in default_set.door_set:
        assert isinstance(modifier, Modifier)

    assert isinstance(default_set.wall_set.exterior_modifier, Modifier)
    assert isinstance(default_set.wall_set.interior_modifier, Modifier)
    assert isinstance(default_set.floor_set.exterior_modifier, Modifier)
    assert isinstance(default_set.floor_set.interior_modifier, Modifier)
    assert isinstance(default_set.roof_ceiling_set.exterior_modifier, Modifier)
    assert isinstance(default_set.roof_ceiling_set.interior_modifier, Modifier)
    assert isinstance(default_set.aperture_set.exterior_modifier, Modifier)
    assert isinstance(default_set.aperture_set.interior_modifier, Modifier)
    assert isinstance(default_set.aperture_set.skylight_modifier, Modifier)
    assert isinstance(default_set.aperture_set.exterior_modifier, Modifier)
    assert isinstance(default_set.aperture_set.window_modifier, Modifier)
    assert isinstance(default_set.door_set.exterior_modifier, Modifier)
    assert isinstance(default_set.door_set.interior_modifier, Modifier)
    assert isinstance(default_set.door_set.overhead_modifier, Modifier)


def test_setting_modifier():
    """Test the setting of modifiers on the ModifierSet."""
    default_set = ModifierSet('Thermal_Mass_Construction_Set')
    opaque_material_1 = Plastic.from_single_reflectance('test_opaque', 0.5)
    opaque_material_2 = Plastic.from_single_reflectance('test_opaque', 0.45)
    opaque_material_3 = Plastic.from_single_reflectance('test_opaque', 0.55)

    default_set.wall_set.exterior_modifier = opaque_material_1
    assert default_set.wall_set.exterior_modifier == opaque_material_1
    assert len(default_set.modified_modifiers_unique) == 1

    default_set.wall_set.interior_modifier = opaque_material_1
    assert default_set.wall_set.interior_modifier == opaque_material_1
    default_set.floor_set.exterior_modifier = opaque_material_2
    assert default_set.floor_set.exterior_modifier == opaque_material_2
    default_set.floor_set.interior_modifier = opaque_material_2
    assert default_set.floor_set.interior_modifier == opaque_material_2
    default_set.roof_ceiling_set.exterior_modifier = opaque_material_3
    assert default_set.roof_ceiling_set.exterior_modifier == opaque_material_3
    default_set.roof_ceiling_set.interior_modifier = opaque_material_3
    assert default_set.roof_ceiling_set.interior_modifier == opaque_material_3
    default_set.door_set.exterior_modifier = opaque_material_3
    assert default_set.door_set.exterior_modifier == opaque_material_3
    default_set.door_set.interior_modifier = opaque_material_3
    assert default_set.door_set.interior_modifier == opaque_material_3
    default_set.door_set.overhead_modifier = opaque_material_3
    assert default_set.door_set.overhead_modifier == opaque_material_3

    assert len(default_set.modified_modifiers_unique) == 3


def test_setting_aperture_modifier():
    """Test the setting of aperture modifiers on the ModifierSet."""
    default_set = ModifierSet('Tinted_Window_Set')
    glass_material = Glass.from_single_transmittance('test_glass', 0.6)
    glass_material_dark = Glass.from_single_transmittance('test_glass_dark', 0.3)

    default_set.aperture_set.exterior_modifier = glass_material
    assert default_set.aperture_set.exterior_modifier == glass_material
    assert len(default_set.modified_modifiers_unique) == 1

    default_set.aperture_set.interior_modifier = glass_material
    assert default_set.aperture_set.interior_modifier == glass_material
    default_set.aperture_set.skylight_modifier = glass_material_dark
    assert default_set.aperture_set.skylight_modifier == glass_material_dark
    default_set.aperture_set.exterior_modifier = glass_material
    assert default_set.aperture_set.exterior_modifier == glass_material
    default_set.aperture_set.window_modifier = glass_material_dark
    assert default_set.aperture_set.window_modifier == glass_material_dark

    assert len(default_set.modified_modifiers_unique) == 2


def test_modifierset_equality():
    """Test the equality of ModifierSets to one another."""
    default_set = ModifierSet('Default_Set')
    new_default_set = default_set.duplicate()

    assert default_set is default_set
    assert new_default_set is not default_set
    assert new_default_set == default_set

    new_default_set.identifier = 'New_Construction_Set'
    assert new_default_set != default_set

    new_default_set = default_set.duplicate()
    opaque_material = Plastic.from_single_reflectance('test_opaque', 0.5)
    default_set.wall_set.exterior_modifier = opaque_material
    assert new_default_set != default_set


def test_modifierset_to_dict_full():
    """Test the to_dict method writing out all modifiers."""
    default_set = ModifierSet('Default_Set')

    modifier_dict = default_set.to_dict(none_for_defaults=False)

    assert modifier_dict['wall_set']['exterior_modifier'] is not None
    assert modifier_dict['wall_set']['interior_modifier'] is not None
    assert modifier_dict['floor_set']['exterior_modifier'] is not None
    assert modifier_dict['floor_set']['interior_modifier'] is not None
    assert modifier_dict['roof_ceiling_set']['exterior_modifier'] is not None
    assert modifier_dict['roof_ceiling_set']['interior_modifier'] is not None
    assert modifier_dict['aperture_set']['window_modifier'] is not None
    assert modifier_dict['aperture_set']['interior_modifier'] is not None
    assert modifier_dict['aperture_set']['skylight_modifier'] is not None
    assert modifier_dict['aperture_set']['operable_modifier'] is not None
    assert modifier_dict['door_set']['exterior_modifier'] is not None
    assert modifier_dict['door_set']['interior_modifier'] is not None
    assert modifier_dict['door_set']['exterior_glass_modifier'] is not None
    assert modifier_dict['door_set']['interior_glass_modifier'] is not None
    assert modifier_dict['door_set']['overhead_modifier'] is not None
    assert modifier_dict['shade_set']['exterior_modifier'] is not None
    assert modifier_dict['shade_set']['interior_modifier'] is not None


def test_modifierset_dict_methods():
    """Test the to/from dict methods."""
    insulated_set = ModifierSet('Insulated_Set')
    triple_clear = Glass.from_single_transmittance('Triple_Clear_Window', 0.4)

    insulated_set.aperture_set.window_modifier = triple_clear
    mod_dict = insulated_set.to_dict()

    assert mod_dict['wall_set']['exterior_modifier'] is None
    assert mod_dict['wall_set']['interior_modifier'] is None
    assert mod_dict['floor_set']['exterior_modifier'] is None
    assert mod_dict['floor_set']['interior_modifier'] is None
    assert mod_dict['roof_ceiling_set']['exterior_modifier'] is None
    assert mod_dict['roof_ceiling_set']['interior_modifier'] is None
    assert mod_dict['aperture_set']['window_modifier'] is not None
    assert mod_dict['aperture_set']['interior_modifier'] is None
    assert mod_dict['aperture_set']['skylight_modifier'] is None
    assert mod_dict['aperture_set']['operable_modifier'] is None
    assert mod_dict['door_set']['exterior_modifier'] is None
    assert mod_dict['door_set']['interior_modifier'] is None
    assert mod_dict['door_set']['exterior_glass_modifier'] is None
    assert mod_dict['door_set']['interior_glass_modifier'] is None
    assert mod_dict['door_set']['overhead_modifier'] is None
    assert mod_dict['shade_set']['exterior_modifier'] is None
    assert mod_dict['shade_set']['interior_modifier'] is None

    new_mod_set = ModifierSet.from_dict(mod_dict)
    assert mod_dict == new_mod_set.to_dict()
