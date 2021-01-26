"""Test SensorGrid class."""
from honeybee_radiance.sensor import Sensor
from honeybee_radiance.sensorgrid import SensorGrid
import ladybug_geometry.geometry3d.pointvector as pv
from ladybug_geometry.geometry3d.plane import Plane
from ladybug_geometry.geometry2d.pointvector import Point2D
from ladybug_geometry.geometry2d.mesh import Mesh2D
from ladybug_geometry.geometry3d.mesh import Mesh3D
import pytest


sensors = [Sensor((0, 0, 0), (0, 0, 1)), Sensor((0, 0, 10), (0, 0, 1))]


def test_creation():
    sg = SensorGrid('sg_1', sensors)
    str(sg)  # test string representation
    hash(sg)  # test hashability

    assert sg.identifier == 'sg_1'
    assert len(sg) == 2
    assert sg[0] == sensors[0]
    assert sg[1] == sensors[1]


def test_updating_values():
    sg = SensorGrid('sg_1', sensors)
    # sensor is immutable - hence no assignment
    with pytest.raises(TypeError):
        sg.sensors[0] = Sensor((0, 0, 100), (0, 0, -10))


def test_invalid_input():
    with pytest.raises(ValueError):
        SensorGrid('sg_1', ((0, 0, 0, 0, 0, 1),))


def test_assigning_group():
    sg = SensorGrid('sg_1', sensors)
    sg.group_identifier = 'floor_1/dining_room'
    str(sg)  # test string representation
    hash(sg)  # test hashability

    assert sg.identifier == 'sg_1'
    assert sg.group_identifier == 'floor_1/dining_room'
    assert len(sg) == 2
    assert sg[0] == sensors[0]
    assert sg[1] == sensors[1]


def test_from_planar_positions():
    positions = [[0, 0, 0], [0, 0, 5], [0, 0, 10]]
    plane_normal = [0, 0, 1]
    sg = SensorGrid.from_planar_positions('test_grid', positions, plane_normal)
    assert len(sg) == 3
    for sensor in sg:
        assert sensor.dir == (0, 0, 1)


def test_from_loc_dir():
    positions = [[0, 0, 0], [0, 0, 5], [0, 0, 10]]
    directions = [[0, 0, 1], [0, 0, -1], [0, 0, 10]]
    sg = SensorGrid.from_position_and_direction('sg', positions, directions)
    for count, sensor in enumerate(sg):
        list(sensor.pos) == positions[count]
        list(sensor.dir) == directions[count]


def test_from_mesh3d():
    mesh_2d = Mesh2D.from_grid(Point2D(1, 1), 8, 2, 0.25, 1)
    mesh = Mesh3D.from_mesh2d(mesh_2d)
    sg = SensorGrid.from_mesh3d('sg_1', mesh)

    assert len(sg.sensors) == 16
    assert len(sg.mesh.vertices) == 27
    assert len(sg.mesh.faces) == 16
    assert mesh.area == 4


def test_from_file():
    sensor_grid = SensorGrid.from_file('./tests/assets/test_points.pts')
    assert sensor_grid.identifier == 'test_points'
    assert sensor_grid[0].pos == (0, 0, 0)
    assert sensor_grid[0].dir == (0, 0, 1)
    assert len(sensor_grid) == 3
    assert sensor_grid[1].to_radiance() == '0.2 0.3 0.4 0.5 0.6 0.7'
    assert sensor_grid[2].to_radiance() == '-10.0 -5.0 0.0 -50.0 -60.0 -70.0'


def test_move():
    sensor = Sensor((0, 0, 10), (0, 0, -1))
    sensors = [Sensor((0, 0, 0), (0, 0, 1)), Sensor((0, 0, 10), (0, 0, 1)), sensor]
    sg = SensorGrid('sg_1', sensors)
    sg.move(pv.Vector3D(10, 20, 30))

    assert sensor.pos == (10, 20, 40)
    assert sensor.dir == (0, 0, -1)


