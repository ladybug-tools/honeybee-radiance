from honeybee_radiance.lightsource.sky.hemisphere import Hemisphere
import os


def test_defaults():
    hem = Hemisphere()
    assert hem.r_emittance == hem.b_emittance == hem.g_emittance == 1.0
    assert hem.to_radiance() == \
        'skyfunc glow sky_glow\n0\n0\n4 1.000 1.000 1.000 0\n' \
        'sky_glow source sky\n0\n0\n4 0 0 1 180'


def test_update_values():
    """Updating values for sky is not encouraged but is possible."""
    hem = Hemisphere()
    hem.r_emittance = 0
    hem.g_emittance = 0.5
    hem.b_emittance = 1

    assert hem.r_emittance == 0.0
    assert hem.g_emittance == 0.5
    assert hem.b_emittance == 1.0
    assert hem.to_radiance() == \
        'skyfunc glow sky_glow\n0\n0\n4 0.000 0.500 1.000 0\n' \
        'sky_glow source sky\n0\n0\n4 0 0 1 180'


def test_to_and_from_dict():
    hem = Hemisphere()
    assert hem.to_dict() == {
        'type': 'SkyHemisphere',
        'r_emittance': 1.0, 'g_emittance': 1.0, 'b_emittance': 1.0, 'modifier': 'skyfunc'
    }
    assert hem == Hemisphere.from_dict(hem.to_dict())


def test_to_file():
    hem = Hemisphere()
    sky_file = hem.to_file('./tests/assets/temp', mkdir=True)
    assert os.path.isfile(sky_file)
    with open(sky_file, 'r') as gf:
        content = gf.read()

    assert hem.to_radiance() in str(content)
