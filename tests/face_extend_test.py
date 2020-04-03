"""Tests the features that honeybee_radiance adds to honeybee_core Face."""
from honeybee.face import Face
from honeybee.boundarycondition import boundary_conditions

from honeybee_radiance.properties.face import FaceRadianceProperties
from honeybee_radiance.modifier.material import Plastic, Glass

from honeybee_radiance.lib.modifiers import generic_floor, generic_wall, \
    generic_ceiling, black

from ladybug_geometry.geometry3d.pointvector import Point3D, Vector3D
from ladybug_geometry.geometry3d.face import Face3D

import pytest


def test_radiance_properties():
    """Test the existence of the Face radiance properties."""
    face = Face.from_vertices(
        'wall_face', [[0, 0, 0], [10, 0, 0], [10, 0, 10], [0, 0, 10]])
    assert hasattr(face.properties, 'radiance')
    assert isinstance(face.properties.radiance, FaceRadianceProperties)
    assert not face.properties.radiance.is_modifier_set_on_object

    assert face.properties.radiance.modifier == generic_wall
    assert face.properties.radiance.modifier_blk == black
    assert not face.properties.radiance.is_modifier_set_on_object

    glass_brick = Glass.from_single_transmittance('GlassBrick', 0.2)
    face.properties.radiance.modifier = glass_brick
    assert face.properties.radiance.modifier_blk == glass_brick
    assert face.properties.radiance.is_modifier_set_on_object


def test_default_modifiers():
    """Test the auto-assigning of modifiers by face type and boundary condition."""
    vertices_wall = [[0, 0, 0], [0, 10, 0], [0, 10, 3], [0, 0, 3]]
    vertices_floor = [[0, 0, 0], [0, 10, 0], [10, 10, 0], [10, 0, 0]]
    vertices_roof = [[10, 0, 3], [10, 10, 3], [0, 10, 3], [0, 0, 3]]

    wf = Face.from_vertices('wall', vertices_wall)
    assert wf.properties.radiance.modifier == generic_wall
    rf = Face.from_vertices('roof', vertices_roof)
    assert rf.properties.radiance.modifier == generic_ceiling
    ff = Face.from_vertices('floor', vertices_floor)
    assert ff.properties.radiance.modifier == generic_floor


def test_set_modifier():
    """Test the setting of a modifier on a Face."""
    face = Face.from_vertices(
        'wall_face', [[0, 0, 0], [10, 0, 0], [10, 0, 10], [0, 0, 10]])
    concrete = Plastic.from_single_reflectance('035Concrete', 0.35)
    face.properties.radiance.modifier = concrete

    assert face.properties.radiance.modifier == concrete
    assert face.properties.radiance.is_modifier_set_on_object

    with pytest.raises(AttributeError):
        face.properties.radiance.modifier.r_reflectance = 0.1


def test_duplicate():
    """Test what happens to radiance properties when duplicating a Face."""
    verts = [Point3D(0, 0, 0), Point3D(10, 0, 0), Point3D(10, 0, 10), Point3D(0, 0, 10)]
    concrete = Plastic.from_single_reflectance('035Concrete', 0.35)
    face_original = Face('wall_face', Face3D(verts))
    face_dup_1 = face_original.duplicate()

    assert face_original.properties.radiance.host is face_original
    assert face_dup_1.properties.radiance.host is face_dup_1
    assert face_original.properties.radiance.host is not face_dup_1.properties.radiance.host

    assert face_original.properties.radiance.modifier == \
        face_dup_1.properties.radiance.modifier
    face_dup_1.properties.radiance.modifier = concrete
    assert face_original.properties.radiance.modifier != \
        face_dup_1.properties.radiance.modifier

    face_dup_2 = face_dup_1.duplicate()

    assert face_dup_1.properties.radiance.modifier == \
        face_dup_2.properties.radiance.modifier
    face_dup_2.properties.radiance.modifier = None
    assert face_dup_1.properties.radiance.modifier != \
        face_dup_2.properties.radiance.modifier


def test_to_dict():
    """Test the Face to_dict method with radiance properties."""
    face = Face.from_vertices(
        'wall_face', [[0, 0, 0], [10, 0, 0], [10, 0, 10], [0, 0, 10]])
    concrete = Plastic.from_single_reflectance('035Concrete', 0.35)

    fd = face.to_dict()
    assert 'properties' in fd
    assert fd['properties']['type'] == 'FaceProperties'
    assert 'radiance' in fd['properties']
    assert fd['properties']['radiance']['type'] == 'FaceRadianceProperties'

    face.properties.radiance.modifier = concrete
    fd = face.to_dict()
    assert 'modifier' in fd['properties']['radiance']
    assert fd['properties']['radiance']['modifier'] is not None
    assert fd['properties']['radiance']['modifier']['identifier'] == '035Concrete'


def test_from_dict():
    """Test the Face from_dict method with radiance properties."""
    face = Face.from_vertices(
        'wall_face', [[0, 0, 0], [10, 0, 0], [10, 0, 10], [0, 0, 10]])
    concrete = Plastic.from_single_reflectance('035Concrete', 0.35)
    face.properties.radiance.modifier = concrete

    fd = face.to_dict()
    new_face = Face.from_dict(fd)
    assert new_face.properties.radiance.modifier == concrete
    assert new_face.to_dict() == fd


def test_writer_to_rad():
    """Test the Face to.rad method."""
    pts = [[0, 0, 0], [10, 0, 0], [10, 0, 10], [0, 0, 10]]
    face = Face.from_vertices('wall_face', pts)
    concrete = Plastic.from_single_reflectance('035Concrete', 0.35)
    face.properties.radiance.modifier = concrete

    assert hasattr(face.to, 'rad')
    rad_string = face.to.rad(face)
    assert 'polygon wall_face' in rad_string
    assert '035Concrete' in rad_string
    for pt in pts:
        assert ' '.join([str(float(x)) for x in pt]) in rad_string


def test_writer_to_rad_aperture_door_shade():
    pts = [[0, 0, 0], [10, 0, 0], [10, 0, 3], [0, 0, 3]]
    face = Face.from_vertices('wall_face', pts)
    face.apertures_by_ratio(0.4, 0.01)
    face.apertures[0].overhang(0.5, indoor=False)
    face.apertures[0].overhang(0.5, indoor=True)
    face.apertures[0].move_shades(Vector3D(0, 0, -0.5))
    light_shelf_out = Plastic.from_single_reflectance('OutdoorLightShelf', 0.5)
    light_shelf_in = Plastic.from_single_reflectance('IndoorLightShelf', 0.7)
    face.apertures[0].shades[0].properties.radiance.modifier = light_shelf_out
    face.apertures[0].shades[1].properties.radiance.modifier = light_shelf_in

    assert hasattr(face.to, 'rad')
    rad_string = face.to.rad(face)
    rad_string.split().count('polygon') == 4
    assert 'polygon wall_face' in rad_string
    assert 'OutdoorLightShelf' in rad_string
    assert 'IndoorLightShelf' in rad_string
