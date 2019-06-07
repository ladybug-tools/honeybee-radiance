from honeybee_radiance.parser import parse_from_string
from .rad_string_collection import frit, microshade, metal_cone


def test_frit():
    objects = parse_from_string(frit)
    assert len(objects) == 3
    assert objects[0] == 'void glass glass_alt_mat 0 0 3 0.96 0.96 0.96'
    assert objects[1] == 'void brightfunc glass_angular_effect 2 ' \
        'A1+(1-A1) (exp(-5.85 Rdot)-0.00287989916) 0 1 0.08'
    assert objects[2] == 'glass_angular_effect mirror glass_mat 1 glass_alt_mat ' \
        '0 3 1 1 1'


def test_microshade():
    objects = parse_from_string(microshade)
    assert len(objects) == 3
    assert objects[0] == 'void glass microshade_air 0 0 4 1 1 1 1'
    assert objects[1] == 'void plastic microshade_metal 0 0 5 0.1 0.1 0.1 0.017 0.005'
    assert objects[2] == 'void mixfunc microshade_a_mat 4 microshade_air ' \
        'microshade_metal trans microshade_a.cal 0 1 0'


def test_parser_three():
    objects = parse_from_string(metal_cone)
    assert len(objects) == 2
    assert objects[0] == 'void metal new_wall 0 0 5 0.000 0.000 0.000 0.950 0.000'
    assert objects[1] == 'new_wall cone floor_0_0_0 0 0 8 -77.3022 -78.4625 415.900' \
        ' -81.9842 -78.9436 420.900 10 20'
