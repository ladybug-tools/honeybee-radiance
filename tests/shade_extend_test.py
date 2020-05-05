"""Tests the features that honeybee_radiance adds to honeybee_core Shade."""
from honeybee.shade import Shade
from honeybee.aperture import Aperture

from honeybee_radiance.properties.shade import ShadeRadianceProperties
from honeybee_radiance.dynamic import RadianceShadeState, StateGeometry
from honeybee_radiance.modifier import Modifier
from honeybee_radiance.modifier.material import Plastic, Glass

from honeybee_radiance.lib.modifiers import generic_interior_shade, \
    generic_exterior_shade, generic_context, black

from ladybug_geometry.geometry3d.pointvector import Point3D, Vector3D
from ladybug_geometry.geometry3d.plane import Plane
from ladybug_geometry.geometry3d.face import Face3D

import pytest


def test_radiance_properties():
    """Test the existence of the Shade radiance properties."""
    shade = Shade.from_vertices(
        'overhang', [[0, 0, 3], [1, 0, 3], [1, 1, 3], [0, 1, 3]])

    assert hasattr(shade.properties, 'radiance')
    assert isinstance(shade.properties.radiance, ShadeRadianceProperties)
    assert isinstance(shade.properties.radiance.modifier, Modifier)

    assert shade.properties.radiance.modifier == generic_context
    assert shade.properties.radiance.modifier_blk == black
    assert not shade.properties.radiance.is_modifier_set_on_object

    frit_glass = Glass.from_single_transmittance('FritGlass', 0.2)
    shade.properties.radiance.modifier = frit_glass
    assert shade.properties.radiance.modifier_blk == frit_glass
    assert shade.properties.radiance.is_modifier_set_on_object


def test_default_properties():
    """Test the auto-assigning of shade properties."""
    out_shade = Shade.from_vertices(
        'overhang', [[0, 0, 3], [1, 0, 3], [1, 1, 3], [0, 1, 3]])
    in_shade = Shade.from_vertices(
        'light_shelf', [[0, 0, 3], [-1, 0, 3], [-1, -1, 3], [0, -1, 3]])
    aperture = Aperture.from_vertices(
        'parent_aperture', [[0, 0, 0], [0, 10, 0], [0, 10, 3], [0, 0, 3]])

    assert out_shade.properties.radiance.modifier == generic_context
    assert in_shade.properties.radiance.modifier == generic_context

    aperture.add_outdoor_shade(out_shade)
    assert out_shade.properties.radiance.modifier == generic_exterior_shade

    aperture.add_indoor_shade(in_shade)
    assert in_shade.properties.radiance.modifier == generic_interior_shade


def test_set_modifier():
    """Test the setting of a modifier on a Shade."""
    shade = Shade.from_vertices(
        'tree', [[0, 0, 3], [1, 0, 3], [1, 1, 3], [0, 1, 3]])
    foliage = Glass.from_single_transmittance('Foliage', 0.2)
    shade.properties.radiance.modifier = foliage

    assert shade.properties.radiance.modifier == foliage
    assert shade.properties.radiance.is_modifier_set_on_object

    with pytest.raises(AttributeError):
        shade.properties.radiance.modifier.r_transmittance = 0.1


def test_duplicate():
    """Test what happens to radiance properties when duplicating a Shade."""
    verts = [Point3D(0, 0, 3), Point3D(1, 0, 3), Point3D(1, 1, 3), Point3D(0, 1, 3)]
    foliage = Glass.from_single_transmittance('Foliage', 0.2)
    shade_original = Shade('tree', Face3D(verts))
    shade_dup_1 = shade_original.duplicate()

    assert shade_original.properties.radiance.host is shade_original
    assert shade_dup_1.properties.radiance.host is shade_dup_1
    assert shade_original.properties.radiance.host is not shade_dup_1.properties.radiance.host

    assert shade_original.properties.radiance.modifier == \
        shade_dup_1.properties.radiance.modifier
    shade_dup_1.properties.radiance.modifier = foliage
    assert shade_original.properties.radiance.modifier != \
        shade_dup_1.properties.radiance.modifier

    shade_dup_2 = shade_dup_1.duplicate()

    assert shade_dup_1.properties.radiance.modifier == \
        shade_dup_2.properties.radiance.modifier
    shade_dup_2.properties.radiance.modifier = None
    assert shade_dup_1.properties.radiance.modifier != \
        shade_dup_2.properties.radiance.modifier


