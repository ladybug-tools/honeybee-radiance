"""tests for tube.

Tube is identical to Cylinder except for the name. If Cylinder works cup will also work.
"""
from honeybee_radiance.geometry import Tube


def test_cup():
    geo = Tube('test_tube')
    assert geo.identifier == 'test_tube'
    assert geo.to_radiance(
        minimal=True) == 'void tube test_tube 0 0 7 0.0 0.0 0.0 0.0 0.0 10.0 10.0'
