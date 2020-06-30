"""Library of default modifiers for honeybee-radiance.

Default values are generic values to set the initial visible / solar reflectance and
transmittance values in your model. There is no guarantee that these values exactly
match what you are trying to model.
"""
from ._loadmodifiers import _loaded_modifiers


# establish variables for the default modifiers used across the library
# generic opaque modifiers - visible and solar
generic_floor = _loaded_modifiers['generic_floor_0.20']
generic_wall = _loaded_modifiers['generic_wall_0.50']
generic_ceiling = _loaded_modifiers['generic_ceiling_0.80']
generic_door = _loaded_modifiers['generic_opaque_door_0.50']

# generic shade modifiers - visible and solar
generic_interior_shade = _loaded_modifiers['generic_interior_shade_0.50']
generic_exterior_shade = _loaded_modifiers['generic_exterior_shade_0.35']
generic_context = _loaded_modifiers['generic_context_0.20']
generic_interior_window = _loaded_modifiers['generic_interior_window_vis_0.88']
generic_exterior_window = _loaded_modifiers['generic_exterior_window_vis_0.64']
generic_exterior_window_insect_screen = \
    _loaded_modifiers['generic_exterior_screened_window_vis_0.32']

# generic glass modifiers - solar
generic_interior_window_solar = _loaded_modifiers['generic_interior_window_sol_0.77']
generic_exterior_window_solar = _loaded_modifiers['generic_exterior_window_sol_0.37']
generic_exterior_window_insect_screen_solar = \
    _loaded_modifiers['generic_exterior_screened_window_sol_0.19']

# generic exterior side opaque modifiers - visible and solar
generic_floor_exterior = _loaded_modifiers['generic_floor_exterior_side_0.50']
generic_wall_exterior = _loaded_modifiers['generic_wall_exterior_side_0.35']
generic_roof_exterior = _loaded_modifiers['generic_ceiling_exterior_side_0.35']

# special types of modifiers used within various simulation processes
air_boundary = _loaded_modifiers['air_boundary']
black = _loaded_modifiers['black']
white_glow = _loaded_modifiers['white_glow']


# make lists of modifier identifiers to look up items in the library
MODIFIERS = tuple(_loaded_modifiers.keys())


def modifier_by_identifier(modifier_identifier):
    """Get a modifier from the library given the modifier identifier.

    Args:
        modifier_identifier: A text string for the identifier of the modifier.
    """
    try:
        return _loaded_modifiers[modifier_identifier]
    except KeyError:
        raise ValueError(
            '"{}" was not found in the radiancemodifier library.'.format(
                modifier_identifier))
