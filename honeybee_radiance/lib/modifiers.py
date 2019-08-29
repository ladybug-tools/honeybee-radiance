"""Library of default modifiers for honeybee-radiance.

Default values are generic values to set the initial visible / solar reflectance and
transmittance values in your model. There is no guarantee that these values exactly
match what you are trying to model.
"""

from honeybee_radiance.primitive.material import Plastic, Glass

# interior modifiers - visible
generic_floor = Plastic.from_single_reflectance('generic_floor_0.20', 0.2)
generic_interior_wall = Plastic.from_single_reflectance('generic_int_wall_0.50', 0.5)
generic_ceiling = Plastic.from_single_reflectance('generic_ceiling_0.80', 0.8)
generic_opaque_door = Plastic.from_single_reflectance('generic_opaque_door_0.50', 0.5)
generic_context = Plastic.from_single_reflectance('generic_context_0.20', 0.2)
generic_interior_glass = Glass.from_single_transmittance('generic_int_glass_0.88', 0.88)
generic_interior_glass_door = generic_interior_glass
generic_interior_shade = \
    Plastic.from_single_reflectance('generic_interior_shade_0.50', 0.50)

# interior modifiers - solar
generic_interior_glass_solar = \
    Glass.from_single_transmittance('generic_int_glass_sol_0.77', 0.77)

# exterior modifiers - visible
generic_exposed_floor = \
    Plastic.from_single_reflectance('generic_exposed_floor_0.50', 0.5)
generic_exterior_wall = Plastic.from_single_reflectance('generic_ext_wall_0.35', 0.35)
generic_roof = Plastic.from_single_reflectance('generic_roof_0.35', 0.35)
generic_exterior_glass = Glass.from_single_transmittance('generic_ext_glass_0.64', 0.64)
generic_exterior_glass_door = generic_exterior_glass
generic_exterior_shade = \
    Plastic.from_single_reflectance('generic_exterior_shade_0.35', 0.35)

# exterior modifiers - solar
generic_exterior_glass_solar = \
    Glass.from_single_transmittance('generic_ext_glass_sol_0.37', 0.37)

air_wall = Glass.from_single_transmissivity('air_wall', 1.0)
