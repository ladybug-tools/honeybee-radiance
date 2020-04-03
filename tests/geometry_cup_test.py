"""tests for cup.

Cup is identical to Cone except for the name. If cone works cup will also work.
"""
from honeybee_radiance.geometry import Cup


def test_cup():
    geo = Cup('test_cup')
    assert geo.identifier == 'test_cup'
    assert geo.to_radiance(
        minimal=True) == 'void cup test_cup 0 0 8 0.0 0.0 0.0 0.0 0.0 10.0 10.0 0.0'
