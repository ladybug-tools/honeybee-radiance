"""Tests the features that honeybee_radiance adds to honeybee_core Aperture."""
from honeybee.aperture import Aperture
from honeybee.face import Face
from honeybee.room import Room
from honeybee.boundarycondition import boundary_conditions

from honeybee_radiance.properties.aperture import ApertureRadianceProperties
from honeybee_radiance.modifier import Modifier
from honeybee_radiance.modifier.material import Glass

from honeybee_radiance.lib.modifiers import generic_interior_window, \
    generic_exterior_window, black

from ladybug_geometry.geometry3d.pointvector import Point3D, Vector3D
from ladybug_geometry.geometry3d.face import Face3D

import pytest


def test_radiance_properties():
    """Test the existence of the Aperture radiance properties."""
    aperture = Aperture.from_vertices(
        'wall_aper', [[0, 0, 0], [10, 0, 0], [10, 0, 10], [0, 0, 10]])
    assert hasattr(aperture.properties, 'radiance')
    assert isinstance(aperture.properties.radiance, ApertureRadianceProperties)

    assert aperture.properties.radiance.modifier == generic_exterior_window
    assert aperture.properties.radiance.modifier_blk == black
    assert not aperture.properties.radiance.is_modifier_set_on_object


def test_default_modifiers():
    """Test the auto-assigning of modifiers by face type and boundary condition."""
    vertices_parent_wall = [[0, 0, 0], [0, 10, 0], [0, 10, 3], [0, 0, 3]]
    vertices_parent_wall_2 = list(reversed(vertices_parent_wall))
    vertices_wall = [[0, 1, 0], [0, 2, 0], [0, 2, 2], [0, 0, 2]]
    vertices_wall_2 = list(reversed(vertices_wall))
    vertices_floor = [[0, 0, 0], [0, 10, 0], [10, 10, 0], [10, 0, 0]]
    vertices_roof = [[10, 0, 3], [10, 10, 3], [0, 10, 3], [0, 0, 3]]

    wf = Face.from_vertices('wall_face', vertices_parent_wall)
    wa = Aperture.from_vertices('wall_window', vertices_wall)
    wf.add_aperture(wa)
    Room('TestRoom1', [wf])
    assert wa.properties.radiance.modifier == generic_exterior_window

    wf2 = Face.from_vertices('wall_face2', vertices_parent_wall_2)
    wa2 = Aperture.from_vertices('wall_window2', vertices_wall_2)
    wf2.add_aperture(wa2)
    Room('TestRoom2', [wf2])
    wa.set_adjacency(wa2)
    assert wa.properties.radiance.modifier == generic_interior_window

    ra = Aperture.from_vertices('roof_window', vertices_roof)
    assert ra.properties.radiance.modifier == generic_exterior_window
    fa = Aperture.from_vertices('floor_window', vertices_floor)
    assert fa.properties.radiance.modifier == generic_exterior_window


def test_set_modifier():
    """Test the setting of a modifier on an Aperture."""
    aperture = Aperture.from_vertices(
        'wall_aper', [[0, 0, 0], [10, 0, 0], [10, 0, 10], [0, 0, 10]])
    triple_pane = Glass.from_single_transmittance('TriplePane', 0.45)
    aperture.properties.radiance.modifier = triple_pane

    assert aperture.properties.radiance.modifier == triple_pane
    assert aperture.properties.radiance.is_modifier_set_on_object

    with pytest.raises(AttributeError):
        aperture.properties.radiance.modifier.r_transmittance = 0.45


def test_duplicate():
    """Test what happens to radiance properties when duplicating a Aperture."""
    verts = [Point3D(0, 0, 0), Point3D(10, 0, 0), Point3D(10, 0, 10), Point3D(0, 0, 10)]
    triple_pane = Glass.from_single_transmittance('TriplePane', 0.45)
    ap_original = Aperture.from_vertices('wall_aper', Face3D(verts))
    ap_dup_1 = ap_original.duplicate()

    assert ap_original.properties.radiance.host is ap_original
    assert ap_dup_1.properties.radiance.host is ap_dup_1
    assert ap_original.properties.radiance.host is not ap_dup_1.properties.radiance.host

    assert ap_original.properties.radiance.modifier == \
        ap_dup_1.properties.radiance.modifier
    ap_dup_1.properties.radiance.modifier = triple_pane
    assert ap_original.properties.radiance.modifier != \
        ap_dup_1.properties.radiance.modifier

    ap_dup_2 = ap_dup_1.duplicate()

    assert ap_dup_1.properties.radiance.modifier == \
        ap_dup_2.properties.radiance.modifier
    ap_dup_2.properties.radiance.modifier = None
    assert ap_dup_1.properties.radiance.modifier != \
        ap_dup_2.properties.radiance.modifier


def test_to_dict():
    """Test the Aperture to_dict method with radiance properties."""
    aperture = Aperture.from_vertices(
        'wall_aperture', [[0, 0, 0], [10, 0, 0], [10, 0, 10], [0, 0, 10]])
    triple_pane = Glass.from_single_transmittance('TriplePane', 0.45)

    ad = aperture.to_dict()
    assert 'properties' in ad
    assert ad['properties']['type'] == 'ApertureProperties'
    assert 'radiance' in ad['properties']
    assert ad['properties']['radiance']['type'] == 'ApertureRadianceProperties'

    aperture.properties.radiance.modifier = triple_pane
    ad = aperture.to_dict()
    assert 'modifier' in ad['properties']['radiance']
    assert ad['properties']['radiance']['modifier'] is not None
    assert ad['properties']['radiance']['modifier']['identifier'] == 'TriplePane'


def test_from_dict():
    """Test the Aperture from_dict method with radiance properties."""
    aperture = Aperture.from_vertices(
        'wall_aperture', [[0, 0, 0], [10, 0, 0], [10, 0, 10], [0, 0, 10]])
    triple_pane = Glass.from_single_transmittance('TriplePane', 0.45)
    aperture.properties.radiance.modifier = triple_pane

    ad = aperture.to_dict()
    new_aperture = Aperture.from_dict(ad)
    assert new_aperture.properties.radiance.modifier == triple_pane
    assert new_aperture.to_dict() == ad


def test_writer_to_rad():
    """Test the Aperture to.rad method."""
    pts = [[0, 0, 0], [10, 0, 0], [10, 0, 10], [0, 0, 10]]
    aperture = Aperture.from_vertices('wall_aperture', pts)
    triple_pane = Glass.from_single_transmittance('TriplePane', 0.45)
    aperture.properties.radiance.modifier = triple_pane

    assert hasattr(aperture.to, 'rad')
    rad_string = aperture.to.rad(aperture)
    assert 'polygon wall_aperture' in rad_string
    assert 'TriplePane' in rad_string
    for pt in pts:
        assert ' '.join([str(float(x)) for x in pt]) in rad_string
