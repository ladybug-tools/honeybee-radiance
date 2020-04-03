from honeybee_radiance.view import View
import ladybug_geometry.geometry3d.pointvector as pv
import math
import pytest


def test_default_values():
    v = View('test_view')
    assert v.position == (0, 0, 0)
    assert v.direction == (0, 0, 1)
    assert v.up_vector == (0, 1, 0)
    assert v.type == 'v'
    assert v.h_size == 60
    assert v.v_size == 60
    assert v.fore_clip.to_radiance() == ''
    assert v.aft_clip.to_radiance() == ''
    assert v.to_radiance() == '-vtv -vp 0.0 0.0 0.0 -vd 0.0 0.0 1.0' \
        ' -vu 0.0 1.0 0.0 -vh 60.0 -vv 60.0'


def test_value_assignment():
    v = View(
        'test_view', (0, 0, 10), (0, 1, 0), (0, 0, 1), 'l', 240, 300, -10, -25
    )
    assert v.position == (0, 0, 10)
    assert v.direction == (0, 1, 0)
    assert v.up_vector == (0, 0, 1)
    assert v.type == 'l'
    assert v.h_size == 240
    assert v.v_size == 300
    assert v.shift == -10
    assert v.lift == -25
    assert v.fore_clip.to_radiance() == ''
    assert v.to_radiance() == '-vtl -vp 0.0 0.0 10.0 -vd 0.0 1.0 0.0' \
        ' -vu 0.0 0.0 1.0 -vh 240.0 -vv 300.0 -vs -10.0 -vl -25.0'


def test_value_update():
    v = View('__')
    v.position = (0, 0, 10)
    v.direction = (0, 1, 0)
    v.up_vector = (0, 0, 1)
    v.type = 'l'
    v.h_size = 240
    v.v_size = 300
    v.shift = -10
    v.lift = -25
    v.fore_clip = 30
    v.aft_clip = 50

    assert v.position == (0, 0, 10)
    assert v.direction == (0, 1, 0)
    assert v.up_vector == (0, 0, 1)
    assert v.type == 'l'
    assert v.h_size == 240
    assert v.v_size == 300
    assert v.shift == -10
    assert v.lift == -25
    assert v.fore_clip == 30
    assert v.aft_clip == 50
    assert v.to_radiance() == '-vtl -vp 0.0 0.0 10.0 -vd 0.0 1.0 0.0' \
        ' -vu 0.0 0.0 1.0 -vh 240.0 -vv 300.0 -vs -10.0 -vl -25.0 ' \
        '-vo 30.0 -va 50.0'


def test_dimensions():
    view_string = 'rvu -vtv -vp 1.000 8.000 2.000 -vd 3.000 -2.000 0.000' \
        ' -vu 0.000 0.000 1.000 -vh 120.000 -vv 45.000'
    view = View.from_string('test_view', view_string)
    x, y = view.dimension_x_y(512, 512)
    assert x == 512
    assert y == 122

    assert view.dimension(512, 512) == '-x 512 -y 122 -ld-'


def test_move():
    v = View('test_view')
    v.move((10, 20, 30))

    assert v.position == (10, 20, 30)
    assert v.up_vector == (0, 1, 0)

def test_rotate():
    v = View('test_view', (0, 0, 0), (1, 0, 0), (0, 0, 1))
    v.rotate(0.5 * math.pi, (0, 1, 1), (0, 0, 20))
    assert round(v.position[0], 3) == -14.142
    assert round(v.position[1]) == -10
    assert round(v.position[2]) == 10
    assert round(v.up_vector[0], 3) == 0.707
    assert round(v.up_vector[1], 1) == 0.5
    assert round(v.up_vector[2], 1) == 0.5
    assert round(v.direction[0], 1) == 0.0
    assert round(v.direction[1], 3) == 0.707
    assert round(v.direction[2], 3) == -0.707

def test_from_string():
    view = 'rvu -vtv -vp 0.000 0.000 0.000 -vd 0.000 0.000 1.000 ' \
        '-vu 0.000 1.000 0.000 -vh 29.341 -vv 32.204 ' \
        '-vs -0.500 -vl -0.500 -vo 100.000 -va 200.000'

    vw = View.from_string('test_view', view)
    assert list(vw.position) == [0, 0, 0]
    assert list(vw.direction) == [0, 0, 1]
    assert list(vw.up_vector) == [0, 1, 0]
    assert vw.h_size == 29.341
    assert vw.v_size == 32.204
    assert vw.shift == -0.500
    assert vw.lift == -0.500
    assert vw.fore_clip == 100
    assert vw.aft_clip == 200


def test_from_file():
    vw = View.from_file('./tests/assets/view.vf')
    assert vw.identifier == 'view'
    assert list(vw.position) == [0, 0, 0]
    assert list(vw.direction) == [0, 0, 1]
    assert list(vw.up_vector) == [0, 1, 0]
    assert vw.h_size == 29.341
    assert vw.v_size == 32.204
    assert vw.shift == -0.500
    assert vw.lift == -0.500
    assert vw.fore_clip == 100
    assert vw.aft_clip == 200
