"""Tests the features that honeybee_radiance adds to honeybee_core Aperture."""
from honeybee.aperture import Aperture
from honeybee.face import Face
from honeybee.room import Room
from honeybee.boundarycondition import boundary_conditions

from honeybee_radiance.properties.aperture import ApertureRadianceProperties
from honeybee_radiance.dynamic import RadianceSubFaceState, StateGeometry
from honeybee_radiance.modifier import Modifier
from honeybee_radiance.modifier.material import Glass

from honeybee_radiance.lib.modifiers import generic_interior_window, \
    generic_exterior_window, black

from ladybug_geometry.geometry3d.pointvector import Point3D, Vector3D
from ladybug_geometry.geometry3d.plane import Plane
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


def test_set_states():
    """Test the setting of states on an Aperture."""
    pts = (Point3D(0, 0, 0), Point3D(0, 0, 3), Point3D(1, 0, 3), Point3D(1, 0, 0))
    ap = Aperture('TestWindow', Face3D(pts))
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
    tint3 = RadianceSubFaceState(ecglass3)
    tint4 = RadianceSubFaceState(ecglass4)
    states = (tint1, tint2, tint3, tint4)

    tint3.add_shade(shd1)
    with pytest.raises(AssertionError):
        tint4.add_shades([shd1, shd2])
    tint4.add_shades([shd1.duplicate(), shd2])

    with pytest.raises(AssertionError):
        tint1.gen_geos_from_tmtx_thickness(0.05)
    with pytest.raises(AssertionError):
        tint1.gen_geo_from_vmtx_offset(0.1)
    with pytest.raises(AssertionError):
        tint1.gen_geo_from_dmtx_offset(0.1)

    with pytest.raises(AssertionError):
        ap.properties.radiance.states = states
    ap.properties.radiance.dynamic_group_identifier = 'ElectrochromicWindow1'
    ap.properties.radiance.states = states

    for state in ap.properties.radiance.states:
        assert state.parent.identifier == 'TestWindow'

    new_ap = ap.duplicate()

    assert ap.properties.radiance.dynamic_group_identifier == \
        new_ap.properties.radiance.dynamic_group_identifier == 'ElectrochromicWindow1'
    assert len(new_ap.properties.radiance.states) == 4
    for i, state in enumerate(new_ap.properties.radiance.states):
        assert state.modifier.identifier == 'ElectrochromicState{}'.format(i + 1)
    assert len(new_ap.properties.radiance.states[2].shades) == 1
    assert len(new_ap.properties.radiance.states[3].shades) == 2


def move_state_shades():
    """Check to be sure that dynamic shades are moved with their parent."""
    pts = (Point3D(0, 0, 0), Point3D(0, 0, 3), Point3D(1, 0, 3), Point3D(1, 0, 0))
    ap = Aperture('TestWindow', Face3D(pts))
    pts_1 = (Point3D(0, 0, 0), Point3D(2, 0, 0), Point3D(2, 2, 0), Point3D(0, 2, 0))
    shade = StateGeometry('RectangleShade', Face3D(pts_1))

    tint1 = RadianceSubFaceState(shades=[shade])
    ap.properties.radiance.dynamic_group_identifier = 'ElectrochromicWindow1'
    ap.properties.radiance.states = [tint1]
    tint1.gen_geos_from_tmtx_thickness(0.05)

    vec_1 = Vector3D(2, 2, 2)
    new_ap = ap.duplicate()
    new_ap.move(vec_1)
    new_shd = new_ap.properties.radiance.states[0].shades[0]
    assert new_shd.geometry[0] == Point3D(2, 2, 2)
    assert new_shd.geometry[1] == Point3D(4, 2, 2)
    assert new_shd.geometry[2] == Point3D(4, 4, 2)
    assert new_shd.geometry[3] == Point3D(2, 4, 2)


def scale_state_shades():
    """Check to be sure that dynamic shades are scaled with their parent."""
    pts = (Point3D(1, 1, 2), Point3D(2, 1, 2), Point3D(2, 2, 2), Point3D(1, 2, 2))
    ap = Aperture('TestWindow', Face3D(pts))
    pts_1 = (Point3D(0, 0, 0), Point3D(2, 0, 0), Point3D(2, 2, 0), Point3D(0, 2, 0))
    shade = StateGeometry('RectangleShade', Face3D(pts_1))

    tint1 = RadianceSubFaceState(shades=[shade])
    ap.properties.radiance.dynamic_group_identifier = 'ElectrochromicWindow1'
    ap.properties.radiance.states = [tint1]
    tint1.gen_geo_from_vmtx_offset(0.05)
    tint1.gen_geo_from_dmtx_offset(0.1)

    new_ap = ap.duplicate()
    new_ap.scale(2)
    new_shd = new_ap.properties.radiance.states[0].shades[0]
    assert new_shd.geometry[0] == Point3D(2, 2, 4)
    assert new_shd.geometry[1] == Point3D(4, 2, 4)
    assert new_shd.geometry[2] == Point3D(4, 4, 4)
    assert new_shd.geometry[3] == Point3D(2, 4, 4)


