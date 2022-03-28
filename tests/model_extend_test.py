"""Tests the features that honeybee_radiance adds to honeybee_core Model."""
from honeybee.model import Model
from honeybee.room import Room
from honeybee.face import Face
from honeybee.shade import Shade
from honeybee.aperture import Aperture
from honeybee.door import Door
from honeybee.boundarycondition import Ground, Outdoors
from honeybee.facetype import face_types

from honeybee_radiance.properties.model import ModelRadianceProperties
from honeybee_radiance.dynamic import RadianceSubFaceState, RadianceShadeState, \
    StateGeometry
from honeybee_radiance.modifierset import ModifierSet
from honeybee_radiance.modifier import Modifier
from honeybee_radiance.modifier.material import Plastic, Glass, Trans, BSDF

from honeybee_radiance_folder.folder import ModelFolder
from ladybug.futil import nukedir
from ladybug_geometry.geometry3d.pointvector import Point3D, Vector3D
from ladybug_geometry.geometry3d.plane import Plane
from ladybug_geometry.geometry3d.face import Face3D

import os
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
    assert len(model.properties.radiance.modifiers) == 1
    assert len(model.properties.radiance.blk_modifiers) == 1
    for mat in model.properties.radiance.modifiers:
        assert isinstance(mat, Modifier)
    assert len(model.properties.radiance.face_modifiers) == 0
    assert len(model.properties.radiance.modifier_sets) == 0


def test_check_duplicate_modifier_set_identifiers():
    """Test the check_duplicate_modifier_set_identifiers method."""
    first_floor = Room.from_box('FirstFloor', 10, 10, 3, origin=Point3D(0, 0, 0))
    second_floor = Room.from_box('SecondFloor', 10, 10, 3, origin=Point3D(0, 0, 3))
    for face in first_floor[1:5]:
        face.apertures_by_ratio(0.2, 0.01)
    for face in second_floor[1:5]:
        face.apertures_by_ratio(0.2, 0.01)
    mod_set_bottom = ModifierSet('Lower_Floor_Modifier_Set')
    first_floor.properties.radiance.modifier_set = mod_set_bottom
    second_floor.properties.radiance.modifier_set = mod_set_bottom

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

    mod_set = ModifierSet('Attic_Modifier_Set')
    mod_set.floor_set.interior_modifier = Plastic('AtticFloor', 0.4)
    mod_set.roof_ceiling_set.exterior_modifier = Plastic('AtticRoof', 0.6)
    attic.properties.radiance.modifier_set = mod_set

    Room.solve_adjacency([first_floor, second_floor, attic], 0.01)

    model = Model('Multi_Zone_Single_Family_House', [first_floor, second_floor, attic])

    assert model.properties.radiance.check_duplicate_modifier_set_identifiers(False) == ''
    mod_set.unlock()
    mod_set.identifier = 'Lower_Floor_Modifier_Set'
    mod_set.lock()
    assert model.properties.radiance.check_duplicate_modifier_set_identifiers(False) != ''
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

    assert model.properties.radiance.check_duplicate_modifier_identifiers(False) == ''
    triple_pane.unlock()
    triple_pane.identifier = 'CustomModifier'
    triple_pane.lock()
    assert model.properties.radiance.check_duplicate_modifier_identifiers(False) != ''
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

    model_dict = model.to_dict()

    assert 'radiance' in model_dict['properties']
    assert 'modifiers' in model_dict['properties']['radiance']
    assert 'modifier_sets' in model_dict['properties']['radiance']

    assert len(model_dict['properties']['radiance']['modifiers']) == 5
    assert len(model_dict['properties']['radiance']['modifier_sets']) == 0

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

    assert len(model_dict['properties']['radiance']['modifiers']) == 2
    assert len(model_dict['properties']['radiance']['modifier_sets']) == 1

    assert model_dict['rooms'][0]['faces'][5]['boundary_condition']['type'] == 'Surface'
    assert model_dict['rooms'][1]['faces'][0]['boundary_condition']['type'] == 'Surface'
    assert model_dict['rooms'][1]['faces'][5]['boundary_condition']['type'] == 'Surface'
    assert model_dict['rooms'][2]['faces'][0]['boundary_condition']['type'] == 'Surface'

    assert model_dict['rooms'][2]['properties']['radiance']['modifier_set'] == \
        mod_set.identifier


