"""Tests the features that honeybee_radiance adds to honeybee_core Model."""
from honeybee.model import Model
from honeybee.room import Room
from honeybee.face import Face
from honeybee.shade import Shade
from honeybee.aperture import Aperture
from honeybee.door import Door
from honeybee.boundarycondition import boundary_conditions, Ground, Outdoors
from honeybee.facetype import face_types

from honeybee_radiance.properties.model import ModelRadianceProperties
from honeybee_radiance.modifierset import ModifierSet
from honeybee_radiance.modifier import Modifier
from honeybee_radiance.modifier.material import Plastic, Glass

from honeybee_radiance.lib.modifiers import generic_floor, generic_wall, \
    generic_ceiling, generic_door, generic_exterior_window, generic_interior_window, \
    generic_exterior_shade, generic_interior_shade, air_boundary

from ladybug_geometry.geometry3d.pointvector import Point3D, Vector3D
from ladybug_geometry.geometry3d.plane import Plane
from ladybug_geometry.geometry3d.face import Face3D

import pytest


def test_radiance_properties():
    """Test the existence of the Model radiance properties."""
    room = Room.from_box('TinyHouseRoom', 5, 10, 3)
    south_face = room[3]
    south_face.apertures_by_ratio(0.4, 0.01)
    south_face.apertures[0].overhang(0.5, indoor=False)
    south_face.apertures[0].overhang(0.5, indoor=True)
    south_face.apertures[0].move_shades(Vector3D(0, 0, -0.5))
    fritted_glass_trans = Glass.from_single_transmittance('FrittedGlass', 0.35)
    south_face.apertures[0].outdoor_shades[0].properties.radiance.modifier = \
        fritted_glass_trans
    model = Model('TinyHouse', [room])

    assert hasattr(model.properties, 'radiance')
    assert isinstance(model.properties.radiance, ModelRadianceProperties)
    assert isinstance(model.properties.host, Model)
    assert len(model.properties.radiance.modifiers) == 10
    assert len(model.properties.radiance.blk_modifiers) == 1
    for mat in model.properties.radiance.modifiers:
        assert isinstance(mat, Modifier)
    assert len(model.properties.radiance.face_modifiers) == 0
    assert len(model.properties.radiance.modifier_sets) == 0
    assert isinstance(model.properties.radiance.global_modifier_set, ModifierSet)


def test_check_duplicate_modifier_set_identifiers():
    """Test the check_duplicate_modifier_set_identifiers method."""
    first_floor = Room.from_box('FirstFloor', 10, 10, 3, origin=Point3D(0, 0, 0))
    second_floor = Room.from_box('SecondFloor', 10, 10, 3, origin=Point3D(0, 0, 3))
    for face in first_floor[1:5]:
        face.apertures_by_ratio(0.2, 0.01)
    for face in second_floor[1:5]:
        face.apertures_by_ratio(0.2, 0.01)

    pts_1 = [Point3D(0, 0, 6), Point3D(0, 10, 6), Point3D(10, 10, 6), Point3D(10, 0, 6)]
    pts_2 = [Point3D(0, 0, 6), Point3D(5, 0, 9), Point3D(5, 10, 9), Point3D(0, 10, 6)]
    pts_3 = [Point3D(10, 0, 6), Point3D(10, 10, 6), Point3D(5, 10, 9), Point3D(5, 0, 9)]
    pts_4 = [Point3D(0, 0, 6), Point3D(10, 0, 6), Point3D(5, 0, 9)]
    pts_5 = [Point3D(10, 10, 6), Point3D(0, 10, 6), Point3D(5, 10, 9)]
    face_1 = Face('AtticFace1', Face3D(pts_1))
    face_2 = Face('AtticFace2', Face3D(pts_2))
    face_3 = Face('AtticFace3', Face3D(pts_3))
    face_4 = Face('AtticFace4', Face3D(pts_4))
    face_5 = Face('AtticFace5', Face3D(pts_5))
    attic = Room('Attic', [face_1, face_2, face_3, face_4, face_5], 0.01, 1)

    mod_set = ModifierSet('Attic_Construction_Set')
    mod_set.floor_set.interior_modifier = Plastic('AtticFloor', 0.4)
    mod_set.roof_ceiling_set.exterior_modifier = Plastic('AtticRoof', 0.6)
    attic.properties.radiance.modifier_set = mod_set

    Room.solve_adjacency([first_floor, second_floor, attic], 0.01)

    model = Model('Multi_Zone_Single_Family_House', [first_floor, second_floor, attic])

    assert model.properties.radiance.check_duplicate_modifier_set_identifiers(False)
    mod_set.unlock()
    mod_set.identifier = 'Generic_Interior_Visible_Modifier_Set'
    mod_set.lock()
    assert not model.properties.radiance.check_duplicate_modifier_set_identifiers(False)
    with pytest.raises(ValueError):
        model.properties.radiance.check_duplicate_modifier_set_identifiers(True)


