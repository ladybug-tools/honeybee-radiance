"""tests for bubble.

Bubble is identical to Sphere except for the name. If Sphere works Bubble will also work.
"""
from honeybee_radiance.primitive.geometry import Bubble


def test_cup():
    geo = Bubble('test_bubble')
    assert geo.name == 'test_bubble'
    assert geo.to_radiance(
        minimal=True) == 'void bubble test_bubble 0 0 4 0.0 0.0 0.0 10.0'
