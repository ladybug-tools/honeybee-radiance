from honeybee_radiance.geometry import Ring
from honeybee_radiance.modifier.material import Plastic
from .rad_string_collection import metal_ring


def test_ring():
    geo = Ring('test_ring')
    assert geo.identifier == 'test_ring'
    assert geo.center_pt == (0, 0, 0)
    assert geo.normal_vector == (0, 0, 1)
    assert geo.radius_inner == 5
    assert geo.radius_outer == 10
    assert geo.to_radiance(
        minimal=True) == 'void ring test_ring 0 0 8 0.0 0.0 0.0 0.0 0.0 1.0 5.0 10.0'


def test_assign_values():
    geo = Ring('test_ring', (0.6, 0.7, 0.8), (0, 0, 20), 50, 100)
    assert geo.identifier == 'test_ring'
    assert geo.center_pt == (0.6, 0.7, 0.8)
    assert geo.normal_vector == (0, 0, 20)
    assert geo.radius_inner == 50
    assert geo.radius_outer == 100
    assert geo.to_radiance(minimal=True) == \
        'void ring test_ring 0 0 8 0.6 0.7 0.8 0.0 0.0 20.0 50.0 100.0'


def test_update_values():
    geo = Ring('test_ring', (0.6, 0.7, 0.8), (0, 0, 20), 50, 100)
    geo.identifier = 'new_ring'
    geo.center_pt = (10, 10, 10)
    geo.normal_vector = (0, 0, 10)
    geo.radius_inner = 0
    geo.radius_outer = 20
    assert geo.identifier == 'new_ring'
    assert geo.center_pt == (10, 10, 10)
    assert geo.normal_vector == (0, 0, 10)
    assert geo.radius_inner == 0
    assert geo.radius_outer == 20
    assert geo.to_radiance(minimal=True) == \
        'void ring new_ring 0 0 8 10.0 10.0 10.0 0.0 0.0 10.0 0.0 20.0'


def test_from_string():
    geometry_str = metal_ring
    geo = Ring.from_string(geometry_str)
    assert geo.identifier == 'ring_one'
    assert geo.center_pt == (0, 0, 0)
    assert geo.normal_vector == (0, 0, 1)
    assert geo.radius_inner == 10
    assert geo.radius_outer == 20
    assert ' '.join(geo.to_radiance(minimal=True).split()) == \
        ' '.join(geometry_str.split())


def test_from_and_to_dict():
    modifier = Plastic('ring_material')
    ring = Ring('default_ring', modifier=modifier)
    ring_dict = ring.to_dict()

    # check values in dictionary
    assert ring_dict['identifier'] == 'default_ring'
    assert ring_dict['modifier'] == modifier.to_dict()
    assert ring_dict['center_pt'] == (0, 0, 0)
    assert ring_dict['normal_vector'] == (0, 0, 1)
    assert ring_dict['radius_inner'] == 5
    assert ring_dict['radius_outer'] == 10

    ring_from_dict = Ring.from_dict(ring_dict)

    assert ring_from_dict.to_radiance() == ring.to_radiance()