def test_set_states():
    """Test the setting of states on a Shade."""
    pts = (Point3D(0, 0, 0), Point3D(0, 0, 3), Point3D(1, 0, 3), Point3D(1, 0, 0))
    shd = Shade('TreeTrunk', Face3D(pts))
    shd1 = StateGeometry.from_vertices(
        'tree_foliage1', [[0, 0, 5], [2, 0, 5], [2, 2, 5], [0, 2, 5]])
    shd2 = StateGeometry.from_vertices(
        'tree_foliage2', [[0, 0, 5], [-2, 0, 5], [-2, 2, 5], [0, 2, 5]])

    trans1 = Glass.from_single_transmittance('TreeTrans1', 0.5)
    trans2 = Glass.from_single_transmittance('TreeTrans2', 0.27)
    trans3 = Glass.from_single_transmittance('TreeTrans3', 0.14)
    trans4 = Glass.from_single_transmittance('TreeTrans4', 0.01)

    tr1 = RadianceShadeState(trans1)
    tr2 = RadianceShadeState(trans2)
    tr3 = RadianceShadeState(trans3)
    tr4 = RadianceShadeState(trans4)
    states = (tr1, tr2, tr3, tr4)

    tr3.add_shade(shd1)
    with pytest.raises(AssertionError):
        tr4.add_shades([shd1, shd2])
    tr4.add_shades([shd1.duplicate(), shd2])

    with pytest.raises(AssertionError):
        shd.properties.radiance.states = states
    shd.properties.radiance.dynamic_group_identifier = 'DeciduousTrees'
    shd.properties.radiance.states = states

    for state in shd.properties.radiance.states:
        assert state.parent.identifier == 'TreeTrunk'

    new_shd = shd.duplicate()

    assert shd.properties.radiance.dynamic_group_identifier == \
        new_shd.properties.radiance.dynamic_group_identifier == 'DeciduousTrees'
    assert len(new_shd.properties.radiance.states) == 4
    for i, state in enumerate(new_shd.properties.radiance.states):
        assert state.modifier.identifier == 'TreeTrans{}'.format(i + 1)
    assert len(new_shd.properties.radiance.states[2].shades) == 1
    assert len(new_shd.properties.radiance.states[3].shades) == 2


def move_state_shades():
    """Check to be sure that dynamic shades are moved with their parent."""
    pts = (Point3D(0, 0, 0), Point3D(0, 0, 3), Point3D(1, 0, 3), Point3D(1, 0, 0))
    ap = Shade('TestShade', Face3D(pts))
    pts_1 = (Point3D(0, 0, 0), Point3D(2, 0, 0), Point3D(2, 2, 0), Point3D(0, 2, 0))
    shade = StateGeometry('RectangleShade', Face3D(pts_1))

    tint1 = RadianceShadeState(shades=[shade])
    ap.properties.radiance.dynamic_group_identifier = 'DeciduousTrees'
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
    ap = Shade('TestShade', Face3D(pts))
    pts_1 = (Point3D(0, 0, 0), Point3D(2, 0, 0), Point3D(2, 2, 0), Point3D(0, 2, 0))
    shade = StateGeometry('RectangleShade', Face3D(pts_1))

    tint1 = RadianceShadeState(shades=[shade])
    ap.properties.radiance.dynamic_group_identifier = 'DeciduousTrees'
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
    ap = Shade('TestShade', Face3D(pts))
    pts_1 = (Point3D(0, 0, 0), Point3D(2, 0, 0), Point3D(2, 2, 0), Point3D(0, 2, 0))
    shade = StateGeometry('RectangleShade', Face3D(pts_1))

    tint1 = RadianceShadeState(shades=[shade])
    ap.properties.radiance.dynamic_group_identifier = 'DeciduousTrees'
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
    ap = Shade('TestShade', Face3D(pts))
    pts_1 = (Point3D(0, 0, 0), Point3D(2, 0, 0), Point3D(2, 2, 0), Point3D(0, 2, 0))
    shade = StateGeometry('RectangleShade', Face3D(pts_1))

    tint1 = RadianceShadeState(shades=[shade])
    ap.properties.radiance.dynamic_group_identifier = 'DeciduousTrees'
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
    ap = Shade('TestShade', Face3D(pts))
    pts_1 = (Point3D(0, 0, 0), Point3D(2, 0, 0), Point3D(2, 2, 0), Point3D(0, 2, 0))
    shade = StateGeometry('RectangleShade', Face3D(pts_1))

    tint1 = RadianceShadeState(shades=[shade])
    ap.properties.radiance.dynamic_group_identifier = 'DeciduousTrees'
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
    """Test the Shade to_dict method with radiance properties."""
    shade = Shade.from_vertices(
        'tree', [[0, 0, 0], [10, 0, 0], [10, 0, 10], [0, 0, 10]])
    foliage = Glass.from_single_transmittance('Foliage', 0.2)

    shdd = shade.to_dict()
    assert 'properties' in shdd
    assert shdd['properties']['type'] == 'ShadeProperties'
    assert 'radiance' in shdd['properties']
    assert shdd['properties']['radiance']['type'] == 'ShadeRadianceProperties'

    shade.properties.radiance.modifier = foliage
    shdd = shade.to_dict()
    assert 'modifier' in shdd['properties']['radiance']
    assert shdd['properties']['radiance']['modifier'] is not None
    assert shdd['properties']['radiance']['modifier']['identifier'] == 'Foliage'


