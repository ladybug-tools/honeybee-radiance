"""Tests the features that honeybee_radiance adds to honeybee_core Door."""
from honeybee.door import Door
from honeybee.face import Face
from honeybee.room import Room
from honeybee.boundarycondition import boundary_conditions

from honeybee_radiance.properties.door import DoorRadianceProperties
from honeybee_radiance.dynamic import RadianceSubFaceState, StateGeometry
from honeybee_radiance.modifier import Modifier
from honeybee_radiance.modifier.material import Plastic, Glass

from honeybee_radiance.lib.modifiers import generic_door, generic_interior_window, \
    generic_exterior_window, black

from ladybug_geometry.geometry3d.pointvector import Point3D, Vector3D
from ladybug_geometry.geometry3d.face import Face3D

import pytest


def test_radiance_properties():
    """Test the existence of the Door radiance properties."""
    door = Door.from_vertices(
        'wall_door', [[0, 0, 0], [10, 0, 0], [10, 0, 10], [0, 0, 10]])
    assert hasattr(door.properties, 'radiance')
    assert isinstance(door.properties.radiance, DoorRadianceProperties)

    assert door.properties.radiance.modifier == generic_door
    assert door.properties.radiance.modifier_blk == black
    assert not door.properties.radiance.is_modifier_set_on_object


def test_default_modifiers():
    """Test the auto-assigning of modifiers by boundary condition."""
    vertices_parent_wall = [[0, 0, 0], [0, 10, 0], [0, 10, 3], [0, 0, 3]]
    vertices_parent_wall_2 = list(reversed(vertices_parent_wall))
    vertices_wall = [[0, 1, 0], [0, 2, 0], [0, 2, 2], [0, 0, 2]]
    vertices_wall_2 = list(reversed(vertices_wall))

    wf = Face.from_vertices('wall_face', vertices_parent_wall)
    wdr = Door.from_vertices('wall_door', vertices_wall)
    wf.add_door(wdr)
    Room('TestRoom1', [wf])
    assert wdr.properties.radiance.modifier == generic_door

    wf2 = Face.from_vertices('wall_face2', vertices_parent_wall_2)
    wdr2 = Door.from_vertices('wall_door2', vertices_wall_2)
    wdr.is_glass = True
    wdr2.is_glass = True
    wf2.add_door(wdr2)
    Room('TestRoom2', [wf2])
    wdr.set_adjacency(wdr2)
    assert wdr.properties.radiance.modifier == generic_interior_window

    ra = Door.from_vertices('wall_door', vertices_parent_wall)
    ra.is_glass = True
    assert ra.properties.radiance.modifier == generic_exterior_window


def test_set_modifier():
    """Test the setting of a modifier on an Door."""
    door = Door.from_vertices(
        'wall_door', [[0, 0, 0], [10, 0, 0], [10, 0, 10], [0, 0, 10]])
    painted_door = Plastic.from_single_reflectance('PaintedDoor', 0.75)
    door.properties.radiance.modifier = painted_door

    assert door.properties.radiance.modifier == painted_door
    assert door.properties.radiance.is_modifier_set_on_object

    with pytest.raises(AttributeError):
        door.properties.radiance.modifier.r_reflectance = 0.45


def test_duplicate():
    """Test what happens to radiance properties when duplicating a Door."""
    verts = [Point3D(0, 0, 0), Point3D(10, 0, 0), Point3D(10, 0, 10), Point3D(0, 0, 10)]
    painted_door = Plastic.from_single_reflectance('PaintedDoor', 0.75)
    dr_original = Door.from_vertices('wall_door', Face3D(verts))
    dr_dup_1 = dr_original.duplicate()

    assert dr_original.properties.radiance.host is dr_original
    assert dr_dup_1.properties.radiance.host is dr_dup_1
    assert dr_original.properties.radiance.host is not dr_dup_1.properties.radiance.host

    assert dr_original.properties.radiance.modifier == \
        dr_dup_1.properties.radiance.modifier
    dr_dup_1.properties.radiance.modifier = painted_door
    assert dr_original.properties.radiance.modifier != \
        dr_dup_1.properties.radiance.modifier

    dr_dup_2 = dr_dup_1.duplicate()

    assert dr_dup_1.properties.radiance.modifier == \
        dr_dup_2.properties.radiance.modifier
    dr_dup_2.properties.radiance.modifier = None
    assert dr_dup_1.properties.radiance.modifier != \
        dr_dup_2.properties.radiance.modifier