def test_rotate():
    sensor = Sensor((0, 0, 0), (1, 0, 0))
    sensors = [Sensor((0, 0, 0), (0, 0, 1)), Sensor((0, 0, 10), (0, 0, 1)), sensor]
    sg = SensorGrid('sg_1', sensors)
    sg.rotate(90, pv.Vector3D(0, 1, 1), pv.Point3D(0, 0, 20))

    assert round(sensor.pos[0], 3) == -14.142
    assert round(sensor.pos[1]) == -10
    assert round(sensor.pos[2]) == 10
    assert round(sensor.dir[0], 1) == 0.0
    assert round(sensor.dir[1], 3) == 0.707
    assert round(sensor.dir[2], 3) == -0.707


def test_rotate_xy():
    sensor = Sensor((1, 0, 2), (2, 0, 0))
    sensors = [Sensor((0, 0, 0), (0, 0, 1)), Sensor((0, 0, 10), (0, 0, 1)), sensor]
    sg = SensorGrid('sg_1', sensors)
    sg.rotate_xy(90, pv.Point3D(0, 0, 0))

    assert round(sensor.pos[0]) == 0
    assert round(sensor.pos[1]) == 1
    assert round(sensor.pos[2]) == 2
    assert round(sensor.dir[0]) == 0
    assert round(sensor.dir[1]) == 2
    assert round(sensor.dir[2]) == 0


def test_reflect():
    sensor = Sensor((1, 0, 2), (2, 0, 0))
    sensors = [Sensor((0, 0, 0), (0, 0, 1)), Sensor((0, 0, 10), (0, 0, 1)), sensor]
    sg = SensorGrid('sg_1', sensors)
    sg.reflect(Plane(pv.Vector3D(1, 0, 0), pv.Point3D(0, 0, 0)))

    assert round(sensor.pos[0]) == -1
    assert round(sensor.pos[1]) == 0
    assert round(sensor.pos[2]) == 2
    assert round(sensor.dir[0]) == -2
    assert round(sensor.dir[1]) == 0
    assert round(sensor.dir[2]) == 0


def test_scale():
    sensor = Sensor((1, 0, 2), (1, 0, 0))
    sensors = [Sensor((0, 0, 0), (0, 0, 1)), Sensor((0, 0, 10), (0, 0, 1)), sensor]
    sg = SensorGrid('sg_1', sensors)
    sg.scale(2)

    assert round(sensor.pos[0]) == 2
    assert round(sensor.pos[1]) == 0
    assert round(sensor.pos[2]) == 4
    assert round(sensor.dir[0]) == 1
    assert round(sensor.dir[1]) == 0
    assert round(sensor.dir[2]) == 0


def test_to_radiance():
    sg = SensorGrid('sg', sensors)
    sg.to_radiance() == \
        """0.0 0.0 0.0 0.0 0.0 1.0\n0.0 0.0 10.0 0.0 0.0 1.0"""


def test_to_and_from_dict():
    sg = SensorGrid('sg', sensors)
    sg_dict = sg.to_dict()
    assert sg_dict == {
        'type': 'SensorGrid',
        'identifier': 'sg',
        'sensors': [
            {'pos': (0, 0, 0), 'dir': (0, 0, 1)},
            {'pos': (0, 0, 10), 'dir': (0, 0, 1)}
        ]
    }

    sensor_from = SensorGrid.from_dict(sg_dict)
    assert sensor_from == sg
    assert sg_dict == sensor_from.to_dict()


def test_split_single_grid():
    """Test splitting a sensor grid."""
    sensor_grid = SensorGrid.from_file('./tests/assets/grid/sensor_grid_split.pts')
    folder = './tests/assets/temp'
    info = sensor_grid.to_files(folder, 1, 'single_grid')
    assert len(info) == 1
    assert info[0]['count'] == sensor_grid.count


def test_split_grid():
    """Test splitting a sensor grid."""
    sensor_grid = SensorGrid.from_file('./tests/assets/grid/sensor_grid_split.pts')
    folder = './tests/assets/temp'
    info = sensor_grid.to_files(folder, 6, 'test_sensor_grid')
    assert len(info) == 6
    for i in range(6 - 1):
        assert info[i]['count'] == 4

    assert info[-1]['count'] == 1