def rotate_state_shades():
    """Check to be sure that dynamic shades are rotated with their parent."""
    pts = (Point3D(0, 0, 2), Point3D(2, 0, 2), Point3D(2, 2, 2), Point3D(0, 2, 2))
    ap = Aperture('TestWindow', Face3D(pts))
    pts_1 = (Point3D(0, 0, 0), Point3D(2, 0, 0), Point3D(2, 2, 0), Point3D(0, 2, 0))
    shade = StateGeometry('RectangleShade', Face3D(pts_1))

    tint1 = RadianceSubFaceState(shades=[shade])
    ap.properties.radiance.dynamic_group_identifier = 'ElectrochromicWindow1'
    ap.properties.radiance.states = [tint1]
    tint1.gen_geos_from_tmtx_thickness(0.05)

    new_ap = ap.duplicate()
    origin = Point3D(0, 0, 0)
    axis = Vector3D(1, 0, 0)
    new_ap.rotate(axis, 180, origin)
    new_shd = new_ap.properties.radiance.states[0].shades[0]
    assert new_shd.geometry[0].x == pytest.approx(0, rel=1e-3)
    assert new_shd.geometry[0].y == pytest.approx(0, rel=1e-3)
    assert new_shd.geometry[0].z == pytest.approx(-2, rel=1e-3)
    assert new_shd.geometry[2].x == pytest.approx(2, rel=1e-3)
    assert new_shd.geometry[2].y == pytest.approx(-2, rel=1e-3)
    assert new_shd.geometry[2].z == pytest.approx(-2, rel=1e-3)


def rotate_xy_state_shades():
    """Check to be sure that dynamic shades are rotated with their parent."""
    pts = (Point3D(1, 1, 2), Point3D(2, 1, 2), Point3D(2, 2, 2), Point3D(1, 2, 2))
    ap = Aperture('TestWindow', Face3D(pts))
    pts_1 = (Point3D(0, 0, 0), Point3D(2, 0, 0), Point3D(2, 2, 0), Point3D(0, 2, 0))
    shade = StateGeometry('RectangleShade', Face3D(pts_1))

    tint1 = RadianceSubFaceState(shades=[shade])
    ap.properties.radiance.dynamic_group_identifier = 'ElectrochromicWindow1'
    ap.properties.radiance.states = [tint1]
    tint1.gen_geos_from_tmtx_thickness(0.05)

    new_ap = ap.duplicate()
    origin = Point3D(0, 0, 0)
    new_ap.rotate_xy(180, origin)
    new_shd = new_ap.properties.radiance.states[0].shades[0]
    assert new_shd.geometry[0].x == pytest.approx(1, rel=1e-3)
    assert new_shd.geometry[0].y == pytest.approx(1, rel=1e-3)
    assert new_shd.geometry[0].z == pytest.approx(2, rel=1e-3)
    assert new_shd.geometry[2].x == pytest.approx(0, rel=1e-3)
    assert new_shd.geometry[2].y == pytest.approx(0, rel=1e-3)
    assert new_shd.geometry[2].z == pytest.approx(2, rel=1e-3)


def reflect_state_shades():
    """Check to be sure that dynamic shades are reflected with their parent."""
    pts = (Point3D(1, 1, 2), Point3D(2, 1, 2), Point3D(2, 2, 2), Point3D(1, 2, 2))
    ap = Aperture('TestWindow', Face3D(pts))
    pts_1 = (Point3D(0, 0, 0), Point3D(2, 0, 0), Point3D(2, 2, 0), Point3D(0, 2, 0))
    shade = StateGeometry('RectangleShade', Face3D(pts_1))

    tint1 = RadianceSubFaceState(shades=[shade])
    ap.properties.radiance.dynamic_group_identifier = 'ElectrochromicWindow1'
    ap.properties.radiance.states = [tint1]
    tint1.gen_geos_from_tmtx_thickness(0.05)

    new_ap = ap.duplicate()
    origin_1 = Point3D(1, 0, 2)
    normal_1 = Vector3D(1, 0, 0)
    plane_1 = Plane(normal_1, origin_1)
    new_ap.reflect(plane_1)
    new_shd = new_ap.properties.radiance.states[0].shades[0]
    assert new_shd.geometry[-1].x == pytest.approx(1, rel=1e-3)
    assert new_shd.geometry[-1].y == pytest.approx(1, rel=1e-3)
    assert new_shd.geometry[-1].z == pytest.approx(2, rel=1e-3)
    assert new_shd.geometry[1].x == pytest.approx(0, rel=1e-3)
    assert new_shd.geometry[1].y == pytest.approx(2, rel=1e-3)
    assert new_shd.geometry[1].z == pytest.approx(2, rel=1e-3)


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


def test_to_from_dict():
    """Test the Aperture from_dict method with states."""
    aperture = Aperture.from_vertices(
        'wall_aperture', [[0, 0, 0], [10, 0, 0], [10, 0, 10], [0, 0, 10]])
    triple_pane = Glass.from_single_transmittance('TriplePane', 0.45)
    aperture.properties.radiance.modifier = triple_pane

    ad = aperture.to_dict()
    new_aperture = Aperture.from_dict(ad)
    assert new_aperture.properties.radiance.modifier == triple_pane
    assert new_aperture.to_dict() == ad


def test_to_from_dict_with_states():
    """Test the Aperture from_dict method with radiance properties."""
    ap = Aperture.from_vertices(
        'wall_aperture', [[0, 0, 0], [10, 0, 0], [10, 0, 10], [0, 0, 10]])
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

    ap.properties.radiance.dynamic_group_identifier = 'ElectrochromicWindow1'
    ap.properties.radiance.states = states
    tint4.gen_geos_from_tmtx_thickness(0.05)

    ad = ap.to_dict()
    new_aperture = Aperture.from_dict(ad)
    assert new_aperture.properties.radiance.dynamic_group_identifier == \
        ap.properties.radiance.dynamic_group_identifier
    state_ids1 = [state.modifier for state in states]
    state_ids2 = [state.modifier for state in new_aperture.properties.radiance.states]
    assert state_ids1 == state_ids2
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
