# coding=utf-8
"""EN 13201 pedestrian & road lighting SensorGrid generation, rasters, and safety metrics.

Implements European Standard EN 13201-2 / EN 13201-3 road and pedestrian lighting classes
(horizontal illuminance E_h, semi-cylindrical facial-recognition illuminance E_sc at 1.5 m,
longitudinal uniformity U_l, and disability glare Threshold Increment TI%) together with
psychophysical night-time visual degradation and perceived-safety route impedance models.
"""
from __future__ import division

from dataclasses import dataclass
import math
from pathlib import Path

import numpy as np

from ..sensorgrid import SensorGrid

ESC_FACIAL_HEIGHT_M = 1.50

# EN 13201-2 Table 3 (P-classes with facial recognition requirement: E_h_mean, E_h_min, E_sc_min)
EN13201_P_CLASS_REQUIREMENTS = {
    'P1': {'eh_mean_lux': 15.0, 'eh_min_lux': 3.0, 'esc_min_lux': 5.0, 'ti_max_pct': 20.0},
    'P2': {'eh_mean_lux': 10.0, 'eh_min_lux': 2.0, 'esc_min_lux': 3.0, 'ti_max_pct': 25.0},
    'P3': {'eh_mean_lux': 7.5, 'eh_min_lux': 1.5, 'esc_min_lux': 2.0, 'ti_max_pct': 25.0},
    'P4': {'eh_mean_lux': 5.0, 'eh_min_lux': 1.0, 'esc_min_lux': 1.0, 'ti_max_pct': 30.0},
    'P5': {'eh_mean_lux': 3.0, 'eh_min_lux': 0.6, 'esc_min_lux': 0.6, 'ti_max_pct': 30.0},
}


@dataclass(frozen=True)
class LuminairePreset(object):
    """EN 13201 road and pedestrian lighting luminaire configuration preset."""

    preset_name: str
    pole_spacing_m: float
    mounting_height_m: float
    luminous_flux_lm: float
    ambient_eh_lux: float
    ambient_esc_lux: float
    glare_ti_pct: float
    cct_kelvin: float = 4000.0
    cri_ra: float = 80.0


LIGHTING_PRESETS = {
    'DAYLIGHT_CLEAR': LuminairePreset(
        preset_name='DAYLIGHT_CLEAR',
        pole_spacing_m=30.0,
        mounting_height_m=8.0,
        luminous_flux_lm=0.0,
        ambient_eh_lux=12000.0,
        ambient_esc_lux=4500.0,
        glare_ti_pct=1.0,
        cct_kelvin=5800.0,
        cri_ra=98.0,
    ),
    'DUSK_TRANSITION': LuminairePreset(
        preset_name='DUSK_TRANSITION',
        pole_spacing_m=32.0,
        mounting_height_m=7.5,
        luminous_flux_lm=8500.0,
        ambient_eh_lux=45.0,
        ambient_esc_lux=16.0,
        glare_ti_pct=4.5,
        cct_kelvin=4200.0,
        cri_ra=85.0,
    ),
    'NIGHT_EN13201_M3': LuminairePreset(
        preset_name='NIGHT_EN13201_M3',
        pole_spacing_m=28.0,
        mounting_height_m=8.0,
        luminous_flux_lm=14500.0,
        ambient_eh_lux=2.0,
        ambient_esc_lux=0.8,
        glare_ti_pct=7.5,
        cct_kelvin=4000.0,
        cri_ra=82.0,
    ),
    'NIGHT_EN13201_P2_UNIFORM': LuminairePreset(
        preset_name='NIGHT_EN13201_P2_UNIFORM',
        pole_spacing_m=22.0,
        mounting_height_m=6.5,
        luminous_flux_lm=11000.0,
        ambient_eh_lux=2.5,
        ambient_esc_lux=1.2,
        glare_ti_pct=6.0,
        cct_kelvin=4000.0,
        cri_ra=85.0,
    ),
    'NIGHT_EN13201_P4_LOW_UNIFORMITY': LuminairePreset(
        preset_name='NIGHT_EN13201_P4_LOW_UNIFORMITY',
        pole_spacing_m=46.0,
        mounting_height_m=7.5,
        luminous_flux_lm=5200.0,
        ambient_eh_lux=0.6,
        ambient_esc_lux=0.25,
        glare_ti_pct=12.5,
        cct_kelvin=3000.0,
        cri_ra=70.0,
    ),
    'NIGHT_HIGH_GLARE_TI': LuminairePreset(
        preset_name='NIGHT_HIGH_GLARE_TI',
        pole_spacing_m=38.0,
        mounting_height_m=5.2,
        luminous_flux_lm=13000.0,
        ambient_eh_lux=1.2,
        ambient_esc_lux=0.5,
        glare_ti_pct=24.0,
        cct_kelvin=5000.0,
        cri_ra=72.0,
    ),
}