def test_load_dump_properties_from_dict():
    """Test the Model load / dump properties_from_dict."""
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

    modifiers, modifier_sets = \
        model.properties.radiance.load_properties_from_dict(model_dict)

    new_prop_dict = model.properties.radiance.dump_properties_to_dict(
        modifiers.values(), modifier_sets.values())

    for key in new_prop_dict:
        if isinstance(new_prop_dict[key], list):
            for item in model_dict['properties']['radiance'][key]:
                assert item in new_prop_dict[key]
        else:
            assert new_prop_dict[key] == model_dict['properties']['radiance'][key]


def test_to_dict_sensor_grids_views():
    """Test the Model to_dict method with assigned sensor grids and views."""
    room = Room.from_box('Tiny_House_Zone', 5, 10, 3)
    garage = Room.from_box('Tiny_Garage', 5, 10, 3, origin=Point3D(5, 0, 0))

    south_face = room[3]
    south_face.apertures_by_ratio(0.4, 0.01)
    south_face.apertures[0].overhang(0.5, indoor=False)
    south_face.apertures[0].overhang(0.5, indoor=True)
    south_face.move_shades(Vector3D(0, 0, -0.5))
    north_face = garage[1]
    north_face.apertures_by_ratio(0.1, 0.01)

    room_grid = room.properties.radiance.generate_sensor_grid(0.5, 0.5, 1)
    garage_grid = garage.properties.radiance.generate_sensor_grid(0.5, 0.5, 1)
    room_view = room.properties.radiance.generate_view((0, -1, 0))
    garage_view = garage.properties.radiance.generate_view((0, 1, 0))

    Room.solve_adjacency([room, garage], 0.01)

    model = Model('Tiny_House', [room, garage])
    model.properties.radiance.sensor_grids = [room_grid]
    model.properties.radiance.add_sensor_grids([garage_grid])
    model.properties.radiance.views = [room_view]
    model.properties.radiance.add_views([garage_view])

    model_dict = model.to_dict(included_prop=['radiance'])

    assert 'sensor_grids' in model_dict['properties']['radiance']
    assert 'views' in model_dict['properties']['radiance']
    assert len(model_dict['properties']['radiance']['sensor_grids']) == 2
    assert len(model_dict['properties']['radiance']['views']) == 2

    new_model = Model.from_dict(model_dict)
    assert new_model.properties.radiance.has_sensor_grids
    assert new_model.properties.radiance.has_views
    assert len(new_model.properties.radiance.sensor_grids) == 2
    assert len(new_model.properties.radiance.views) == 2
    assert model_dict == new_model.to_dict(included_prop=['radiance'])


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

    assert hasattr(model.to, 'rad')
    rad_string = model.to.rad(model)
    assert len(rad_string) == 2
    assert 'outdoor_light_shelf_0.5' in rad_string[1]
    assert 'Front_Door' in rad_string[0]


