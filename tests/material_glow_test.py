from honeybee_radiance.modifier.material import Glow


def test_glow():
    mt = Glow('test_glow')
    assert mt.r_emittance == 0
    assert mt.g_emittance == 0
    assert mt.b_emittance == 0
    assert mt.max_radius == 0
    assert mt.to_radiance(
        minimal=True) == 'void glow test_glow 0 0 4 0.0 0.0 0.0 0.0'


def test_assign_values():
    mt = Glow('test_glow', 160, 170, 180, -1)
    assert mt.r_emittance == 160
    assert mt.g_emittance == 170
    assert mt.b_emittance == 180
    assert mt.max_radius == -1
    assert mt.to_radiance(
        minimal=True) == 'void glow test_glow 0 0 4 160.0 170.0 180.0 -1.0'


def test_update_values():
    mt = Glow('test_glow', 0.6, 0.7, 0.8, 20)
    mt.r_emittance = 0.5
    mt.g_emittance = 0.4
    mt.b_emittance = 0.3
    mt.max_radius = 200
    assert mt.r_emittance == 0.5
    assert mt.g_emittance == 0.4
    assert mt.b_emittance == 0.3
    assert mt.max_radius == 200
    assert mt.to_radiance(minimal=True) == \
        'void glow test_glow 0 0 4 0.5 0.4 0.3 200.0'


def test_from_string():
    glow_str = """void glow glow_alt_mat
        0
        0
        4
            100.0
            200.0
            
        10000.0
        240.0
            
    """
    mt = Glow.from_string(glow_str)
    assert mt.identifier == 'glow_alt_mat'
    assert mt.r_emittance == 100
    assert mt.g_emittance == 200
    assert mt.b_emittance == 10000
    assert mt.max_radius == 240
    assert mt.to_radiance(minimal=True) == ' '.join(glow_str.split())


def test_from_single_value():
    mt = Glow.from_single_value('mt_test', 100000, 200)
    assert mt.r_emittance == 100000
    assert mt.g_emittance == 100000
    assert mt.b_emittance == 100000
    assert mt.max_radius == 200


def test_to_dict():
    mt = Glow.from_single_value('mt_test', 100000)
    mdict = mt.to_dict()
    assert mdict['r_emittance'] == 100000
    assert mdict['b_emittance'] == 100000
    assert mdict['g_emittance'] == 100000
    assert mdict['max_radius'] == 0
    assert mdict['type'] == 'Glow'
    assert 'modifier' not in mdict or mdict['modifier'] is None


def test_to_from_dict():
    mt = Glow.from_single_value('mt_test', 100000)
    mdict = mt.to_dict()
    new_mt = Glow.from_dict(mdict)
    assert mt == new_mt
    assert new_mt.to_dict() == mdict
