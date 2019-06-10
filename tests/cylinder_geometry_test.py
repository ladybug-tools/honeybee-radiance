from honeybee_radiance.primitive.geometry import Cylinder
from honeybee_radiance.primitive.material import Plastic
import ladybug_geometry.geometry3d.pointvector as pv
from .rad_string_collection import metal_cylinder

def test_cylinder():
    geo = Cylinder('test_cylinder')
    assert geo.name == 'test_cylinder'
    assert geo.center_pt_start == pv.Point3D(0, 0, 0)
    assert geo.center_pt_end == pv.Point3D(0, 0, 10)
    assert geo.radius == 10
    assert geo.to_radiance(
        minimal=True) == \
            'void cylinder test_cylinder 0 0 7 0.0 0.0 0.0 0.0 0.0 10.0 10.0'


def test_assign_values():
    geo = Cylinder('test_cylinder', (0.6, 0.7, 0.8), (0, 0, 0), 100)
    assert geo.name == 'test_cylinder'
    assert geo.center_pt_start == pv.Point3D(0.6, 0.7, 0.8)
    assert geo.center_pt_end == pv.Point3D(0, 0, 0)
    assert geo.radius == 100
    assert geo.to_radiance(minimal=True) == \
        'void cylinder test_cylinder 0 0 7 0.6 0.7 0.8 0.0 0.0 0.0 100.0'


def test_update_values():
    geo = Cylinder('test_cylinder', (0.6, 0.7, 0.8), (0, 0, 0), 100)
    geo.name = 'new_cylinder'
    geo.center_pt_start = pv.Point3D(10, 10, 10)
    geo.center_pt_end = pv.Point3D(0, 0, 0)
    geo.radius = 0
    assert geo.name == 'new_cylinder'
    assert geo.center_pt_start == pv.Point3D(10, 10, 10)
    assert geo.center_pt_end == pv.Point3D(0, 0, 0)
    assert geo.radius == 0
    assert geo.to_radiance(minimal=True) == \
        'void cylinder new_cylinder 0 0 7 10.0 10.0 10.0 0.0 0.0 0.0 0.0'


def test_from_string():
    geometry_str = metal_cylinder
    geo = Cylinder.from_string(geometry_str)
    assert geo.name == 'cylinder_one'
    assert geo.center_pt_start == pv.Point3D(-77.3022, -78.4625, 415.900)
    assert geo.center_pt_end == pv.Point3D(-81.9842, -78.9436, 420.900)
    assert geo.radius == 10
    assert ' '.join(geo.to_radiance(minimal=True).split()) == \
        ' '.join(geometry_str.split())


def test_from_and_to_dict():
    modifier = Plastic('cylinder_material')
    cylinder = Cylinder('default_cylinder', modifier=modifier)
    cylinder_dict = cylinder.to_dict()

    # check values in dictionary
    assert cylinder_dict['name'] == 'default_cylinder'
    assert cylinder_dict['modifier'] == modifier.to_dict()
    assert cylinder_dict['center_pt_start'] == pv.Point3D(0, 0, 0).to_dict()
    assert cylinder_dict['center_pt_end'] == pv.Point3D(0, 0, 10).to_dict()
    assert cylinder_dict['radius'] == 10

    cylinder_from_dict = Cylinder.from_dict(cylinder_dict)

    assert cylinder_from_dict.to_radiance() == cylinder.to_radiance()
