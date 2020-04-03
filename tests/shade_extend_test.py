"""Tests the features that honeybee_radiance adds to honeybee_core Shade."""
from honeybee.shade import Shade
from honeybee.aperture import Aperture

from honeybee_radiance.properties.shade import ShadeRadianceProperties
from honeybee_radiance.modifier import Modifier
from honeybee_radiance.modifier.material import Plastic, Glass

from honeybee_radiance.lib.modifiers import generic_interior_shade, \
    generic_exterior_shade, generic_context, black

from ladybug_geometry.geometry3d.pointvector import Point3D
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