def test_writer_to_rad_folder():
    """Test the Model to.rad_folder method."""
    room = Room.from_box('Tiny_House_Zone', 5, 10, 3)
    garage = Room.from_box('Tiny_Garage', 5, 10, 3, origin=Point3D(5, 0, 0))

    dark_floor = Plastic.from_single_reflectance('DarkFloor', 0.1)
    room[0].properties.radiance.modifier = dark_floor
    room[5].properties.radiance.modifier_blk = dark_floor

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
    tree_trans = Trans.from_single_reflectance('Leaves', 0.3, 0.0, 0.1, 0.15, 0.15)
    tree_canopy.properties.radiance.modifier = tree_trans

    table_geo = Face3D.from_rectangle(2, 2, Plane(o=Point3D(1.5, 4, 1)))
    table = Shade('Table', table_geo)
    room.add_indoor_shade(table)

    east_face = room[2]
    east_face.apertures_by_ratio(0.1, 0.01)
    west_face = garage[4]
    west_face.apertures_by_ratio(0.1, 0.01)
    Room.solve_adjacency([room, garage], 0.01)

    model = Model('Tiny_House', [room, garage], orphaned_shades=[tree_canopy])

    folder = os.path.abspath('./tests/assets/model/rad_folder')
    model.to.rad_folder(model, folder)

    model_folder = ModelFolder(folder)

    ap_dir = model_folder.aperture_folder(full=True)
    assert os.path.isfile(os.path.join(ap_dir, 'aperture.rad'))
    assert os.path.isfile(os.path.join(ap_dir, 'aperture.mat'))
    assert os.path.isfile(os.path.join(ap_dir, 'aperture.blk'))

    scene_dir = model_folder.scene_folder(full=True)
    assert os.path.isfile(os.path.join(scene_dir, 'envelope.rad'))
    assert os.path.isfile(os.path.join(scene_dir, 'envelope.mat'))
    assert os.path.isfile(os.path.join(scene_dir, 'envelope.blk'))
    assert os.path.isfile(os.path.join(scene_dir, 'shades.rad'))
    assert os.path.isfile(os.path.join(scene_dir, 'shades.mat'))
    assert os.path.isfile(os.path.join(scene_dir, 'shades.blk'))

    # clean up the folder
    nukedir(folder, rmdir=True)


