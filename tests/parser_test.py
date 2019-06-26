import honeybee_radiance.parser as parser
from .rad_string_collection import frit, microshade, metal_cone
import pytest


def test_frit():
    objects = parser.parse_from_string(frit)
    assert len(objects) == 3
    assert objects[0] == 'void glass glass_alt_mat 0 0 3 0.96 0.96 0.96'
    assert objects[1] == 'void brightfunc glass_angular_effect 2 ' \
        'A1+(1-A1) (exp(-5.85 Rdot)-0.00287989916) 0 1 0.08'
    assert objects[2] == 'glass_angular_effect mirror glass_mat 1 glass_alt_mat ' \
        '0 3 1 1 1'


def test_microshade():
    objects = parser.parse_from_string(microshade)
    assert len(objects) == 3
    assert objects[0] == 'void glass microshade_air 0 0 4 1 1 1 1'
    assert objects[1] == 'void plastic microshade_metal 0 0 5 0.1 0.1 0.1 0.017 0.005'
    assert objects[2] == 'void mixfunc microshade_a_mat 4 microshade_air ' \
        'microshade_metal trans microshade_a.cal 0 1 0'


def test_parser_three():
    objects = parser.parse_from_string(metal_cone)
    assert len(objects) == 2
    assert objects[0] == 'void metal metal_wall 0 0 5 0.0 0.0 0.0 0.95 0.0'
    assert objects[1] == 'metal_wall cone cone_one 0 0 8 -77.3022 -78.4625 415.9' \
        ' -81.9842 -78.9436 420.9 10.0 20.0'


def test_import_from_string():
    """Test import options form a string."""
    options = parser.parse_radiance_options('-dj   20  -fo -dc 1 -ab 16    -lw 1e-8')

    assert options['dj'] == '20'
    assert options['fo'] == ''
    assert options['dc'] == '1'
    assert options['ab'] == '16'
    assert options['lw'] == '1e-8'


def test_import_view_from_string():
    """Test import options form a string."""
    view = 'rvu -vtv -vp 0.000 0.000 0.000 -vd 0.000 0.000 1.000 ' \
        '-vu 0.000 1.000 0.000 -vh 29.341 -vv 32.204 -x 300 -y 300 ' \
        '-vs -0.500 -vl -0.500 -vo 100.000'

    options = parser.parse_radiance_options(view)
    
    assert 'rvu' not in options
    assert options['vtv'] == ''
    assert options['vp'] == ['0.000', '0.000', '0.000']
    assert options['vd'] == ['0.000', '0.000', '1.000']
    assert options['vu'] == ['0.000', '1.000', '0.000']
    assert options['vh'] == '29.341'
    assert options['vv'] == '32.204'
    assert options['x'] == '300'
    assert options['y'] == '300'
    assert options['vs'] == '-0.500'
    assert options['vl'] == '-0.500'
    assert options['vo'] == '100.000'


def test_parse_header():
    """Test parser for Radiance header."""
    filepath = './tests/assets/header_parser_test.amb'
    ln_count, header = parser.parse_header(filepath)
    assert ln_count == 7
    lines = [
        '#?RADIANCE',
        'rpict -av 0 0 0 -aw 0 -ab 3 -aa 0.2 -ad 2048 -as 2048 -ar 64 water_cube_IMG.oct',
        'CAPDATE= 2017:02:06 10:57:34', 'GMT= 2017:02:06 15:57:34',
        'FORMAT=Radiance_ambval'
    ]
    for line in lines:
        assert line in header

    with pytest.raises(ValueError):
        filepath = './tests/assets/klemsfull.xml'
        parser.parse_header(filepath)
