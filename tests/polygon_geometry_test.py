from honeybee_radiance.primitive.geometry import Polygon
from honeybee_radiance.primitive.material import Plastic
import ladybug_geometry.geometry3d.pointvector as pv
from .rad_string_collection import metal_polygon

vertices = [[3.0, -7.0, 15.0], [3.0, -1.0, 15.0], [3.0, -1.0, 0.0], [3.0, -7.0, 0.0]]
alt_vertices = \
    [[6.0, -10.0, 20.0], [6.0, -5.0, 20.0], [6.0, -5.0, 10.0], [6.0, -10.0, 10.0]]

def test_polygon():
    geo = Polygon('test_polygon', vertices)
    assert geo.name == 'test_polygon'
    assert geo.vertices == tuple(pv.Point3D(*v) for v in vertices)
    assert geo.to_radiance(
        minimal=True) == \
            'void polygon test_polygon 0 0 12 3.0 -7.0 15.0 3.0 -1.0 15.0 ' \
            '3.0 -1.0 0.0 3.0 -7.0 0.0'


def test_assign_values():
    geo = Polygon('test_polygon',vertices)
    geo.name = 'new_polygon'
    geo.vertices = tuple(pv.Point3D(*v) for v in alt_vertices)
    assert geo.to_radiance(minimal=True) == \
        'void polygon new_polygon 0 0 12 6.0 -10.0 20.0 6.0 -5.0 20.0 ' \
        '6.0 -5.0 10.0 6.0 -10.0 10.0'


def test_from_string():
    geometry_str = metal_polygon
    geo = Polygon.from_string(geometry_str)
    assert geo.name == 'polygon_one'
    assert geo.vertices == tuple(pv.Point3D(*v) for v in vertices)
    assert ' '.join(geo.to_radiance(minimal=True).split()) == \
        ' '.join(geometry_str.split())


def test_from_and_to_dict():
    modifier = Plastic('polygon_material')
    polygon = Polygon('default_polygon', vertices, modifier=modifier)
    polygon_dict = polygon.to_dict()

    # check values in dictionary
    assert polygon_dict['name'] == 'default_polygon'
    assert polygon_dict['modifier'] == modifier.to_dict()
    assert polygon_dict['vertices'] == [v.to_dict() for v in polygon.vertices]

    polygon_from_dict = Polygon.from_dict(polygon_dict)

    assert polygon_from_dict.to_radiance() == polygon.to_radiance()