def test_writer_to_rad_folder_dynamic():
    """Test the Model to.rad_folder method with dynamic geometry."""
    room = Room.from_box('Tiny_House_Zone', 5, 10, 3)
    garage = Room.from_box('Tiny_Garage', 5, 10, 3, origin=Point3D(5, 0, 0))

    south_face = room[3]
    south_face.apertures_by_ratio(0.5, 0.01)
    shd1 = StateGeometry.from_vertices(
        'outdoor_awning', [[0, 0, 2], [5, 0, 2], [5, 2, 2], [0, 2, 2]])

    ecglass1 = Glass.from_single_transmittance('ElectrochromicState1', 0.4)
    ecglass2 = Glass.from_single_transmittance('ElectrochromicState2', 0.27)
    ecglass3 = Glass.from_single_transmittance('ElectrochromicState3', 0.14)
    ecglass4 = Glass.from_single_transmittance('ElectrochromicState4', 0.01)

    tint1 = RadianceSubFaceState(ecglass1)
    tint2 = RadianceSubFaceState(ecglass2)
    tint3 = RadianceSubFaceState(ecglass3, [shd1])
    tint4 = RadianceSubFaceState(ecglass4, [shd1.duplicate()])
    states = (tint1, tint2, tint3, tint4)
    south_face.apertures[0].properties.radiance.dynamic_group_identifier = \
        'ElectrochromicWindow'
    south_face.apertures[0].properties.radiance.states = states

    shd2 = Shade.from_vertices(
        'indoor_light_shelf', [[0, 0, 2], [-1, 0, 2], [-1, 2, 2], [0, 2, 2]])
    ref_1 = Plastic.from_single_reflectance('outdoor_light_shelf_0.5', 0.5)
    ref_2 = Plastic.from_single_reflectance('indoor_light_shelf_0.70', 0.7)
    light_shelf_1 = RadianceShadeState(ref_1)
    light_shelf_2 = RadianceShadeState(ref_2)
    shelf_states = (light_shelf_1, light_shelf_2)
    shd2.properties.radiance.dynamic_group_identifier = 'DynamicLightShelf'
    shd2.properties.radiance.states = shelf_states
    room.add_indoor_shade(shd2)

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
    sum_tree_trans = Trans.from_single_reflectance('SummerLeaves', 0.3, 0.0, 0.1, 0.15, 0.15)
    win_tree_trans = Trans.from_single_reflectance('WinterLeaves', 0.1, 0.0, 0.1, 0.1, 0.6)
    summer = RadianceShadeState(sum_tree_trans)
    winter = RadianceShadeState(win_tree_trans)
    tree_canopy.properties.radiance.dynamic_group_identifier = 'DeciduousTree'
    tree_canopy.properties.radiance.states = (summer, winter)

    ground_geo = Face3D.from_rectangle(10, 10, Plane(o=Point3D(0, -10, 0)))
    ground = Shade('Ground', ground_geo)
    grass = Plastic.from_single_reflectance('grass', 0.3)
    snow = Plastic.from_single_reflectance('snow', 0.7)
    summer_ground = RadianceShadeState(grass)
    winter_ground = RadianceShadeState(snow)
    ground.properties.radiance.dynamic_group_identifier = 'SeasonalGround'
    ground.properties.radiance.states = (summer_ground, winter_ground)

    east_face = room[2]
    east_face.apertures_by_ratio(0.1, 0.01)
    west_face = garage[4]
    west_face.apertures_by_ratio(0.1, 0.01)
    Room.solve_adjacency([room, garage], 0.01)

    model = Model('Tiny_House', [room, garage], orphaned_shades=[ground, tree_canopy])

    folder = os.path.abspath('./tests/assets/model/rad_folder_dynamic')
    model.to.rad_folder(model, folder)

    model_folder = ModelFolder(folder)

    ap_dir = model_folder.aperture_group_folder(full=True)
    assert os.path.isfile(os.path.join(ap_dir, 'states.json'))
    group_name = south_face.apertures[0].properties.radiance.dynamic_group_identifier
    assert os.path.isfile(os.path.join(ap_dir, '{}..black.rad'.format(group_name)))
    for i in range(len(south_face.apertures[0].properties.radiance.states)):
        d_file = (os.path.join(ap_dir, '{}..default..{}.rad'.format(group_name, i)))
        assert os.path.isfile(d_file)
    for i in range(len(south_face.apertures[0].properties.radiance.states)):
        d_file = (os.path.join(ap_dir, '{}..direct..{}.rad'.format(group_name, i)))
        assert os.path.isfile(d_file)

    out_scene_dir = model_folder.dynamic_scene_folder(full=True, indoor=False)
    assert os.path.isfile(os.path.join(out_scene_dir, 'states.json'))
    grp_name = tree_canopy.properties.radiance.dynamic_group_identifier
    for i in range(len(tree_canopy.properties.radiance.states)):
        d_file = (os.path.join(out_scene_dir, '{}..default..{}.rad'.format(grp_name, i)))
        assert os.path.isfile(d_file)
    for i in range(len(tree_canopy.properties.radiance.states)):
        d_file = (os.path.join(out_scene_dir, '{}..direct..{}.rad'.format(grp_name, i)))
        assert os.path.isfile(d_file)
    grp_name = ground.properties.radiance.dynamic_group_identifier
    for i in range(len(ground.properties.radiance.states)):
        d_file = (os.path.join(out_scene_dir, '{}..default..{}.rad'.format(grp_name, i)))
        assert os.path.isfile(d_file)
    for i in range(len(ground.properties.radiance.states)):
        d_file = (os.path.join(out_scene_dir, '{}..direct..{}.rad'.format(grp_name, i)))
        d_file = (os.path.join(out_scene_dir, '{}..direct..{}.rad'.format(grp_name, i)))
        assert os.path.isfile(d_file)

    in_scene_dir = model_folder.dynamic_scene_folder(full=True, indoor=True)
    assert os.path.isfile(os.path.join(in_scene_dir, 'states.json'))
    grp_name = shd2.properties.radiance.dynamic_group_identifier
    for i in range(len(shd2.properties.radiance.states)):
        d_file = (os.path.join(in_scene_dir, '{}..default..{}.rad'.format(grp_name, i)))
        assert os.path.isfile(d_file)
    for i in range(len(shd2.properties.radiance.states)):
        d_file = (os.path.join(in_scene_dir, '{}..direct..{}.rad'.format(grp_name, i)))
        assert os.path.isfile(d_file)

    # clean up the folder
    nukedir(folder, rmdir=True)