def build_facial_recognition_sensor_grid(
    identifier,
    xs,
    ys,
    z_height_m=ESC_FACIAL_HEIGHT_M,
    observer_direction=(0.0, 1.0, 0.0),
):
    """Create a Honeybee ``SensorGrid`` at ``z = 1.5 m`` for EN 13201 semi-cylindrical E_sc.

    Args:
        identifier: Clean SensorGrid identifier string without spaces.
        xs: 1D sequence of X coordinates in meters.
        ys: 1D sequence of Y coordinates in meters.
        z_height_m: Sensor elevation above ground in meters. Defaults to 1.5 m per EN 13201-2.
        observer_direction: Horizontal facing normal ``(dx, dy, dz)`` for semi-cylindrical
            facial recognition evaluation.

    Returns:
        A ``honeybee_radiance.sensorgrid.SensorGrid`` object.
    """
    positions = [
        (float(x), float(y), float(z_height_m))
        for y in ys
        for x in xs
    ]
    directions = [tuple(float(c) for c in observer_direction)] * len(positions)
    sg = SensorGrid.from_position_and_direction(identifier, positions, directions)
    sg.display_name = 'EN 13201 Facial Recognition Esc Grid ({:.2f}m)'.format(z_height_m)
    return sg


def create_en13201_sensor_grid_pair(
    identifier_prefix='en13201_corridor',
    bounds_xy=(-30.0, -15.0, 30.0, 15.0),
    grid_res_m=2.0,
    esc_height_m=ESC_FACIAL_HEIGHT_M,
    observer_direction=(0.0, 1.0, 0.0),
):
    """Create paired horizontal (z=0 m) and semi-cylindrical (z=1.5 m) Honeybee SensorGrids.

    Args:
        identifier_prefix: Prefix for the ``_eh`` and ``_esc`` SensorGrid identifiers.
        bounds_xy: Tuple ``(xmin, ymin, xmax, ymax)`` in meters.
        grid_res_m: Grid point spacing in meters.
        esc_height_m: Elevation for semi-cylindrical facial recognition sensors (1.5 m).
        observer_direction: Horizontal pedestrian travel axis normal.

    Returns:
        Tuple ``(eh_grid, esc_grid)`` of ``SensorGrid`` instances.
    """
    xmin, ymin, xmax, ymax = bounds_xy
    step = max(0.5, float(grid_res_m))
    xs = np.arange(xmin, xmax + 1e-6, step)
    ys = np.arange(ymin, ymax + 1e-6, step)

    ground_pts = [(float(x), float(y), 0.0) for y in ys for x in xs]
    eh_grid = SensorGrid.from_planar_positions(
        '{}_eh'.format(identifier_prefix), ground_pts, (0.0, 0.0, 1.0)
    )
    eh_grid.display_name = 'EN 13201 Horizontal Illuminance Eh Grid'

    esc_grid = build_facial_recognition_sensor_grid(
        '{}_esc'.format(identifier_prefix),
        xs,
        ys,
        z_height_m=esc_height_m,
        observer_direction=observer_direction,
    )
    return eh_grid, esc_grid


def compute_lux_sensory_multiplier(
    eh_lux,
    ti_pct,
    e50_lux=12.0,
    emin_lux=0.5,
    alpha_glare=0.65,
):
    """Compute visual sensory noise multiplier under scotopic/mesopic lux & disability glare.

    .. math::

        \\psi_{\\text{lux}}(E_h, TI) =
        \\left(1 + \\frac{E_{50}}{E_h + E_{\\min}}\\right)
        \\left(1 + \\alpha_{\\text{glare}} \\frac{TI}{15}\\right)

    Args:
        eh_lux: Horizontal ground illuminance in lux.
        ti_pct: Disability glare Threshold Increment TI in percent (%).
        e50_lux: Half-saturation mesopic illuminance anchor (default 12.0 lux).
        emin_lux: Dark-floor illuminance regularizer (default 0.5 lux).
        alpha_glare: Holladay veiling-glare sensitivity coefficient (default 0.65).

    Returns:
        Dimensionless variance multiplier >= 1.0.
    """
    dark_term = 1.0 + float(e50_lux) / (max(0.0, float(eh_lux)) + float(emin_lux))
    glare_term = 1.0 + float(alpha_glare) * (max(0.0, float(ti_pct)) / 15.0)
    return float(dark_term * glare_term)