def test_check_duplicate_modifier_identifiers():
    """Test the check_duplicate_modifier_identifiers method."""
    room = Room.from_box('Tiny_House_Zone', 5, 10, 3)

    high_ref_ceil = Plastic.from_single_reflectance('CustomModifier', 0.9)
    room[-1].properties.radiance.modifier = high_ref_ceil

    north_face = room[1]
    aperture_verts = [Point3D(4.5, 10, 1), Point3D(2.5, 10, 1),
                      Point3D(2.5, 10, 2.5), Point3D(4.5, 10, 2.5)]
    aperture = Aperture('Front_Aperture', Face3D(aperture_verts))
    aperture.is_operable = True
    triple_pane = Glass.from_single_transmittance('CustomTriplePane', 0.3)
    aperture.properties.radiance.modifier = triple_pane
    north_face.add_aperture(aperture)

    model = Model('Tiny_House', [room])

    assert model.properties.radiance.check_duplicate_modifier_identifiers(False)
    triple_pane.unlock()
    triple_pane.identifier = 'CustomModifier'
    triple_pane.lock()
    assert not model.properties.radiance.check_duplicate_modifier_identifiers(False)
    with pytest.raises(ValueError):
        model.properties.radiance.check_duplicate_modifier_identifiers(True)


def test_to_from_dict():
    """Test the Model to_dict and from_dict method with a single zone model."""
    room = Room.from_box('Tiny_House_Room', 5, 10, 3)

    dark_floor = Plastic.from_single_reflectance('DarkFloor', 0.1)
    room[0].properties.radiance.modifier = dark_floor

    south_face = room[3]
    south_face.apertures_by_ratio(0.4, 0.01)
    south_face.apertures[0].overhang(0.5, indoor=False)
    south_face.apertures[0].overhang(0.5, indoor=True)
    south_face.apertures[0].move_shades(Vector3D(0, 0, -0.5))
    light_shelf_out = Plastic.from_single_reflectance('OutdoorLightShelf', 0.5)
    light_shelf_in = Plastic.from_single_reflectance('IndoorLightShelf', 0.7)
    south_face.apertures[0].shades[0].properties.radiance.modifier = light_shelf_out
    south_face.apertures[0].shades[1].properties.radiance.modifier = light_shelf_in

    north_face = room[1]
    door_verts = [Point3D(2, 10, 0.1), Point3D(1, 10, 0.1),
                  Point3D(1, 10, 2.5), Point3D(2, 10, 2.5)]
    door = Door('FrontDoor', Face3D(door_verts))
    north_face.add_door(door)

    aperture_verts = [Point3D(4.5, 10, 1), Point3D(2.5, 10, 1),
                      Point3D(2.5, 10, 2.5), Point3D(4.5, 10, 2.5)]
    aperture = Aperture('FrontAperture', Face3D(aperture_verts))
    aperture.is_operable = True
    triple_pane = Glass.from_single_transmittance('CustomTriplePane', 0.3)
    aperture.properties.radiance.modifier = triple_pane
    north_face.add_aperture(aperture)

    tree_canopy_geo = Face3D.from_regular_polygon(
        6, 2, Plane(Vector3D(0, 0, 1), Point3D(5, -3, 4)))
    tree_canopy = Shade('TreeCanopy', tree_canopy_geo)
    tree_trans = Glass.from_single_transmittance('TreeTransmittance', 0.75)
    tree_canopy.properties.radiance.modifier = tree_trans

    model = Model('TinyHouse', [room], orphaned_shades=[tree_canopy])
    model.north_angle = 15
    model_dict = model.to_dict(included_prop=['radiance'])
    new_model = Model.from_dict(model_dict)
    assert model_dict == new_model.to_dict(included_prop=['radiance'])

    assert dark_floor in new_model.properties.radiance.modifiers
    assert new_model.rooms[0][0].properties.radiance.modifier == dark_floor
    assert new_model.rooms[0][3].apertures[0].indoor_shades[0].properties.radiance.modifier == light_shelf_in
    assert new_model.rooms[0][3].apertures[0].outdoor_shades[0].properties.radiance.modifier == light_shelf_out
    assert triple_pane in new_model.properties.radiance.modifiers
    assert new_model.rooms[0][1].apertures[0].properties.radiance.modifier == triple_pane
    assert new_model.rooms[0][1].apertures[0].is_operable
    assert len(new_model.orphaned_shades) == 1
    assert new_model.north_angle == 15

    assert new_model.rooms[0][0].type == face_types.floor
    assert new_model.rooms[0][1].type == face_types.wall
    assert isinstance(new_model.rooms[0][0].boundary_condition, Ground)
    assert isinstance(new_model.rooms[0][1].boundary_condition, Outdoors)
    assert new_model.orphaned_shades[0].properties.radiance.modifier == tree_trans


