from honeybee_radiance.geometry import Cone
from honeybee_radiance.modifier.material import Plastic
from .rad_string_collection import metal_cone

def test_cone():
    geo = Cone('test_cone')
    assert geo.identifier == 'test_cone'
    assert geo.center_pt_start == (0, 0, 0)
    assert geo.center_pt_end == (0, 0, 10)
    assert geo.radius_start == 10
    assert geo.radius_end == 0
    assert geo.to_radiance(
        minimal=True) == 'void cone test_cone 0 0 8 0.0 0.0 0.0 0.0 0.0 10.0 10.0 0.0'


def test_assign_values():
    geo = Cone('test_cone', (0.6, 0.7, 0.8), 50, (0, 0, 0), 100)
    assert geo.identifier == 'test_cone'
    assert geo.center_pt_start == (0.6, 0.7, 0.8)
    assert geo.center_pt_end == (0, 0, 0)
    assert geo.radius_start == 50
    assert geo.radius_end == 100
    assert geo.to_radiance(minimal=True) == \
        'void cone test_cone 0 0 8 0.6 0.7 0.8 0.0 0.0 0.0 50.0 100.0'


def test_update_values():
    geo = Cone('test_cone', (0.6, 0.7, 0.8), 50, (0, 0, 0), 100)
    geo.identifier = 'new_cone'
    geo.center_pt_start = (10, 10, 10)
    geo.center_pt_end = (0, 0, 0)
    geo.radius_start = 0
    geo.radius_end = 20
    assert geo.identifier == 'new_cone'
    assert geo.center_pt_start == (10, 10, 10)
    assert geo.center_pt_end == (0, 0, 0)
    assert geo.radius_start == 0
    assert geo.radius_end == 20
    assert geo.to_radiance(minimal=True) == \
        'void cone new_cone 0 0 8 10.0 10.0 10.0 0.0 0.0 0.0 0.0 20.0'


def test_from_string():
    geometry_str = metal_cone
    geo = Cone.from_string(geometry_str)
    assert geo.identifier == 'cone_one'
    assert geo.center_pt_start == (-77.3022, -78.4625, 415.900)
    assert geo.center_pt_end == (-81.9842, -78.9436, 420.900)
    assert geo.radius_start == 10
    assert geo.radius_end == 20
    assert ' '.join(geo.to_radiance(minimal=True).split()) == \
        ' '.join(geometry_str.split())


def test_from_and_to_dict():
    modifier = Plastic('cone_material')
    cone = Cone('default_cone', modifier=modifier)
    cone_dict = cone.to_dict()

    # check values in dictionary
    assert cone_dict['identifier'] == 'default_cone'
    assert cone_dict['modifier'] == modifier.to_dict()
    assert cone_dict['center_pt_start'] == (0, 0, 0)
    assert cone_dict['center_pt_end'] == (0, 0, 10)
    assert cone_dict['radius_start'] == 10
    assert cone_dict['radius_end'] == 0

    cone_from_dict = Cone.from_dict(cone_dict)

    assert cone_from_dict.to_radiance() == cone.to_radiance()
