# TODO - add tests for dependencies

from honeybee_radiance.modifier.material import Glass
import pytest


def test_glass():
    gl = Glass('test_glass')
    assert gl.r_transmissivity == 0
    assert gl.g_transmissivity == 0
    assert gl.b_transmissivity == 0
    assert gl.refraction_index is None
    assert gl.to_radiance(
        minimal=True) == 'void glass test_glass 0 0 3 0.0 0.0 0.0'


def test_assign_values():
    gl = Glass('test_glass', 0.6, 0.7, 0.8, 1.52)
    assert gl.r_transmissivity == 0.6
    assert gl.g_transmissivity == 0.7
    assert gl.b_transmissivity == 0.8
    assert gl.refraction_index == 1.52
    assert gl.to_radiance(
        minimal=True) == 'void glass test_glass 0 0 4 0.6 0.7 0.8 1.52'


def test_material_lockability():
    """Test the lockability of Glass."""
    gl = Glass('test_glass', 0.6, 0.7, 0.8, 1.52)
    gl.r_transmissivity = 0.5
    gl.lock()
    with pytest.raises(AttributeError):
        gl.r_transmissivity = 0.7
    gl.unlock()
    gl.r_transmissivity = 0.7


def test_material_equivalency():
    """Test the equality of a material to another Glass."""
    gl_1 = Glass('test_glass', 0.6, 0.7, 0.8, 1.52)
    gl_2 = gl_1.duplicate()
    gl_3 = Glass('test_glass2', 0.8, 0.7, 0.8, 1.52)

    assert gl_1 is gl_1
    assert gl_1 is not gl_2
    assert gl_1 == gl_2
    assert gl_1 != gl_3
    collection = [gl_1, gl_2, gl_3]
    assert len(set(collection)) == 2


def test_update_values():
    gl = Glass('test_glass', 0.6, 0.7, 0.8, 1.52)
    gl.r_transmissivity = 0.5
    gl.g_transmissivity = 0.4
    gl.b_transmissivity = 0.3
    gl.refraction_index = 1.4
    assert gl.r_transmissivity == 0.5
    assert gl.g_transmissivity == 0.4
    assert gl.b_transmissivity == 0.3
    assert gl.refraction_index == 1.4
    assert gl.to_radiance(
        minimal=True) == 'void glass test_glass 0 0 4 0.5 0.4 0.3 1.4'


def test_from_string():
    glass_str = """void glass glass_alt_mat
        0
        0
        3
            0.91 0.92 0.93
            
    """
    gl = Glass.from_string(glass_str)
    assert gl.identifier == 'glass_alt_mat'
    assert gl.r_transmissivity == 0.91
    assert gl.g_transmissivity == 0.92
    assert gl.b_transmissivity == 0.93
    assert gl.to_radiance(minimal=True) == ' '.join(glass_str.split())


def test_from_dict_w_modifier():
    glass_mod = {
        "identifier": "test_glass_mod",
        "type": "Glass",
        "r_transmissivity": 0.4,
        "g_transmissivity": 0.5,
        "b_transmissivity": 0.6,
        "refraction_index": None,
        "modifier": None,
        "dependencies": []
    }

    glass_dict = {
        "identifier": "test_glass",
        "type": "Glass",
        "r_transmissivity": 0.1,
        "g_transmissivity": 0.2,
        "b_transmissivity": 0.3,
        "refraction_index": 1.52,
        "modifier": glass_mod,
        "dependencies": []
    }

    gg = Glass.from_dict(glass_dict)
    assert gg.to_radiance(minimal=True, include_modifier=False) == \
        'test_glass_mod glass test_glass 0 0 4 0.1 0.2 0.3 1.52'
    assert gg.modifier.to_radiance(minimal=True) == \
        'void glass test_glass_mod 0 0 3 0.4 0.5 0.6'


def test_from_transmittance():
    gl = Glass.from_transmittance('gl_test', 0.6, 0.7, 0.8)
    assert round(gl.r_transmissivity, 2) == 0.65
    assert round(gl.g_transmissivity, 2) == 0.76
    assert round(gl.b_transmissivity, 2) == 0.87

    assert round(gl.r_transmittance, 2) == 0.6
    assert round(gl.g_transmittance, 2) == 0.7
    assert round(gl.b_transmittance, 2) == 0.8


def test_from_single_value():
    gl = Glass.from_single_transmissivity('gl_test', 0.6)
    assert gl.r_transmissivity == 0.6
    assert gl.g_transmissivity == 0.6
    assert gl.b_transmissivity == 0.6

    assert round(gl.average_transmissivity, 2) == 0.6


def test_from_single_transmittance():
    gl = Glass.from_single_transmittance('gl_65', 0.6)
    assert round(gl.r_transmissivity, 2) == 0.65
    assert round(gl.g_transmissivity, 2) == 0.65
    assert round(gl.b_transmissivity, 2) == 0.65

    assert round(gl.average_transmittance, 2) == 0.6

    assert round(gl.r_transmittance, 2) == 0.6
    assert round(gl.g_transmittance, 2) == 0.6
    assert round(gl.b_transmittance, 2) == 0.6

    gl.r_transmittance = 0.4
    gl.g_transmittance = 0.4
    gl.b_transmittance = 0.4

    assert round(gl.r_transmittance, 2) == 0.4
    assert round(gl.g_transmittance, 2) == 0.4
    assert round(gl.b_transmittance, 2) == 0.4
