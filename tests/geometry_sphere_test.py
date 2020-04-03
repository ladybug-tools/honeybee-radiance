from honeybee_radiance.geometry import Sphere
from honeybee_radiance.modifier.material import Plastic
from .rad_string_collection import metal_sphere


def test_sphere():
    geo = Sphere('test_sphere')
    assert geo.identifier == 'test_sphere'
    assert geo.center_pt == (0, 0, 0)
    assert geo.radius == 10
    assert geo.to_radiance(
        minimal=True) == \
            'void sphere test_sphere 0 0 4 0.0 0.0 0.0 10.0'


def test_assign_values():
    geo = Sphere('test_sphere', (0.6, 0.7, 0.8), 100)
    assert geo.identifier == 'test_sphere'
    assert geo.center_pt == (0.6, 0.7, 0.8)
    assert geo.radius == 100
    assert geo.to_radiance(minimal=True) == \
        'void sphere test_sphere 0 0 4 0.6 0.7 0.8 100.0'


def test_update_values():
    geo = Sphere('test_sphere', (0.6, 0.7, 0.8), 100)
    geo.identifier = 'new_sphere'
    geo.center_pt = (10, 10, 10)
    geo.radius = 0
    assert geo.identifier == 'new_sphere'
    assert geo.center_pt == (10, 10, 10)
    assert geo.radius == 0
    assert geo.to_radiance(minimal=True) == \
        'void sphere new_sphere 0 0 4 10.0 10.0 10.0 0.0'


def test_from_string():
    geometry_str = metal_sphere
    geo = Sphere.from_string(geometry_str)
    assert geo.identifier == 'sphere_one'
    assert geo.center_pt == (-77.3022, -78.4625, 415.900)
    assert geo.radius == 10
    assert ' '.join(geo.to_radiance(minimal=True).split()) == \
        ' '.join(geometry_str.split())


def test_from_and_to_dict():
    modifier = Plastic('sphere_material')
    sphere = Sphere('default_sphere', modifier=modifier)
    sphere_dict = sphere.to_dict()

    # check values in dictionary
    assert sphere_dict['identifier'] == 'default_sphere'
    assert sphere_dict['modifier'] == modifier.to_dict()
    assert sphere_dict['center_pt'] == (0, 0, 0)
    assert sphere_dict['radius'] == 10

    sphere_from_dict = Sphere.from_dict(sphere_dict)

    assert sphere_from_dict.to_radiance() == sphere.to_radiance()