def test_writer_to_rad_folder_multiphase():
    """Test the Model to.rad_folder method with multi-phase objects like BSDFs."""
    room = Room.from_box('Tiny_House_Zone', 5, 10, 3)
    south_face = room[3]
    south_face.apertures_by_ratio(0.5, 0.01)
    south_aperture = south_face.apertures[0]
    north_face = room[1]
    north_face.apertures_by_ratio(0.5, 0.01)
    north_aperture = north_face.apertures[0]

    folder = os.path.abspath('./tests/assets/')
    clear_bsdf = BSDF(os.path.join(folder, 'clear.xml'))
    diff_bsdf = BSDF(os.path.join(folder, 'diffuse50.xml'))
    clear = RadianceSubFaceState(clear_bsdf)
    diffuse = RadianceSubFaceState(diff_bsdf)

    south_aperture.properties.radiance.dynamic_group_identifier = 'SouthDynamicWindow'
    south_aperture.properties.radiance.states = [clear, diffuse]
    north_aperture.properties.radiance.dynamic_group_identifier = 'NorthDynamicWindow'
    north_aperture.properties.radiance.states = [clear.duplicate(), diffuse.duplicate()]
    north_aperture.properties.radiance.states[0].gen_geos_from_tmtx_thickness(0.1)
    north_aperture.properties.radiance.states[1].gen_geos_from_tmtx_thickness(0.2)

    model = Model('Tiny_House', [room])

    folder = os.path.abspath('./tests/assets/model/rad_folder_multiphase')
    model.to.rad_folder(model, folder)

    model_folder = ModelFolder(folder)

    bsdf_dir = model_folder.bsdf_folder(full=True)
    assert os.path.isfile(os.path.join(bsdf_dir, 'clear.xml'))
    assert os.path.isfile(os.path.join(bsdf_dir, 'diffuse50.xml'))

    ap_dir = model_folder.aperture_group_folder(full=True)
    assert os.path.isfile(os.path.join(ap_dir, 'states.json'))

    group_name = south_aperture.properties.radiance.dynamic_group_identifier
    assert os.path.isfile(os.path.join(ap_dir, '{}..black.rad'.format(group_name)))
    assert os.path.isfile(os.path.join(ap_dir, '{}..mtx.rad'.format(group_name)))
    for i in range(len(south_aperture.properties.radiance.states)):
        d_file = (os.path.join(ap_dir, '{}..default..{}.rad'.format(group_name, i)))
        assert os.path.isfile(d_file)
    for i in range(len(south_aperture.properties.radiance.states)):
        d_file = (os.path.join(ap_dir, '{}..direct..{}.rad'.format(group_name, i)))
        assert os.path.isfile(d_file)

    group_name = north_aperture.properties.radiance.dynamic_group_identifier
    assert os.path.isfile(os.path.join(ap_dir, '{}..black.rad'.format(group_name)))
    for i in range(len(north_aperture.properties.radiance.states)):
        d_file = (os.path.join(ap_dir, '{}..default..{}.rad'.format(group_name, i)))
        assert os.path.isfile(d_file)
    for i in range(len(north_aperture.properties.radiance.states)):
        d_file = (os.path.join(ap_dir, '{}..direct..{}.rad'.format(group_name, i)))
        assert os.path.isfile(d_file)
    for i in range(len(north_aperture.properties.radiance.states)):
        d_file = (os.path.join(ap_dir, '{}..dmtx..{}.rad'.format(group_name, i)))
        assert os.path.isfile(d_file)
    for i in range(len(north_aperture.properties.radiance.states)):
        d_file = (os.path.join(ap_dir, '{}..vmtx..{}.rad'.format(group_name, i)))
        assert os.path.isfile(d_file)

    # clean up the folder
    nukedir(folder, rmdir=True)