def compute_night_perceived_safety_impedance(
    walk_time_s,
    esc_lux,
    isolation_t,
    beta_dark=0.45,
    beta_iso=0.25,
    e_ref_lux=5.0,
):
    """Compute night-time perceived-safety pedestrian route impedance .

    Penalizes street links whose semi-cylindrical illuminance ``E_sc`` at ``z = 1.5 m``
    falls below the EN 13201 facial-recognition threshold ``E_ref = 5.0 lux``, modulated
    by real-time pedestrian isolation ``isolation_t``.

    Args:
        walk_time_s: Unimpeded link walking time in seconds.
        esc_lux: Semi-cylindrical illuminance at 1.5 m height in lux.
        isolation_t: Social isolation index in ``[0, 1]`` (0 = lively street, 1 = deserted).
        beta_dark: Perceived-risk weight per lux deficit below ``e_ref_lux`` (default 0.45).
        beta_iso: Perceived-risk weight for social isolation (default 0.25).
        e_ref_lux: EN 13201 P1 facial-recognition reference illuminance (default 5.0 lux).

    Returns:
        Generalized perceived-safety travel impedance in equivalent seconds.
    """
    penalty = (
        1.0
        + float(beta_dark) * max(0.0, float(e_ref_lux) - float(esc_lux))
        + float(beta_iso) * max(0.0, float(isolation_t))
    )
    return float(walk_time_s) * penalty


