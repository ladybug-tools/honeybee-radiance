"""Library of default modifiers for honeybee-radiance.

Default values are generic values to set the initial visible / solar reflectance and
transmittance values in your model. There is no guarantee that these values exactly
match what you are trying to model.
"""

from honeybee_radiance.modifier.material import Plastic, Glass, Glow

# generic opaque modifiers - visible and solar
generic_floor = Plastic.from_single_reflectance('generic_floor_0.20', 0.2)
generic_wall = Plastic.from_single_reflectance('generic_wall_0.50', 0.5)
generic_ceiling = Plastic.from_single_reflectance('generic_ceiling_0.80', 0.8)
generic_door = Plastic.from_single_reflectance('generic_opaque_door_0.50', 0.5)

# generic shade modifiers - visible and solar
generic_interior_shade = \
    Plastic.from_single_reflectance('generic_interior_shade_0.50', 0.50)
generic_exterior_shade = \
    Plastic.from_single_reflectance('generic_exterior_shade_0.35', 0.35)
generic_context = Plastic.from_single_reflectance('generic_context_0.20', 0.2)

# generic glass modifiers - visible
generic_interior_window = \
    Glass.from_single_transmittance('generic_interior_window_vis_0.88', 0.88)
generic_exterior_window = \
    Glass.from_single_transmittance('generic_exterior_window_vis_0.64', 0.64)
generic_exterior_window_insect_screen = \
    Glass.from_single_transmittance('generic_exterior_screened_window_vis_0.32', 0.32)

# generic glass modifiers - solar
generic_interior_window_solar = \
    Glass.from_single_transmittance('generic_interior_window_sol_0.77', 0.77)
generic_exterior_window_solar = \
    Glass.from_single_transmittance('generic_exterior_window_sol_0.37', 0.37)
generic_exterior_window_insect_screen_solar = \
    Glass.from_single_transmittance('generic_exterior_screened_window_sol_0.19', 0.19)

# generic exterior side opaque modifiers - visible and solar
generic_floor_exterior = \
    Plastic.from_single_reflectance('generic_floor_exterior_side_0.50', 0.5)
generic_wall_exterior = \
    Plastic.from_single_reflectance('generic_wall_exterior_side_0.35', 0.35)
generic_roof_exterior = \
    Plastic.from_single_reflectance('generic_ceiling_exterior_side_0.35', 0.35)

# special types of modifiers used within various simulation processes
air_wall = Glass.from_single_transmissivity('air_wall', 1.0)
black = Plastic.from_single_reflectance('black', 0.0)  # used in multiphase daylight
white_glow = Glow('white_glow', 1.0, 1.0, 1.0, 0.0)  # used in multi-phase daylight
