"""Tests the features that honeybee_radiance adds to honeybee_core ShadeMesh."""
from honeybee.shademesh import ShadeMesh

from honeybee_radiance.properties.shademesh import ShadeMeshRadianceProperties
from honeybee_radiance.modifier import Modifier
from honeybee_radiance.modifier.material import Glass

from honeybee_radiance.lib.modifiers import generic_interior_shade, \
    generic_exterior_shade, generic_context, black

from ladybug_geometry.geometry3d import Point3D, Vector3D, Plane, Mesh3D

import pytest


def test_radiance_properties():
    """Test the existence of the Shade radiance properties."""
    pts = (Point3D(0, 0, 4), Point3D(0, 2, 4), Point3D(2, 2, 4),
           Point3D(2, 0, 4), Point3D(4, 0, 4))
    mesh = Mesh3D(pts, [(0, 1, 2, 3), (2, 3, 4)])
    shade = ShadeMesh('Awning_1', mesh, is_detached=True)

    assert hasattr(shade.properties, 'radiance')
    assert isinstance(shade.properties.radiance, ShadeMeshRadianceProperties)
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
    pts = (Point3D(0, 0, 4), Point3D(0, 2, 4), Point3D(2, 2, 4),
           Point3D(2, 0, 4), Point3D(4, 0, 4))
    mesh = Mesh3D(pts, [(0, 1, 2, 3), (2, 3, 4)])
    out_shade = ShadeMesh('Awning_1', mesh, is_detached=True)
    in_shade = ShadeMesh('Awning_1', mesh, is_detached=False)

    assert out_shade.properties.radiance.modifier == generic_context
    assert in_shade.properties.radiance.modifier == generic_exterior_shade


def test_set_modifier():
    """Test the setting of a modifier on a Shade."""
    pts = (Point3D(0, 0, 4), Point3D(0, 2, 4), Point3D(2, 2, 4),
           Point3D(2, 0, 4), Point3D(4, 0, 4))
    mesh = Mesh3D(pts, [(0, 1, 2, 3), (2, 3, 4)])
    shade = ShadeMesh('Awning_1', mesh, is_detached=True)
    foliage = Glass.from_single_transmittance('Foliage', 0.2)
    shade.properties.radiance.modifier = foliage

    assert shade.properties.radiance.modifier == foliage
    assert shade.properties.radiance.is_modifier_set_on_object

    with pytest.raises(AttributeError):
        shade.properties.radiance.modifier.r_transmittance = 0.1


def test_duplicate():
    """Test what happens to radiance properties when duplicating a Shade."""
    pts = (Point3D(0, 0, 4), Point3D(0, 2, 4), Point3D(2, 2, 4),
           Point3D(2, 0, 4), Point3D(4, 0, 4))
    mesh = Mesh3D(pts, [(0, 1, 2, 3), (2, 3, 4)])
    foliage = Glass.from_single_transmittance('Foliage', 0.2)
    shade_original = ShadeMesh('tree', mesh)
    shade_dup_1 = shade_original.duplicate()

    assert shade_original.properties.radiance.host is shade_original
    assert shade_dup_1.properties.radiance.host is shade_dup_1
    assert shade_original.properties.radiance.host is not \
        shade_dup_1.properties.radiance.host

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


def test_to_dict():
    """Test the Shade to_dict method with radiance properties."""
    pts = (Point3D(0, 0, 4), Point3D(0, 2, 4), Point3D(2, 2, 4),
           Point3D(2, 0, 4), Point3D(4, 0, 4))
    mesh = Mesh3D(pts, [(0, 1, 2, 3), (2, 3, 4)])
    foliage = Glass.from_single_transmittance('Foliage', 0.2)
    shade = ShadeMesh('tree', mesh)

    shdd = shade.to_dict()
    assert 'properties' in shdd
    assert shdd['properties']['type'] == 'ShadeMeshProperties'
    assert 'radiance' in shdd['properties']
    assert shdd['properties']['radiance']['type'] == 'ShadeMeshRadianceProperties'

    shade.properties.radiance.modifier = foliage
    shdd = shade.to_dict()
    assert 'modifier' in shdd['properties']['radiance']
    assert shdd['properties']['radiance']['modifier'] is not None
    assert shdd['properties']['radiance']['modifier']['identifier'] == 'Foliage'


def test_from_dict():
    """Test the Shade from_dict method with radiance properties."""
    pts = (Point3D(0, 0, 4), Point3D(0, 2, 4), Point3D(2, 2, 4),
           Point3D(2, 0, 4), Point3D(4, 0, 4))
    mesh = Mesh3D(pts, [(0, 1, 2, 3), (2, 3, 4)])
    foliage = Glass.from_single_transmittance('Foliage', 0.2)
    shade = ShadeMesh('tree', mesh)
    shade.properties.radiance.modifier = foliage

    shdd = shade.to_dict()
    new_shade = ShadeMesh.from_dict(shdd)
    assert new_shade.properties.radiance.modifier == foliage
    assert new_shade.to_dict() == shdd


def test_writer_to_rad():
    """Test the ShadeMesh to.rad method."""
    pts = (Point3D(0, 0, 4), Point3D(0, 2, 4), Point3D(2, 2, 4),
           Point3D(2, 0, 4), Point3D(4, 0, 4))
    mesh = Mesh3D(pts, [(0, 1, 2, 3), (2, 3, 4)])
    foliage = Glass.from_single_transmittance('Foliage', 0.2)
    shade = ShadeMesh('tree', mesh)
    shade.properties.radiance.modifier = foliage

    assert hasattr(shade.to, 'rad')
    rad_string = shade.to.rad(shade)
    assert 'polygon tree' in rad_string
    assert 'Foliage' in rad_string
    for pt in pts:
        assert ' '.join([str(float(x)) for x in pt]) in rad_string