def test_writer_to_rad_folder_shade_drop():
    """Test the Model to.rad_folder method with shades that drop half-way."""
    room = Room.from_box('Store_Entrance', 10, 10, 6)

    # create the apertures on the south side and put them in the same dynamic group
    pts_1 = [Point3D(1, 0, 1), Point3D(4, 0, 1), Point3D(4, 0, 3), Point3D(1, 0, 3)]
    pts_2 = [Point3D(1, 0, 3), Point3D(4, 0, 3), Point3D(4, 0, 5), Point3D(1, 0, 5)]
    pts_3 = [Point3D(6, 0, 1), Point3D(9, 0, 1), Point3D(9, 0, 3), Point3D(6, 0, 3)]
    pts_4 = [Point3D(6, 0, 3), Point3D(9, 0, 3), Point3D(9, 0, 5), Point3D(6, 0, 5)]
    pts_5 = [Point3D(4.5, 0, 0.25), Point3D(5.5, 0, 0.25), Point3D(5.5, 0, 5), Point3D(4.5, 0, 5)]
    s_left_bottom = Aperture('s_left_bottom', Face3D(pts_1))
    s_left_top = Aperture('s_left_top', Face3D(pts_2))
    s_right_bottom = Aperture('s_right_bottom', Face3D(pts_3))
    s_right_top = Aperture('s_right_top', Face3D(pts_4))
    entry = Aperture('entry', Face3D(pts_5))
    south_face = room[3]
    south_apertures = [s_left_bottom, s_left_top, s_right_bottom, s_right_top, entry]
    south_face.add_apertures(south_apertures)
    for ap in south_apertures:
        ap.properties.radiance.dynamic_group_identifier = 'SouthWall'

    # create the apertures on the east side and put them in the same dynamic group
    pts_6 = [Point3D(10, 1, 1), Point3D(10, 9, 1), Point3D(10, 9, 3), Point3D(10, 1, 3)]
    pts_7 = [Point3D(10, 1, 3), Point3D(10, 9, 3), Point3D(10, 9, 5), Point3D(10, 1, 5)]
    e_bottom = Aperture('e_bottom', Face3D(pts_6))
    e_top = Aperture('e_top', Face3D(pts_7))
    east_face = room[2]
    east_apertures = [e_bottom, e_top]
    east_face.add_apertures(east_apertures)
    for ap in east_apertures:
        ap.properties.radiance.dynamic_group_identifier = 'EastWall'

    # create the states
    bare_glass = Glass.from_single_transmittance('BareGlass', 0.7)
    protected_glass = Glass.from_single_transmittance('ProtectedGlass', 0.3)
    bare = RadianceSubFaceState(bare_glass)
    protected = RadianceSubFaceState(protected_glass)

    # assign states to individual apertures
    s_left_bottom.properties.radiance.states = \
        [bare.duplicate(), bare.duplicate(), protected.duplicate()]
    s_right_bottom.properties.radiance.states = \
        [bare.duplicate(), bare.duplicate(), protected.duplicate()]
    s_left_top.properties.radiance.states = \
        [bare.duplicate(), protected.duplicate(), protected.duplicate()]
    s_right_top.properties.radiance.states = \
        [bare.duplicate(), protected.duplicate(), protected.duplicate()]
    entry.properties.radiance.modifier = bare_glass

    e_bottom.properties.radiance.states = \
        [bare.duplicate(), bare.duplicate(), protected.duplicate()]
    e_top.properties.radiance.states = \
        [bare.duplicate(), protected.duplicate(), protected.duplicate()]

    # export the model radiance folder
    model = Model('Apple_Store', [room])
    folder = os.path.abspath('./tests/assets/model/rad_folder_shade_drop')
    model.to.rad_folder(model, folder)

    model_folder = ModelFolder(folder)

    ap_dir = model_folder.aperture_group_folder(full=True)
    assert os.path.isfile(os.path.join(ap_dir, 'states.json'))

    group_name = entry.properties.radiance.dynamic_group_identifier
    assert os.path.isfile(os.path.join(ap_dir, '{}..black.rad'.format(group_name)))
    for i in range(len(entry.properties.radiance.states)):
        d_file = (os.path.join(ap_dir, '{}..default..{}.rad'.format(group_name, i)))
        assert os.path.isfile(d_file)
    for i in range(len(entry.properties.radiance.states)):
        d_file = (os.path.join(ap_dir, '{}..direct..{}.rad'.format(group_name, i)))
        assert os.path.isfile(d_file)

    group_name = e_bottom.properties.radiance.dynamic_group_identifier
    assert os.path.isfile(os.path.join(ap_dir, '{}..black.rad'.format(group_name)))
    for i in range(len(e_bottom.properties.radiance.states)):
        d_file = (os.path.join(ap_dir, '{}..default..{}.rad'.format(group_name, i)))
        assert os.path.isfile(d_file)
    for i in range(len(e_bottom.properties.radiance.states)):
        d_file = (os.path.join(ap_dir, '{}..direct..{}.rad'.format(group_name, i)))
        assert os.path.isfile(d_file)

    # clean up the folder
    nukedir(folder, rmdir=True)