def test_to_dict_single_zone():
    """Test the Model to_dict method with a single zone model."""
    room = Room.from_box('Tiny_House_Zone', 5, 10, 3)

    dark_floor = Plastic.from_single_reflectance('DarkFloor', 0.1)
    room[0].properties.radiance.modifier = dark_floor

    south_face = room[3]
    south_face.apertures_by_ratio(0.4, 0.01)
    south_face.apertures[0].overhang(0.5, indoor=False)
    south_face.apertures[0].overhang(0.5, indoor=True)
    south_face.move_shades(Vector3D(0, 0, -0.5))
    light_shelf_out = Plastic.from_single_reflectance('OutdoorLightShelf', 0.5)
    light_shelf_in = Plastic.from_single_reflectance('IndoorLightShelf', 0.7)
    south_face.apertures[0].outdoor_shades[0].properties.radiance.modifier = light_shelf_out
    south_face.apertures[0].indoor_shades[0].properties.radiance.modifier = light_shelf_in

    north_face = room[1]
    north_face.overhang(0.25, indoor=False)
    door_verts = [Point3D(2, 10, 0.1), Point3D(1, 10, 0.1),
                  Point3D(1, 10, 2.5), Point3D(2, 10, 2.5)]
    door = Door('Front_Door', Face3D(door_verts))
    north_face.add_door(door)

    aperture_verts = [Point3D(4.5, 10, 1), Point3D(2.5, 10, 1),
                      Point3D(2.5, 10, 2.5), Point3D(4.5, 10, 2.5)]
    aperture = Aperture('Front_Aperture', Face3D(aperture_verts))
    triple_pane = Glass.from_single_transmittance('CustomTriplePane', 0.3)
    aperture.properties.radiance.modifier = triple_pane
    north_face.add_aperture(aperture)

    tree_canopy_geo = Face3D.from_regular_polygon(
        6, 2, Plane(Vector3D(0, 0, 1), Point3D(5, -3, 4)))
    tree_canopy = Shade('Tree_Canopy', tree_canopy_geo)

    table_geo = Face3D.from_rectangle(2, 2, Plane(o=Point3D(1.5, 4, 1)))
    table = Shade('Table', table_geo)
    room.add_indoor_shade(table)

    model = Model('Tiny_House', [room], orphaned_shades=[tree_canopy])
    model.north_angle = 15

    model_dict = model.to_dict()

    assert 'radiance' in model_dict['properties']
    assert 'modifiers' in model_dict['properties']['radiance']
    assert 'modifier_sets' in model_dict['properties']['radiance']
    assert 'global_modifier_set' in model_dict['properties']['radiance']

    assert len(model_dict['properties']['radiance']['modifiers']) == 14
    assert len(model_dict['properties']['radiance']['modifier_sets']) == 1

    assert model_dict['rooms'][0]['faces'][0]['properties']['radiance']['modifier'] == \
        dark_floor.identifier
    south_ap_dict = model_dict['rooms'][0]['faces'][3]['apertures'][0]
    assert south_ap_dict['outdoor_shades'][0]['properties']['radiance']['modifier'] == \
        light_shelf_out.identifier
    assert south_ap_dict['indoor_shades'][0]['properties']['radiance']['modifier'] == \
        light_shelf_in.identifier
    assert model_dict['rooms'][0]['faces'][1]['apertures'][0]['properties']['radiance']['modifier'] == \
        triple_pane.identifier


