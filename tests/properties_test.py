from honeybee.face import Face
from honeybee_radiance.properties import FaceRadianceProperties
from honeybee_radiance.lib.modifiers import generic_wall


face = Face.from_vertices(
    'wall_face', [[0, 0, 0], [10, 0, 0], [10, 0, 10], [0, 0, 10]])


def test_defaults():
    rp = FaceRadianceProperties(face)
    assert rp.modifier == generic_wall


def test_to_dict():
    rp = FaceRadianceProperties(face)
    rp_dict = rp.to_dict()
    assert 'radiance' in rp_dict
    assert 'modifier' in rp_dict['radiance']
