"""Library of default modifiers for honeybee-radiance.

Default values are generic values to set the initial visible / solar reflectance and
transmittance values in your model. There is no guarantee that these values exactly
match what you are trying to model.
"""
from ..modifier.material import Plastic, Glass, Glow
from ._loadmodifiers import _rad_modifiers


# establish variables for the default modifiers used across the library
# and auto-generate modifiers if they were not loaded from default.mat

# generic opaque modifiers - visible and solar
try:
    generic_floor = _rad_modifiers['generic_floor_0.20']
except KeyError:
    generic_floor = Plastic.from_single_reflectance('generic_floor_0.20', 0.2)
    generic_floor.lock()
    _rad_modifiers['generic_floor_0.20'] = generic_floor

try:
    generic_wall = _rad_modifiers['generic_wall_0.50']
except KeyError:
    generic_wall = Plastic.from_single_reflectance('generic_wall_0.50', 0.5)
    generic_wall.lock()
    _rad_modifiers['generic_wall_0.50'] = generic_wall

try:
    generic_ceiling = _rad_modifiers['generic_ceiling_0.80']
except KeyError:
    generic_ceiling = Plastic.from_single_reflectance('generic_ceiling_0.80', 0.8)
    generic_ceiling.lock()
    _rad_modifiers['generic_ceiling_0.80'] = generic_ceiling

try:
    generic_door = _rad_modifiers['generic_opaque_door_0.50']
except KeyError:
    generic_door = Plastic.from_single_reflectance('generic_opaque_door_0.50', 0.5)
    generic_door.lock()
    _rad_modifiers['generic_opaque_door_0.50'] = generic_door


# generic shade modifiers - visible and solar
try:
    generic_interior_shade = _rad_modifiers['generic_interior_shade_0.50']
except KeyError:
    generic_interior_shade = Plastic.from_single_reflectance(
        'generic_interior_shade_0.50', 0.50)
    generic_interior_shade.lock()
    _rad_modifiers['generic_interior_shade_0.50'] = generic_interior_shade

try:
    generic_exterior_shade = _rad_modifiers['generic_exterior_shade_0.35']
except KeyError:
    generic_exterior_shade = Plastic.from_single_reflectance(
        'generic_exterior_shade_0.35', 0.35)
    generic_exterior_shade.lock()
    _rad_modifiers['generic_exterior_shade_0.35'] = generic_exterior_shade

try:
    generic_context = _rad_modifiers['generic_context_0.20']
except KeyError:
    generic_context = Plastic.from_single_reflectance('generic_context_0.20', 0.2)
    generic_context.lock()
    _rad_modifiers['generic_context_0.20'] = generic_context


# generic glass modifiers - visible
try:
    generic_interior_window = _rad_modifiers['generic_interior_window_vis_0.88']
except KeyError:
    generic_interior_window = Glass.from_single_transmittance(
        'generic_interior_window_vis_0.88', 0.88)
    generic_interior_window.lock()
    _rad_modifiers['generic_interior_window_vis_0.88'] = generic_interior_window

try:
    generic_exterior_window = _rad_modifiers['generic_exterior_window_vis_0.64']
except KeyError:
    generic_exterior_window = Glass.from_single_transmittance(
        'generic_exterior_window_vis_0.64', 0.64)
    generic_exterior_window.lock()
    _rad_modifiers['generic_exterior_window_vis_0.64'] = generic_exterior_window

try:
    generic_exterior_window_insect_screen = \
        _rad_modifiers['generic_exterior_screened_window_vis_0.32']
except KeyError:
    generic_exterior_window_insect_screen = \
        Glass.from_single_transmittance(
            'generic_exterior_screened_window_vis_0.32', 0.32)
    generic_exterior_window_insect_screen.lock()
    _rad_modifiers['generic_exterior_screened_window_vis_0.32'] = \
        generic_exterior_window_insect_screen


# generic glass modifiers - solar
try:
    generic_interior_window_solar = _rad_modifiers['generic_interior_window_sol_0.77']
except KeyError:
    generic_interior_window_solar = Glass.from_single_transmittance(
        'generic_interior_window_sol_0.77', 0.77)
    generic_interior_window_solar.lock()
    _rad_modifiers['generic_interior_window_sol_0.77'] = generic_interior_window_solar

try:
    generic_exterior_window_solar = _rad_modifiers['generic_exterior_window_sol_0.37']
except KeyError:
    generic_exterior_window_solar = Glass.from_single_transmittance(
        'generic_exterior_window_sol_0.37', 0.37)
    generic_exterior_window_solar.lock()
    _rad_modifiers['generic_exterior_window_sol_0.37'] = generic_exterior_window_solar

try:
    generic_exterior_window_insect_screen_solar = \
        _rad_modifiers['generic_exterior_screened_window_sol_0.19']
except KeyError:
    generic_exterior_window_insect_screen_solar = \
        Glass.from_single_transmittance(
            'generic_exterior_screened_window_sol_0.19', 0.19)
    generic_exterior_window_insect_screen_solar.lock()
    _rad_modifiers['generic_exterior_screened_window_sol_0.19'] = \
        generic_exterior_window_insect_screen_solar


# generic exterior side opaque modifiers - visible and solar
try:
    generic_floor_exterior = _rad_modifiers['generic_floor_exterior_side_0.50']
except KeyError:
    generic_floor_exterior = Plastic.from_single_reflectance(
        'generic_floor_exterior_side_0.50', 0.5)
    generic_floor_exterior.lock()
    _rad_modifiers['generic_floor_exterior_side_0.50'] = generic_floor_exterior

try:
    generic_wall_exterior = _rad_modifiers['generic_wall_exterior_side_0.35']
except KeyError:
    generic_wall_exterior = Plastic.from_single_reflectance(
        'generic_wall_exterior_side_0.35', 0.35)
    generic_wall_exterior.lock()
    _rad_modifiers['generic_wall_exterior_side_0.35'] = generic_wall_exterior

try:
    generic_roof_exterior = _rad_modifiers['generic_ceiling_exterior_side_0.35']
except KeyError:
    generic_roof_exterior = Plastic.from_single_reflectance(
        'generic_ceiling_exterior_side_0.35', 0.35)
    generic_roof_exterior.lock()
    _rad_modifiers['generic_ceiling_exterior_side_0.35'] = generic_roof_exterior


# special types of modifiers used within various simulation processes
try:
    air_boundary = _rad_modifiers['air_boundary']
except KeyError:
    air_boundary = Glass.from_single_transmissivity('air_boundary', 1.0)
    air_boundary.lock()
    _rad_modifiers['air_boundary'] = air_boundary

try:  # used in multiphase daylight
    black = _rad_modifiers['black']
except KeyError:
    black = Plastic.from_single_reflectance('black', 0.0)
    black.lock()
    _rad_modifiers['black'] = black

try:  # used in multiphase daylight
    white_glow = _rad_modifiers['white_glow']
except KeyError:
    white_glow = Glow('white_glow', 1.0, 1.0, 1.0, 0.0)
    white_glow.lock()
    _rad_modifiers['white_glow'] = white_glow


# make lists of modifier identifiers to look up items in the library
MODIFIERS = tuple(_rad_modifiers.keys())


def modifier_by_identifier(modifier_identifier):
    """Get a modifier from the library given the modifier identifier.

    Args:
        modifier_identifier: A text string for the identifier of the modifier.
    """
    try:
        return _rad_modifiers[modifier_identifier]
    except KeyError:
        raise ValueError(
            '"{}" was not found in the radiancemodifier library.'.format(
                modifier_identifier))