def test_to_dict_multizone_house():
    """Test the Model to_dict method with a multi-zone house."""
    first_floor = Room.from_box('First_Floor', 10, 10, 3, origin=Point3D(0, 0, 0))
    second_floor = Room.from_box('Second_Floor', 10, 10, 3, origin=Point3D(0, 0, 3))
    for face in first_floor[1:5]:
        face.apertures_by_ratio(0.2, 0.01)
    for face in second_floor[1:5]:
        face.apertures_by_ratio(0.2, 0.01)

    pts_1 = [Point3D(0, 0, 6), Point3D(0, 10, 6), Point3D(10, 10, 6), Point3D(10, 0, 6)]
    pts_2 = [Point3D(0, 0, 6), Point3D(5, 0, 9), Point3D(5, 10, 9), Point3D(0, 10, 6)]
    pts_3 = [Point3D(10, 0, 6), Point3D(10, 10, 6), Point3D(5, 10, 9), Point3D(5, 0, 9)]
    pts_4 = [Point3D(0, 0, 6), Point3D(10, 0, 6), Point3D(5, 0, 9)]
    pts_5 = [Point3D(10, 10, 6), Point3D(0, 10, 6), Point3D(5, 10, 9)]
    face_1 = Face('AtticFace1', Face3D(pts_1))
    face_2 = Face('AtticFace2', Face3D(pts_2))
    face_3 = Face('AtticFace3', Face3D(pts_3))
    face_4 = Face('AtticFace4', Face3D(pts_4))
    face_5 = Face('AtticFace5', Face3D(pts_5))
    attic = Room('Attic', [face_1, face_2, face_3, face_4, face_5], 0.01, 1)

    mod_set = ModifierSet('Attic_Construction_Set')
    mod_set.floor_set.interior_modifier = Plastic('AtticFloor', 0.4)
    mod_set.roof_ceiling_set.exterior_modifier = Plastic('AtticRoof', 0.6)
    attic.properties.radiance.modifier_set = mod_set

    Room.solve_adjacency([first_floor, second_floor, attic], 0.01)

    model = Model('Multi_Zone_Single_Family_House', [first_floor, second_floor, attic])
    model_dict = model.to_dict()

    assert 'radiance' in model_dict['properties']
    assert 'modifiers' in model_dict['properties']['radiance']
    assert 'modifier_sets' in model_dict['properties']['radiance']
    assert 'global_modifier_set' in model_dict['properties']['radiance']

    assert len(model_dict['properties']['radiance']['modifiers']) == 11
    assert len(model_dict['properties']['radiance']['modifier_sets']) == 2

    assert model_dict['rooms'][0]['faces'][5]['boundary_condition']['type'] == 'Surface'
    assert model_dict['rooms'][1]['faces'][0]['boundary_condition']['type'] == 'Surface'
    assert model_dict['rooms'][1]['faces'][5]['boundary_condition']['type'] == 'Surface'
    assert model_dict['rooms'][2]['faces'][0]['boundary_condition']['type'] == 'Surface'

    assert model_dict['rooms'][2]['properties']['radiance']['modifier_set'] == \
        mod_set.identifier


def test_writer_to_rad():
    """Test the Model to.rad method."""
    room = Room.from_box('Tiny_House_Zone', 5, 10, 3)

    dark_floor = Plastic.from_single_reflectance('DarkFloor', 0.1)
    room[0].properties.radiance.modifier = dark_floor

    south_face = room[3]
    south_face.apertures_by_ratio(0.4, 0.01)
    south_face.apertures[0].overhang(0.5, indoor=False)
    south_face.apertures[0].overhang(0.5, indoor=True)
    south_face.move_shades(Vector3D(0, 0, -0.5))
    light_shelf_out = Plastic.from_single_reflectance('outdoor_light_shelf_0.5', 0.5)
    light_shelf_in = Plastic.from_single_reflectance('indoor_light_shelf_0.70', 0.7)
    south_face.apertures[0].outdoor_shades[0].properties.radiance.modifier = light_shelf_out
    south_face.apertures[0].indoor_shades[0].properties.radiance.modifier = light_shelf_in

    north_face = room[1]
    north_face.overhang(0.25, indoor=False)
    door_verts = [Point3D(2, 10, 0.1), Point3D(1, 10, 0.1),
                  Point3D(1, 10, 2.5), Point3D(2, 10, 2.5)]
    door = Door('Front_Door', Face3D(door_verts))
    north_face.add_door(door)

    aperture_verts = [Point3D(4.5, 10, 1), Point3D(2.5, 10, 1),
                      Point3D(2.5, 10, 2.5), Point3D(4.5, 10, 2.5)]
    aperture = Aperture('Front_Aperture', Face3D(aperture_verts))
    triple_pane = Glass.from_single_transmittance('custom_triple_pane_0.3', 0.3)
    aperture.properties.radiance.modifier = triple_pane
    north_face.add_aperture(aperture)

    tree_canopy_geo = Face3D.from_regular_polygon(
        6, 2, Plane(Vector3D(0, 0, 1), Point3D(5, -3, 4)))
    tree_canopy = Shade('Tree_Canopy', tree_canopy_geo)

    table_geo = Face3D.from_rectangle(2, 2, Plane(o=Point3D(1.5, 4, 1)))
    table = Shade('Table', table_geo)
    room.add_indoor_shade(table)

    model = Model('Tiny_House', [room], orphaned_shades=[tree_canopy])
    model.north_angle = 15

    assert hasattr(model.to, 'rad')
    rad_string = model.to.rad(model)
