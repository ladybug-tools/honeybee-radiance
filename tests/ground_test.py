from honeybee_radiance.lightsource.ground import Ground
import os


def test_defaults():
    gr = Ground()
    assert gr.r_emittance == gr.b_emittance == gr.g_emittance == 1.0
    assert gr.to_radiance() == \
        'skyfunc glow ground_glow\n0\n0\n4 1.000 1.000 1.000 0\n' \
        'ground_glow source ground\n0\n0\n4 0 0 -1 180'


def test_update_values():
    """Updating values for ground is not encouraged but is possible."""
    gr = Ground()
    gr.r_emittance = 0
    gr.g_emittance = 0.5
    gr.b_emittance = 1

    assert gr.r_emittance == 0.0
    assert gr.g_emittance == 0.5
    assert gr.b_emittance == 1.0
    assert gr.to_radiance() == \
        'skyfunc glow ground_glow\n0\n0\n4 0.000 0.500 1.000 0\n' \
        'ground_glow source ground\n0\n0\n4 0 0 -1 180'


def test_to_and_from_dict():
    gr = Ground()
    assert gr.to_dict() == {
        'type': 'Ground', 'r_emittance': 1.0, 'g_emittance': 1.0, 'b_emittance': 1.0,
        'modifier': 'skyfunc'
    }
    assert gr == Ground.from_dict(gr.to_dict())


def test_to_file():
    gr = Ground()
    ground_file = gr.to_file('./tests/assets/temp', mkdir=True)
    assert os.path.isfile(ground_file)
    with open(ground_file, 'r') as gf:
        content = gf.read()

    assert gr.to_radiance() in str(content)