class En13201RoadLightingSolver(object):
    """Point-by-point EN 13201 raster solver coupled with Honeybee ``SensorGrid`` geometry.

    Computes 2D rasters of horizontal illuminance ``E_h(x, y)``, semi-cylindrical
    illuminance ``E_sc(x, y)`` at ``z = 1.5 m``, longitudinal uniformity ``U_l``,
    overall uniformity ``U_o``, and disability glare ``TI(x, y)`` (%).
    """

    def __init__(
        self,
        preset_name='NIGHT_EN13201_M3',
        bounds_xy=(-60.0, -40.0, 60.0, 40.0),
        grid_res_m=1.0,
        pole_rows_y=(-7.0, 7.0),
    ):
        if preset_name not in LIGHTING_PRESETS:
            raise ValueError(
                'Unknown EN 13201 preset "{}". Choose from: {}'.format(
                    preset_name, sorted(LIGHTING_PRESETS.keys())
                )
            )
        self.preset = LIGHTING_PRESETS[preset_name]
        self.bounds_xy = bounds_xy
        self.grid_res_m = max(0.5, float(grid_res_m))
        self.pole_rows_y = tuple(float(y) for y in pole_rows_y)

        xmin, ymin, xmax, ymax = bounds_xy
        self.xs = np.arange(xmin, xmax + 1e-6, self.grid_res_m)
        self.ys = np.arange(ymin, ymax + 1e-6, self.grid_res_m)
        self.eh_grid, self.esc_grid, self.ti_grid = self._solve_rasters()

    def build_sensor_grid_esc(self, sample_stride=4, observer_direction=(0.0, 1.0, 0.0)):
        """Return a ``SensorGrid`` at ``z = 1.5 m`` covering the solved raster domain."""
        stride = max(1, int(sample_stride))
        ident = 'en13201_{}_esc'.format(self.preset.preset_name.lower())
        return build_facial_recognition_sensor_grid(
            ident,
            self.xs[::stride],
            self.ys[::stride],
            z_height_m=ESC_FACIAL_HEIGHT_M,
            observer_direction=observer_direction,
        )

    def _solve_rasters(self):
        xx, yy = np.meshgrid(self.xs, self.ys)
        eh = np.full_like(xx, self.preset.ambient_eh_lux, dtype=float)
        esc = np.full_like(xx, self.preset.ambient_esc_lux, dtype=float)
        ti = np.full_like(xx, self.preset.glare_ti_pct, dtype=float)

        if self.preset.luminous_flux_lm <= 0.0:
            return eh, esc, ti

        xmin, _, xmax, _ = self.bounds_xy
        pole_xs = np.arange(xmin + 4.0, xmax, self.preset.pole_spacing_m)
        h_m = self.preset.mounting_height_m
        i0_cd = self.preset.luminous_flux_lm / (2.8 * math.pi)

        for px in pole_xs:
            for py in self.pole_rows_y:
                dx = xx - px
                dy = yy - py
                r2_ground = dx * dx + dy * dy + h_m * h_m
                r_ground = np.sqrt(r2_ground)
                cos_theta = h_m / r_ground
                eh += i0_cd * (cos_theta ** 3) / (h_m * h_m)

                hz = max(0.75, h_m - ESC_FACIAL_HEIGHT_M)
                d2_sc = dx * dx + dy * dy + hz * hz
                horiz_r = np.sqrt(dx * dx + dy * dy) + 1e-6
                sin_zenith = horiz_r / np.sqrt(d2_sc)
                esc += (i0_cd / d2_sc) * (1.0 / math.pi) * sin_zenith * 1.15

                glare_hotspot = np.exp(
                    -((dx * dx + dy * dy) / (2.0 * (0.45 * self.preset.pole_spacing_m) ** 2))
                )
                ti += 0.25 * self.preset.glare_ti_pct * glare_hotspot

        return eh, esc, ti

    @property
    def longitudinal_uniformity_ul(self):
        """EN 13201 longitudinal uniformity ``U_l = min(E_h) / mean(E_h)`` along centerline."""
        mid_row = len(self.ys) // 2
        profile = self.eh_grid[mid_row, :]
        return float(np.min(profile) / max(float(np.mean(profile)), 1e-6))

    @property
    def overall_uniformity_uo(self):
        """Overall horizontal illuminance uniformity ``U_o = min(E_h) / mean(E_h)``."""
        return float(np.min(self.eh_grid) / max(float(np.mean(self.eh_grid)), 1e-6))

    def query_at(self, x_m, y_m):
        """Sample ``(eh_lux, esc_lux, ti_pct, psi_lux)`` at world coordinates ``(x_m, y_m)``."""
        ix = int(np.clip(round((x_m - self.xs[0]) / self.grid_res_m), 0, len(self.xs) - 1))
        iy = int(np.clip(round((y_m - self.ys[0]) / self.grid_res_m), 0, len(self.ys) - 1))
        eh_val = float(self.eh_grid[iy, ix])
        esc_val = float(self.esc_grid[iy, ix])
        ti_val = float(self.ti_grid[iy, ix])
        return {
            'eh_lux': eh_val,
            'esc_lux': esc_val,
            'ti_pct': ti_val,
            'psi_lux': compute_lux_sensory_multiplier(eh_val, ti_val),
        }

    def evaluate_p_class_compliance(self, p_class='P2'):
        """Check corridor centerline compliance against EN 13201-2 P-class thresholds."""
        if p_class not in EN13201_P_CLASS_REQUIREMENTS:
            raise ValueError('Unknown EN 13201 P-class "{}"'.format(p_class))
        req = EN13201_P_CLASS_REQUIREMENTS[p_class]
        mid_row = len(self.ys) // 2
        eh_prof = self.eh_grid[mid_row, :]
        esc_prof = self.esc_grid[mid_row, :]
        ti_prof = self.ti_grid[mid_row, :]

        eh_mean = float(np.mean(eh_prof))
        eh_min = float(np.min(eh_prof))
        esc_min = float(np.min(esc_prof))
        ti_max = float(np.max(ti_prof))
        compliant = (
            eh_mean >= req['eh_mean_lux']
            and eh_min >= req['eh_min_lux']
            and esc_min >= req['esc_min_lux']
            and ti_max <= req['ti_max_pct']
        )
        return {
            'p_class': p_class,
            'compliant': bool(compliant),
            'eh_mean_lux': eh_mean,
            'eh_min_lux': eh_min,
            'esc_min_lux': esc_min,
            'ti_max_pct': ti_max,
            'ul': self.longitudinal_uniformity_ul,
        }

    def export_npz(self, path):
        """Export solved ``E_h``, ``E_sc``, and ``TI`` grids as a compressed NumPy archive."""
        out = Path(path)
        out.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(
            out,
            xs=self.xs,
            ys=self.ys,
            eh_lux=self.eh_grid,
            esc_lux=self.esc_grid,
            ti_pct=self.ti_grid,
        )
        return out
