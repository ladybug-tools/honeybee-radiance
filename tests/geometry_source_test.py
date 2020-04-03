from honeybee_radiance.geometry import Source
from honeybee_radiance.modifier.material import Plastic
from .rad_string_collection import metal_source


def test_source():
    geo = Source('test_source')
    assert geo.identifier == 'test_source'
    assert geo.direction == (0, 0, -1)
    assert geo.angle == 0.533
    assert geo.to_radiance(
        minimal=True) == \
            'void source test_source 0 0 4 0.0 0.0 -1.0 0.533'


def test_assign_values():
    geo = Source('test_source', (0.6, 0.7, 0.8), 100)
    assert geo.identifier == 'test_source'
    assert geo.direction == (0.6, 0.7, 0.8)
    assert geo.angle == 100
    assert geo.to_radiance(minimal=True) == \
        'void source test_source 0 0 4 0.6 0.7 0.8 100.0'


def test_update_values():
    geo = Source('test_source', (0.6, 0.7, 0.8), 100)
    geo.identifier = 'new_source'
    geo.direction = (10, 10, 10)
    geo.angle = 0
    assert geo.identifier == 'new_source'
    assert geo.direction == (10, 10, 10)
    assert geo.angle == 0
    assert geo.to_radiance(minimal=True) == \
        'void source new_source 0 0 4 10.0 10.0 10.0 0.0'


def test_from_string():
    geometry_str = metal_source
    geo = Source.from_string(geometry_str)
    assert geo.identifier == 'source_one'
    assert geo.direction == (0, 0, -1)
    assert geo.angle == 0.533
    assert ' '.join(geo.to_radiance(minimal=True).split()) == \
        ' '.join(geometry_str.split())


def test_from_and_to_dict():
    modifier = Plastic('source_material')
    source = Source('default_source', modifier=modifier)
    source_dict = source.to_dict()

    # check values in dictionary
    assert source_dict['identifier'] == 'default_source'
    assert source_dict['modifier'] == modifier.to_dict()
    assert source_dict['direction'] == (0, 0, -1)
    assert source_dict['angle'] == 0.533

    source_from_dict = Source.from_dict(source_dict)

    assert source_from_dict.to_radiance() == source.to_radiance()
