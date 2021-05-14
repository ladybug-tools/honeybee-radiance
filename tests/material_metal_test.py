from honeybee_radiance.modifier.material import Metal

import pytest

def test_metal():
    mt = Metal('test_metal')
    assert mt.r_reflectance == 0
    assert mt.g_reflectance == 0
    assert mt.b_reflectance == 0
    assert mt.specularity == 0.9
    assert mt.roughness == 0
    assert mt.to_radiance(
        minimal=True) == 'void metal test_metal 0 0 5 0.0 0.0 0.0 0.9 0.0'


def test_assign_values():
    mt = Metal('test_metal', 0.6, 0.7, 0.8, 0, 0)
    assert mt.r_reflectance == 0.6
    assert mt.g_reflectance == 0.7
    assert mt.b_reflectance == 0.8
    assert mt.specularity == 0
    assert mt.roughness == 0
    assert mt.to_radiance(
        minimal=True) == 'void metal test_metal 0 0 5 0.6 0.7 0.8 0.0 0.0'


def test_material_lockability():
    """Test the lockability of Metal."""
    mt = Metal('test_metal', 0.6, 0.7, 0.8, 0, 0)
    mt.r_reflectance = 0.5
    mt.lock()
    with pytest.raises(AttributeError):
        mt.r_reflectance = 0.7
    mt.unlock()
    mt.r_reflectance = 0.7


def test_material_equivalency():
    """Test the equality of a material to another."""
    mt_1 = Metal('test_metal', 0.6, 0.7, 0.8, 0, 0)
    mt_2 = mt_1.duplicate()
    mt_3 = Metal('test_metal2', 0.8, 0.7, 0.8, 0, 0)

    assert mt_1 is mt_1
    assert mt_1 is not mt_2
    assert mt_1 == mt_2
    assert isinstance(mt_2, Metal)
    assert mt_1 != mt_3
    collection = [mt_1, mt_2, mt_3]
    assert len(set(collection)) == 2


def test_update_values():
    mt = Metal('test_metal', 0.6, 0.7, 0.8, 0.1, 0.02)
    mt.r_reflectance = 0.5
    mt.g_reflectance = 0.4
    mt.b_reflectance = 0.3
    mt.specularity = 0.1
    mt.roughness = 0.02
    assert mt.r_reflectance == 0.5
    assert mt.g_reflectance == 0.4
    assert mt.b_reflectance == 0.3
    assert mt.specularity == 0.1
    assert mt.roughness == 0.02
    assert mt.to_radiance(minimal=True) == \
        'void metal test_metal 0 0 5 0.5 0.4 0.3 0.1 0.02'


def test_from_string():
    plastic_str = """void metal plastic_alt_mat
        0
        0
        5
            0.91 0.92 0.93
            0.3 0.4
            
    """
    mt = Metal.from_string(plastic_str)
    assert mt.identifier == 'plastic_alt_mat'
    assert mt.r_reflectance == 0.91
    assert mt.g_reflectance == 0.92
    assert mt.b_reflectance == 0.93
    assert mt.to_radiance(minimal=True) == ' '.join(plastic_str.split())


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

    plastic_dict = {
        "identifier": "test_metal",
        "type": "Metal",
        "r_reflectance": 0.1,
        "g_reflectance": 0.2,
        "b_reflectance": 0.3,
        "specularity": 0.01,
        "roughness": 0.02,
        "modifier": glass_mod,
        "dependencies": []
    }

    gg = Metal.from_dict(plastic_dict)
    assert gg.to_radiance(minimal=True, include_modifier=False) == \
        'test_glass_mod metal test_metal 0 0 5 0.1 0.2 0.3 0.01 0.02'
    assert gg.modifier.to_radiance(minimal=True) == \
        'void glass test_glass_mod 0 0 3 0.4 0.5 0.6'


def test_from_single_value():
    mt = Metal.from_single_reflectance('mt_test', 0.6)
    assert mt.r_reflectance == 0.6
    assert mt.g_reflectance == 0.6
    assert mt.b_reflectance == 0.6
