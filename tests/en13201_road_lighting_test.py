# coding=utf-8
"""Tests for honeybee_radiance.postprocess.en13201 pedestrian & road lighting."""
import pytest

from honeybee_radiance.dictutil import dict_to_object
from honeybee_radiance.sensorgrid import SensorGrid
from honeybee_radiance.postprocess.en13201 import (
    ESC_OBSERVER_HEIGHT_M,
    LIGHTING_PRESETS,
    En13201RoadLightingSolver,
    build_semicylindrical_illuminance_grid,
    compute_lux_sensory_multiplier,
    compute_night_perceived_safety_impedance,
    create_en13201_sensor_grid_pair,
)


def test_en13201_lighting_presets_catalog():
    """Verify all 6 EN 13201 road & pedestrian lighting presets are registered."""
    expected = {
        'DAYLIGHT_CLEAR',
        'DUSK_TRANSITION',
        'NIGHT_EN13201_M3',
        'NIGHT_EN13201_P2_UNIFORM',
        'NIGHT_EN13201_P4_LOW_UNIFORMITY',
        'NIGHT_HIGH_GLARE_TI',
    }
    assert set(LIGHTING_PRESETS.keys()) == expected
    with pytest.raises(ValueError):
        En13201RoadLightingSolver('NON_EXISTENT_PRESET')


def test_honeybee_semicylindrical_illuminance_grid_serialization():
    """Test Honeybee SensorGrid generation at z = 1.5 m and dict round-trip."""
    eh_sg, esc_sg = create_en13201_sensor_grid_pair(
        identifier_prefix='woodhouse_crossing',
        bounds_xy=(-10.0, -6.0, 10.0, 6.0),
        grid_res_m=5.0,
        observer_direction=(0.0, 1.0, 0.0),
    )
    assert isinstance(eh_sg, SensorGrid)
    assert isinstance(esc_sg, SensorGrid)
    assert eh_sg.count == esc_sg.count == 15

    for pos, direction in zip(esc_sg.positions, esc_sg.directions):
        assert pos[2] == pytest.approx(ESC_OBSERVER_HEIGHT_M)
        assert tuple(direction) == pytest.approx((0.0, 1.0, 0.0))

    reconstructed = dict_to_object(esc_sg.to_dict())
    assert isinstance(reconstructed, SensorGrid)
    assert reconstructed.identifier == 'woodhouse_crossing_esc'
    assert reconstructed.count == 15


def test_en13201_rasters_uniformity_and_glare_invariants(tmp_path):
    """Verify Eh, Esc, Ul, and TI% physical ordering across M3, P2, P4, and High-Glare."""
    day = En13201RoadLightingSolver(
        'DAYLIGHT_CLEAR', bounds_xy=(-30.0, -20.0, 30.0, 20.0)
    )
    p2 = En13201RoadLightingSolver(
        'NIGHT_EN13201_P2_UNIFORM', bounds_xy=(-30.0, -20.0, 30.0, 20.0)
    )
    m3 = En13201RoadLightingSolver(
        'NIGHT_EN13201_M3', bounds_xy=(-30.0, -20.0, 30.0, 20.0)
    )
    p4 = En13201RoadLightingSolver(
        'NIGHT_EN13201_P4_LOW_UNIFORMITY', bounds_xy=(-30.0, -20.0, 30.0, 20.0)
    )
    glare = En13201RoadLightingSolver(
        'NIGHT_HIGH_GLARE_TI', bounds_xy=(-30.0, -20.0, 30.0, 20.0)
    )

    q_day = day.query_at(0.0, 0.0)
    q_p2 = p2.query_at(0.0, 0.0)
    q_m3 = m3.query_at(0.0, 0.0)
    q_p4 = p4.query_at(0.0, 0.0)
    q_glare = glare.query_at(0.0, 0.0)

    assert q_day['eh_lux'] == pytest.approx(12000.0)
    assert q_m3['eh_lux'] > q_p4['eh_lux']
    assert q_p2['esc_lux'] > q_p4['esc_lux']
    assert p2.longitudinal_uniformity_ul > p4.longitudinal_uniformity_ul
    assert q_glare['ti_pct'] > q_p2['ti_pct']

    sg_esc = p2.build_sensor_grid_esc(sample_stride=5)
    assert isinstance(sg_esc, SensorGrid)
    assert sg_esc.count > 0

    comp_p2 = p2.evaluate_p_class_compliance('P2')
    comp_p4_against_p2 = p4.evaluate_p_class_compliance('P2')
    assert comp_p2['compliant'] is True
    assert comp_p4_against_p2['compliant'] is False

    out_npz = m3.export_npz(tmp_path / 'en13201_m3.npz')
    assert out_npz.exists()


def test_lux_sensory_multiplier_and_night_perceived_safety_impedance():
    """Verify scotopic/glare variance amplification and night-safety route choice."""
    psi_day = compute_lux_sensory_multiplier(eh_lux=12000.0, ti_pct=1.0)
    psi_p2 = compute_lux_sensory_multiplier(eh_lux=15.0, ti_pct=6.0)
    psi_dark_glare = compute_lux_sensory_multiplier(eh_lux=0.8, ti_pct=24.0)
    assert 1.0 <= psi_day < 1.10
    assert psi_day < psi_p2 < psi_dark_glare

    # Short dark isolated alley (walk_time=30s, Esc=0.5 lux, isolation=0.85)
    # vs slightly longer well-lit EN 13201 P2 street (walk_time=42s, Esc=7.5 lux, isolation=0.10)
    cost_dark_alley = compute_night_perceived_safety_impedance(
        walk_time_s=30.0, esc_lux=0.5, isolation_t=0.85, beta_dark=0.45
    )
    cost_lit_street = compute_night_perceived_safety_impedance(
        walk_time_s=42.0, esc_lux=7.5, isolation_t=0.10, beta_dark=0.45
    )
    assert cost_dark_alley > cost_lit_street
    assert build_semicylindrical_illuminance_grid('single_pt', [0.0], [0.0]).count == 1
