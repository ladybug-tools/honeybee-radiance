"""Tests the features that honeybee_radiance adds to honeybee_core Room."""
from honeybee.room import Room
from honeybee.door import Door

from honeybee_radiance.properties.room import RoomRadianceProperties
from honeybee_radiance.modifierset import ModifierSet
from honeybee_radiance.modifier import Modifier
from honeybee_radiance.modifier.material import Plastic, Glass

from honeybee_radiance.lib.modifiersets import generic_modifier_set_visible, \
    generic_modifier_set_visible_exterior, generic_modifier_set_solar, \
    generic_modifier_set_solar_exterior
from honeybee_radiance.lib.modifiers import generic_exterior_window_solar, \
    generic_exterior_window_insect_screen_solar

from ladybug_geometry.geometry3d.pointvector import Point3D, Vector3D

import pytest


def test_radiance_properties():
    """Test the existence of the Room radiance properties."""
    room = Room.from_box('Shoe_Box', 5, 10, 3, 90, Point3D(0, 0, 3))

    assert hasattr(room.properties, 'radiance')
    assert isinstance(room.properties.radiance, RoomRadianceProperties)
    assert isinstance(room.properties.radiance.modifier_set, ModifierSet)
    assert room.properties.radiance.modifier_set == generic_modifier_set_visible


def test_set_modifier_set():
    """Test the auto-assigning of Room properties."""
    room = Room.from_box('Shoe_Box', 5, 10, 3, 90, Point3D(0, 0, 3))
    door_verts = [[1, 0, 0.1], [2, 0, 0.1], [2, 0, 3], [1, 0, 3]]
    room[3].add_door(Door.from_vertices('test_door', door_verts))
    room[1].apertures_by_ratio(0.4, 0.01)
    room[1].apertures[0].overhang(0.5, indoor=False)
    room[1].apertures[0].overhang(0.5, indoor=True)
    room[1].apertures[0].move_shades(Vector3D(0, 0, -0.5))

    assert room.properties.radiance.modifier_set == generic_modifier_set_visible

    room.properties.radiance.modifier_set = generic_modifier_set_visible_exterior
    assert room[1].apertures[0].properties.radiance.modifier == \
        generic_modifier_set_visible_exterior.aperture_set.window_modifier

    insect_screen_set = ModifierSet('Insect_Screen_Set')
    insect_screen_set.aperture_set.window_modifier = \
        generic_exterior_window_insect_screen_solar
    room.properties.radiance.modifier_set = insect_screen_set
    assert room[1].apertures[0].properties.radiance.modifier == \
        generic_exterior_window_insect_screen_solar

    with pytest.raises(AttributeError):
        room[1].properties.radiance.modifier.r_reflectance = 0.3
    with pytest.raises(AttributeError):
        room[5].properties.radiance.modifier.r_reflectance = 0.3
    with pytest.raises(AttributeError):
        room[3].doors[0].properties.radiance.modifier.r_reflectance = 0.3


def test_duplicate():
    """Test what happens to radiance properties when duplicating a Room."""
    custom_set = ModifierSet('Custom_Modifier_Set')
    room_original = Room.from_box('Shoe_Box', 5, 10, 3)
    room_original.properties.radiance.modifier_set = generic_modifier_set_visible_exterior

    room_dup_1 = room_original.duplicate()

    assert room_original.properties.radiance.modifier_set == \
        room_dup_1.properties.radiance.modifier_set

    assert room_original.properties.radiance.host is room_original
    assert room_dup_1.properties.radiance.host is room_dup_1
    assert room_original.properties.radiance.host is not \
        room_dup_1.properties.radiance.host

    assert room_original.properties.radiance.modifier_set == \
        room_dup_1.properties.radiance.modifier_set
    room_dup_1.properties.radiance.modifier_set = custom_set
    assert room_original.properties.radiance.modifier_set != \
        room_dup_1.properties.radiance.modifier_set

    prefix ='Opt1'
    room_dup_1.add_prefix('Opt1')
    assert room_dup_1.identifier.startswith('Opt1')

    room_dup_2 = room_dup_1.duplicate()

    assert room_dup_1.properties.radiance.modifier_set == \
        room_dup_2.properties.radiance.modifier_set
    room_dup_2.properties.radiance.modifier_set = None
    assert room_dup_1.properties.radiance.modifier_set != \
        room_dup_2.properties.radiance.modifier_set


def test_to_dict():
    """Test the Room to_dict method with radiance properties."""
    custom_set = ModifierSet('Custom_Modifier_Set')
    room = Room.from_box('Shoe_Box', 5, 10, 3)

    rd = room.to_dict()
    assert 'properties' in rd
    assert rd['properties']['type'] == 'RoomProperties'
    assert 'radiance' in rd['properties']
    assert rd['properties']['radiance']['type'] == 'RoomRadianceProperties'
    assert 'modifier_set' not in rd['properties']['radiance'] or \
        rd['properties']['radiance']['modifier_set'] is None

    room.properties.radiance.modifier_set = custom_set
    rd = room.to_dict()
    assert rd['properties']['radiance']['modifier_set'] is not None


def test_from_dict():
    """Test the Room from_dict method with radiance properties."""
    custom_set = ModifierSet('CustomModifierSet')
    room = Room.from_box('Shoe_Box', 5, 10, 3)
    room.properties.radiance.modifier_set = custom_set

    rd = room.to_dict()
    new_room = Room.from_dict(rd)
    assert new_room.properties.radiance.modifier_set.identifier == 'CustomModifierSet'
    assert new_room.to_dict() == rd


def test_writer_to_rad():
    """Test the Room to_rad method."""
    room = Room.from_box('ClosedOffice', 5, 10, 3)
    custom_set = ModifierSet('Custom_Modifier_Set')
    concrete = Plastic.from_single_reflectance('035Concrete', 0.35)
    custom_set.wall_set.exterior_modifier = concrete
    room.properties.radiance.modifier_set = custom_set

    assert hasattr(room.to, 'rad')
    rad_string = room.to.rad(room)
    assert '035Concrete' in rad_string
