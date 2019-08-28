"""Tests for features add to honeybee by honeybee_radiance."""
from honeybee.face import Face
from honeybee_radiance.properties import FaceRadianceProperties


face = Face.from_vertices(
    'wall_face', [[0, 0, 0], [10, 0, 0], [10, 0, 10], [0, 0, 10]])


def test_radiance_properties():
    assert hasattr(face.properties, 'radiance')
    assert isinstance(face.properties.radiance, FaceRadianceProperties)


def test_writer_to_rad():
    assert hasattr(face.to, 'radiance')
    rad_string = face.to.radiance(face)
    assert 'polygon wall_face' in rad_string
    # TODO: Add more rigid tests here after adding default material set
