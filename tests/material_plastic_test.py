from honeybee_radiance.modifier.material import Plastic

import pytest


def test_plastic():
    pl = Plastic('test_plastic')
    assert pl.r_reflectance == 0
    assert pl.g_reflectance == 0
    assert pl.b_reflectance == 0
    assert pl.specularity == 0
    assert pl.roughness == 0
    assert pl.to_radiance(
        minimal=True) == 'void plastic test_plastic 0 0 5 0.0 0.0 0.0 0.0 0.0'


def test_assign_values():
    pl = Plastic('test_plastic', 0.6, 0.7, 0.8, 0, 0)
    assert pl.r_reflectance == 0.6
    assert pl.g_reflectance == 0.7
    assert pl.b_reflectance == 0.8
    assert pl.specularity == 0
    assert pl.roughness == 0
    assert pl.to_radiance(
        minimal=True) == 'void plastic test_plastic 0 0 5 0.6 0.7 0.8 0.0 0.0'


def test_material_lockability():
    """Test the lockability of Plastic."""
    pl = Plastic('test_plastic', 0.6, 0.7, 0.8, 0, 0)
    pl.r_reflectance = 0.5
    pl.lock()
    with pytest.raises(AttributeError):
        pl.r_reflectance = 0.7
    pl.unlock()
    pl.r_reflectance = 0.7


def test_material_equivalency():
    """Test the equality of a material to another."""
    pl_1 = Plastic('test_plastic', 0.6, 0.7, 0.8, 0, 0)
    pl_2 = pl_1.duplicate()
    pl_3 = Plastic('test_plastic2', 0.8, 0.7, 0.8, 0, 0)

    assert pl_1 is pl_1
    assert pl_1 is not pl_2
    assert pl_1 == pl_2
    assert isinstance(pl_2, Plastic)
    assert pl_1 != pl_3
    collection = [pl_1, pl_2, pl_3]
    assert len(set(collection)) == 2
    
    pl_2.r_reflectance = 0.7
    assert pl_1 != pl_2


def test_update_values():
    pl = Plastic('test_plastic', 0.6, 0.7, 0.8, 0.1, 0.02)
    pl.r_reflectance = 0.5
    pl.g_reflectance = 0.4
    pl.b_reflectance = 0.3
    pl.specularity = 0.1
    pl.roughness = 0.02
    assert pl.r_reflectance == 0.5
    assert pl.g_reflectance == 0.4
    assert pl.b_reflectance == 0.3
    assert pl.specularity == 0.1
    assert pl.roughness == 0.02
    assert pl.to_radiance(minimal=True) == \
        'void plastic test_plastic 0 0 5 0.5 0.4 0.3 0.1 0.02'


def test_from_string():
    plastic_str = """void plastic plastic_alt_mat
        0
        0
        5
            0.91 0.92 0.93
            0.3 0.4
            
    """
    pl = Plastic.from_string(plastic_str)
    assert pl.identifier == 'plastic_alt_mat'
    assert pl.r_reflectance == 0.91
    assert pl.g_reflectance == 0.92
    assert pl.b_reflectance == 0.93
    assert pl.to_radiance(minimal=True) == ' '.join(plastic_str.split())


def test_from_dict_w_modifier():
    glass_mod = {
        "identifier": "test_glass_mod",
        "type": "glass",
        "r_transmissivity": 0.4,
        "g_transmissivity": 0.5,
        "b_transmissivity": 0.6,
        "refraction_index": None,
        "modifier": None,
        "dependencies": []
    }

    plastic_dict = {
        "identifier": "test_plastic",
        "type": "plastic",
        "r_reflectance": 0.1,
        "g_reflectance": 0.2,
        "b_reflectance": 0.3,
        "specularity": 0.01,
        "roughness": 0.02,
        "modifier": glass_mod,
        "dependencies": []
    }

    gg = Plastic.from_dict(plastic_dict)
    assert gg.to_radiance(minimal=True, include_modifier=False) == \
        'test_glass_mod plastic test_plastic 0 0 5 0.1 0.2 0.3 0.01 0.02'
    assert gg.modifier.to_radiance(minimal=True) == \
        'void glass test_glass_mod 0 0 3 0.4 0.5 0.6'


def test_from_single_value():
    pl = Plastic.from_single_reflectance('gl_test', 0.6)
    assert pl.r_reflectance == 0.6
    assert pl.g_reflectance == 0.6
    assert pl.b_reflectance == 0.6
