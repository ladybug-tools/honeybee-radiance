from honeybee_radiance.modifierset import ModifierSet, WallSet, FloorSet, \
    RoofCeilingSet, ApertureSet, DoorSet
from honeybee_radiance.primitive import Primitive
from honeybee_radiance.primitive.material import Plastic, Glass

import pytest


def test_modifierset_init():
    """Test the initialization of ModifierSet and basic properties."""
    default_set = ModifierSet('Default Set')

    str(default_set)  # test the string representation of the modifier

    assert default_set.name == 'DefaultSet'
    assert len(default_set.modifiers) == 17
    assert len(default_set.unique_modifiers) == 10
    assert len(default_set.unique_modified_modifiers) == 0

    assert isinstance(default_set.wall_set, WallSet)
    assert isinstance(default_set.floor_set, FloorSet)
    assert isinstance(default_set.roof_ceiling_set, RoofCeilingSet)
    assert isinstance(default_set.aperture_set, ApertureSet)
    assert isinstance(default_set.door_set, DoorSet)


def test_modifierset_defaults():
    """Test the ModifierSet defaults."""
    default_set = ModifierSet('Default Set')

    assert len(default_set.wall_set) == 2
    assert len(default_set.floor_set) == 2
    assert len(default_set.roof_ceiling_set) == 2
    assert len(default_set.aperture_set) == 4
    assert len(default_set.door_set) == 3

    for modifier in default_set.wall_set:
        assert isinstance(modifier, Primitive)
    for modifier in default_set.floor_set:
        assert isinstance(modifier, Primitive)
    for modifier in default_set.roof_ceiling_set:
        assert isinstance(modifier, Primitive)
    for modifier in default_set.aperture_set:
        assert isinstance(modifier, Primitive)
    for modifier in default_set.door_set:
        assert isinstance(modifier, Primitive)

    assert isinstance(default_set.wall_set.exterior_modifier, Primitive)
    assert isinstance(default_set.wall_set.interior_modifier, Primitive)
    assert isinstance(default_set.floor_set.exterior_modifier, Primitive)
    assert isinstance(default_set.floor_set.interior_modifier, Primitive)
    assert isinstance(default_set.roof_ceiling_set.exterior_modifier, Primitive)
    assert isinstance(default_set.roof_ceiling_set.interior_modifier, Primitive)
    assert isinstance(default_set.aperture_set.exterior_modifier, Primitive)
    assert isinstance(default_set.aperture_set.interior_modifier, Primitive)
    assert isinstance(default_set.aperture_set.skylight_modifier, Primitive)
    assert isinstance(default_set.aperture_set.exterior_modifier, Primitive)
    assert isinstance(default_set.aperture_set.window_modifier, Primitive)
    assert isinstance(default_set.door_set.exterior_modifier, Primitive)
    assert isinstance(default_set.door_set.interior_modifier, Primitive)
    assert isinstance(default_set.door_set.overhead_modifier, Primitive)


def test_setting_modifier():
    """Test the setting of modifiers on the ModifierSet."""
    default_set = ModifierSet('Thermal Mass Construction Set')
    opaque_material = Plastic.from_single_reflectance('test_opaque', 0.5)
    
    default_set.wall_set.exterior_modifier = opaque_material
    assert default_set.wall_set.exterior_modifier == opaque_material
    assert len(default_set.unique_modified_modifiers) == 1

    default_set.wall_set.interior_modifier = opaque_material
    assert default_set.wall_set.interior_modifier == opaque_material
    default_set.floor_set.exterior_modifier = opaque_material
    assert default_set.floor_set.exterior_modifier == opaque_material
    default_set.floor_set.interior_modifier = opaque_material
    assert default_set.floor_set.interior_modifier == opaque_material
    default_set.roof_ceiling_set.exterior_modifier = opaque_material
    assert default_set.roof_ceiling_set.exterior_modifier == opaque_material
    default_set.roof_ceiling_set.interior_modifier = opaque_material
    assert default_set.roof_ceiling_set.interior_modifier == opaque_material
    default_set.door_set.exterior_modifier = opaque_material
    assert default_set.door_set.exterior_modifier == opaque_material
    default_set.door_set.interior_modifier = opaque_material
    assert default_set.door_set.interior_modifier == opaque_material
    default_set.door_set.overhead_modifier = opaque_material
    assert default_set.door_set.overhead_modifier == opaque_material

    assert len(default_set.unique_modified_modifiers) == 1


def test_setting_aperture_modifier():
    """Test the setting of aperture modifiers on the ModifierSet."""
    default_set = ModifierSet('Tinted Window Set')
    glass_material = Glass.from_single_transmittance('test_glass', 0.6)
    glass_material_dark = Glass.from_single_transmittance('test_glass_dark', 0.3)

    default_set.aperture_set.exterior_modifier = glass_material
    assert default_set.aperture_set.exterior_modifier == glass_material
    assert len(default_set.unique_modified_modifiers) == 1

    default_set.aperture_set.interior_modifier = glass_material
    assert default_set.aperture_set.interior_modifier == glass_material
    default_set.aperture_set.skylight_modifier = glass_material_dark
    assert default_set.aperture_set.skylight_modifier == glass_material_dark
    default_set.aperture_set.exterior_modifier = glass_material
    assert default_set.aperture_set.exterior_modifier == glass_material
    default_set.aperture_set.window_modifier = glass_material_dark
    assert default_set.aperture_set.window_modifier == glass_material_dark

    assert len(default_set.unique_modified_modifiers) == 2


def test_modifierset_equality():
    """Test the equality of ModifierSets to one another."""
    default_set = ModifierSet('Default Set')
    opaque_material = Plastic.from_single_reflectance('test_opaque', 0.5)
    default_set.wall_set.exterior_modifier = opaque_material
    new_default_set = default_set.duplicate()

    assert default_set is default_set
    assert new_default_set is not default_set
    assert new_default_set == default_set

    new_default_set.name = 'New Construction Set'
    assert new_default_set != default_set


def test_modifierset_to_dict_full():
    """Test the to_dict method writing out all modifiers."""
    default_set = ModifierSet('Default Set')

    modifier_dict = default_set.to_dict(none_for_defaults=False)

    assert modifier_dict['wall_set']['exterior_modifier'] is not None
    assert modifier_dict['wall_set']['interior_modifier'] is not None
    assert modifier_dict['floor_set']['exterior_modifier'] is not None
    assert modifier_dict['floor_set']['interior_modifier'] is not None
    assert modifier_dict['roof_ceiling_set']['exterior_modifier'] is not None
    assert modifier_dict['roof_ceiling_set']['interior_modifier'] is not None
    assert modifier_dict['aperture_set']['interior_modifier'] is not None
    assert modifier_dict['aperture_set']['skylight_modifier'] is not None
    assert modifier_dict['aperture_set']['exterior_modifier'] is not None
    assert modifier_dict['door_set']['exterior_modifier'] is not None
    assert modifier_dict['door_set']['interior_modifier'] is not None
    assert modifier_dict['door_set']['overhead_modifier'] is not None
    assert modifier_dict['shade_set']['exterior_modifier'] is not None
    assert modifier_dict['shade_set']['interior_modifier'] is not None
