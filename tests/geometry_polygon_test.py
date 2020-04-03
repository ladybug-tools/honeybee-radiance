from honeybee_radiance.geometry import Polygon
from honeybee_radiance.modifier.material import Plastic
import ladybug_geometry.geometry3d.pointvector as pv
from .rad_string_collection import metal_polygon

vertices = [[3.0, -7.0, 15.0], [3.0, -1.0, 15.0], [3.0, -1.0, 0.0], [3.0, -7.0, 0.0]]
alt_vertices = \
    [[6.0, -10.0, 20.0], [6.0, -5.0, 20.0], [6.0, -5.0, 10.0], [6.0, -10.0, 10.0]]

def test_polygon():
    geo = Polygon('test_polygon', vertices)
    assert geo.identifier == 'test_polygon'
    assert geo.vertices == tuple(tuple(pt) for pt in vertices)
    assert geo.to_radiance(
        minimal=True) == \
            'void polygon test_polygon 0 0 12 3.0 -7.0 15.0 3.0 -1.0 15.0 ' \
            '3.0 -1.0 0.0 3.0 -7.0 0.0'


def test_assign_values():
    geo = Polygon('test_polygon',vertices)
    geo.identifier = 'new_polygon'
    geo.vertices = tuple(tuple(pt) for pt in alt_vertices)
    assert geo.to_radiance(minimal=True) == \
        'void polygon new_polygon 0 0 12 6.0 -10.0 20.0 6.0 -5.0 20.0 ' \
        '6.0 -5.0 10.0 6.0 -10.0 10.0'


def test_from_string():
    geometry_str = metal_polygon
    geo = Polygon.from_string(geometry_str)
    assert geo.identifier == 'polygon_one'
    assert geo.vertices == tuple(tuple(pt) for pt in vertices)
    assert ' '.join(geo.to_radiance(minimal=True).split()) == \
        ' '.join(geometry_str.split())


def test_from_and_to_dict():
    modifier = Plastic('polygon_material')
    polygon = Polygon('default_polygon', vertices, modifier=modifier)
    polygon_dict = polygon.to_dict()

    # check values in dictionary
    assert polygon_dict['identifier'] == 'default_polygon'
    assert polygon_dict['modifier'] == modifier.to_dict()
    assert polygon_dict['vertices'] == tuple(tuple(pt) for pt in vertices)

    polygon_from_dict = Polygon.from_dict(polygon_dict)

    assert polygon_from_dict.to_radiance() == polygon.to_radiance()