def test_to_dict():
    """Test the Door to_dict method with radiance properties."""
    door = Door.from_vertices(
        'front_door', [[0, 0, 0], [10, 0, 0], [10, 0, 10], [0, 0, 10]])
    painted_door = Plastic.from_single_reflectance('PaintedDoor', 0.75)

    drd = door.to_dict()
    assert 'properties' in drd
    assert drd['properties']['type'] == 'DoorProperties'
    assert 'radiance' in drd['properties']
    assert drd['properties']['radiance']['type'] == 'DoorRadianceProperties'

    door.properties.radiance.modifier = painted_door
    drd = door.to_dict()
    assert 'modifier' in drd['properties']['radiance']
    assert drd['properties']['radiance']['modifier'] is not None
    assert drd['properties']['radiance']['modifier']['identifier'] == 'PaintedDoor'


def test_from_dict():
    """Test the Door from_dict method with radiance properties."""
    door = Door.from_vertices(
        'wall_door', [[0, 0, 0], [10, 0, 0], [10, 0, 10], [0, 0, 10]])
    painted_door = Plastic.from_single_reflectance('PaintedDoor', 0.75)
    door.properties.radiance.modifier = painted_door

    ad = door.to_dict()
    new_door = Door.from_dict(ad)
    assert new_door.properties.radiance.modifier == painted_door
    assert new_door.to_dict() == ad


def test_to_from_dict_with_states():
    """Test the Door from_dict method with radiance properties."""
    dr = Door.from_vertices(
        'front_door', [[0, 0, 0], [10, 0, 0], [10, 0, 10], [0, 0, 10]])
    shd1 = StateGeometry.from_vertices(
        'wall_overhang1', [[0, 0, 10], [10, 0, 10], [10, 2, 10], [0, 2, 10]])
    shd2 = StateGeometry.from_vertices(
        'wall_overhang2', [[0, 0, 5], [10, 0, 5], [10, 2, 5], [0, 2, 5]])

    ecglass1 = Glass.from_single_transmittance('ElectrochromicState1', 0.4)
    ecglass2 = Glass.from_single_transmittance('ElectrochromicState2', 0.27)
    ecglass3 = Glass.from_single_transmittance('ElectrochromicState3', 0.14)
    ecglass4 = Glass.from_single_transmittance('ElectrochromicState4', 0.01)

    tint1 = RadianceSubFaceState(ecglass1)
    tint2 = RadianceSubFaceState(ecglass2)
    tint3 = RadianceSubFaceState(ecglass3, [shd1])
    tint4 = RadianceSubFaceState(ecglass4, [shd1.duplicate(), shd2])
    states = (tint1, tint2, tint3, tint4)

    dr.properties.radiance.dynamic_group_identifier = 'ElectrochromicDoor1'
    dr.properties.radiance.states = states

    drd = dr.to_dict()
    new_door = Door.from_dict(drd)
    assert new_door.properties.radiance.dynamic_group_identifier == \
        dr.properties.radiance.dynamic_group_identifier
    state_ids1 = [state.modifier for state in states]
    state_ids2 = [state.modifier for state in new_door.properties.radiance.states]
    assert state_ids1 == state_ids2
    assert new_door.to_dict() == drd


def test_writer_to_rad():
    """Test the Door to.rad method."""
    pts = [[0, 0, 0], [10, 0, 0], [10, 0, 10], [0, 0, 10]]
    door = Door.from_vertices('wall_door', pts)
    painted_door = Plastic.from_single_reflectance('PaintedDoor', 0.75)
    door.properties.radiance.modifier = painted_door

    assert hasattr(door.to, 'rad')
    rad_string = door.to.rad(door)
    assert 'polygon wall_door' in rad_string
    assert 'PaintedDoor' in rad_string
    for pt in pts:
        assert ' '.join([str(float(x)) for x in pt]) in rad_string