def test_from_dict():
    """Test the Shade from_dict method with radiance properties."""
    shade = Shade.from_vertices(
        'tree', [[0, 0, 0], [10, 0, 0], [10, 0, 10], [0, 0, 10]])
    foliage = Glass.from_single_transmittance('Foliage', 0.2)
    shade.properties.radiance.modifier = foliage

    shdd = shade.to_dict()
    new_shade = Shade.from_dict(shdd)
    assert new_shade.properties.radiance.modifier == foliage
    assert new_shade.to_dict() == shdd


def test_to_from_dict_with_states():
    """Test the Shade from_dict method with radiance properties."""
    pts = (Point3D(0, 0, 0), Point3D(0, 0, 3), Point3D(1, 0, 3), Point3D(1, 0, 0))
    shd = Shade('TreeTrunk', Face3D(pts))
    shd1 = StateGeometry.from_vertices(
        'tree_foliage1', [[0, 0, 5], [2, 0, 5], [2, 2, 5], [0, 2, 5]])
    shd2 = StateGeometry.from_vertices(
        'tree_foliage2', [[0, 0, 5], [-2, 0, 5], [-2, 2, 5], [0, 2, 5]])

    trans1 = Glass.from_single_transmittance('TreeTrans1', 0.5)
    trans2 = Glass.from_single_transmittance('TreeTrans2', 0.27)
    trans3 = Glass.from_single_transmittance('TreeTrans3', 0.14)
    trans4 = Glass.from_single_transmittance('TreeTrans4', 0.01)

    tr1 = RadianceShadeState(trans1)
    tr2 = RadianceShadeState(trans2)
    tr3 = RadianceShadeState(trans3, [shd1])
    tr4 = RadianceShadeState(trans4, [shd1.duplicate(), shd2])
    states = (tr1, tr2, tr3, tr4)

    shd.properties.radiance.dynamic_group_identifier = 'DeciduousTrees'
    shd.properties.radiance.states = states

    ad = shd.to_dict()
    new_shade = Shade.from_dict(ad)
    assert new_shade.properties.radiance.dynamic_group_identifier == \
        shd.properties.radiance.dynamic_group_identifier
    state_ids1 = [state.modifier for state in states]
    state_ids2 = [state.modifier for state in new_shade.properties.radiance.states]
    assert state_ids1 == state_ids2
    assert new_shade.to_dict() == ad


def test_writer_to_rad():
    """Test the Shade to.rad method."""
    pts = [[0, 0, 0], [10, 0, 0], [10, 0, 10], [0, 0, 10]]
    shade = Shade.from_vertices('tree', pts)
    foliage = Glass.from_single_transmittance('Foliage', 0.2)
    shade.properties.radiance.modifier = foliage

    assert hasattr(shade.to, 'rad')
    rad_string = shade.to.rad(shade)
    assert 'polygon tree' in rad_string
    assert 'Foliage' in rad_string
    for pt in pts:
        assert ' '.join([str(float(x)) for x in pt]) in rad_string