def test_writer_to_rad_folder_sensor_grids_views():
    """Test the Model to.rad_folder method with assigned sensor grids and views."""
    room = Room.from_box('Tiny_House_Zone', 5, 10, 3)
    garage = Room.from_box('Tiny_Garage', 5, 10, 3, origin=Point3D(5, 0, 0))

    south_face = room[3]
    south_face.apertures_by_ratio(0.4, 0.01)
    south_face.apertures[0].overhang(0.5, indoor=False)
    south_face.apertures[0].overhang(0.5, indoor=True)
    south_face.move_shades(Vector3D(0, 0, -0.5))
    north_face = garage[1]
    north_face.apertures_by_ratio(0.1, 0.01)

    room_grid = room.properties.radiance.generate_sensor_grid(0.5, 0.5, 1)
    garage_grid = garage.properties.radiance.generate_sensor_grid(0.5, 0.5, 1)
    room_view = room.properties.radiance.generate_view((0, -1, 0))
    garage_view = garage.properties.radiance.generate_view((0, 1, 0))

    Room.solve_adjacency([room, garage], 0.01)

    model = Model('Tiny_House', [room, garage])
    model.properties.radiance.sensor_grids = [room_grid]
    model.properties.radiance.add_sensor_grids([garage_grid])
    model.properties.radiance.views = [room_view]
    model.properties.radiance.add_views([garage_view])

    folder = os.path.abspath('./tests/assets/model/rad_folder_grids_views')
    model.to.rad_folder(model, folder)

    model_folder = ModelFolder(folder)

    grid_dir = model_folder.grid_folder(full=True)
    assert os.path.isfile(os.path.join(grid_dir, 'Tiny_House_Zone.pts'))
    assert os.path.isfile(os.path.join(grid_dir, 'Tiny_Garage.pts'))

    view_dir = model_folder.view_folder(full=True)
    assert os.path.isfile(os.path.join(view_dir, 'Tiny_House_Zone.vf'))
    assert os.path.isfile(os.path.join(view_dir, 'Tiny_House_Zone.json'))
    assert os.path.isfile(os.path.join(view_dir, 'Tiny_Garage.vf'))
    assert os.path.isfile(os.path.join(view_dir, 'Tiny_Garage.json'))

    # clean up the folder
    nukedir(folder, rmdir=True)
