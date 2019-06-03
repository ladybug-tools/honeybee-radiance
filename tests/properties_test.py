from honeybee_radiance.properties import RadianceProperties
from honeybee.facetype import face_types
from honeybee.boundarycondition import boundary_conditions


def test_defaults():
    rp = RadianceProperties(face_types.wall, boundary_conditions.outdoors)
    assert rp.modifier == None
    assert rp._boundary_condition.name == 'Outdoors'


def test_to_dict():
    rp = RadianceProperties(face_types.wall, boundary_conditions.outdoors)
    rp_dict = rp.to_dict()
    assert 'radiance' in rp_dict
    assert 'modifier' in rp_dict['radiance']
