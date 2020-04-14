from honeybee_radiance.modifier.material import Light


def test_light():
    mt = Light('test_light')
    assert mt.r_emittance == 0
    assert mt.g_emittance == 0
    assert mt.b_emittance == 0
    assert mt.to_radiance(
        minimal=True) == 'void light test_light 0 0 3 0.0 0.0 0.0'


def test_assign_values():
    mt = Light('test_light', 0.6, 0.7, 0.8)
    assert mt.r_emittance == 0.6
    assert mt.g_emittance == 0.7
    assert mt.b_emittance == 0.8
    assert mt.to_radiance(
        minimal=True) == 'void light test_light 0 0 3 0.6 0.7 0.8'


def test_update_values():
    mt = Light('test_light', 0.6, 0.7, 0.8)
    mt.r_emittance = 0.5
    mt.g_emittance = 0.4
    mt.b_emittance = 0.3
    assert mt.r_emittance == 0.5
    assert mt.g_emittance == 0.4
    assert mt.b_emittance == 0.3
    assert mt.to_radiance(minimal=True) == \
        'void light test_light 0 0 3 0.5 0.4 0.3'


def test_from_string():
    light_str = """void light light_alt_mat
        0
        0
        3
            100.0
            200.0
            
        10000.0
            
    """
    mt = Light.from_string(light_str)
    assert mt.identifier == 'light_alt_mat'
    assert mt.r_emittance == 100
    assert mt.g_emittance == 200
    assert mt.b_emittance == 10000
    assert mt.to_radiance(minimal=True) == ' '.join(light_str.split())


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

    light_dict = {
        "identifier": "test_light",
        "type": "light",
        "r_emittance": 0.1,
        "g_emittance": 0.2,
        "b_emittance": 0.3,
        "modifier": glass_mod,
        "dependencies": []
    }

    gg = Light.from_dict(light_dict)
    assert gg.to_radiance(minimal=True, include_modifier=False) == \
        'test_glass_mod light test_light 0 0 3 0.1 0.2 0.3'
    assert gg.modifier.to_radiance(minimal=True) == \
        'void glass test_glass_mod 0 0 3 0.4 0.5 0.6'


def test_from_single_value():
    mt = Light.from_single_value('mt_test', 100000)
    assert mt.r_emittance == 100000
    assert mt.g_emittance == 100000
    assert mt.b_emittance == 100000


def test_to_dict():
    mt = Light.from_single_value('mt_test', 100000)
    mdict = mt.to_dict()
    assert mdict['r_emittance'] == 100000
    assert mdict['b_emittance'] == 100000
    assert mdict['g_emittance'] == 100000
    assert mdict['type'] == 'light'
    assert 'modifier' not in mdict or mdict['modifier'] is None

