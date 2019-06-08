from honeybee_radiance.primitive.material import Metal


def test_metal():
    mt = Metal('test_metal')
    assert mt.r_reflectance == 0
    assert mt.g_reflectance == 0
    assert mt.b_reflectance == 0
    assert mt.specularity == 0
    assert mt.roughness == 0
    assert mt.to_radiance(
        minimal=True) == 'void metal test_metal 0 0 5 0.0 0.0 0.0 0.0 0.0'


def test_assign_values():
    mt = Metal('test_metal', 0.6, 0.7, 0.8, 0, 0)
    assert mt.r_reflectance == 0.6
    assert mt.g_reflectance == 0.7
    assert mt.b_reflectance == 0.8
    assert mt.specularity == 0
    assert mt.roughness == 0
    assert mt.to_radiance(
        minimal=True) == 'void metal test_metal 0 0 5 0.6 0.7 0.8 0.0 0.0'


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
    assert mt.name == 'plastic_alt_mat'
    assert mt.r_reflectance == 0.91
    assert mt.g_reflectance == 0.92
    assert mt.b_reflectance == 0.93
    assert mt.to_radiance(minimal=True) == ' '.join(plastic_str.split())


def test_from_dict_w_modifier():
    glass_mod = {
        "name": "test_glass_mod",
        "type": "glass",
        "r_transmissivity": 0.4,
        "g_transmissivity": 0.5,
        "b_transmissivity": 0.6,
        "refraction_index": None,
        "modifier": "void",
        "dependencies": []
    }

    plastic_dict = {
        "name": "test_metal",
        "type": "metal",
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
