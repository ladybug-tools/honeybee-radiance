"""Collection of modifier sets."""
from ..modifierset import ModifierSet
import honeybee_radiance.lib.modifiers as modifiers

# create the generic interior visible set
generic_modifier_set_visible = ModifierSet('Generic_Interior_Visible_Modifier_Set')
generic_modifier_set_visible.lock()

# create the generic interior solar set
generic_modifier_set_solar = ModifierSet('Generic_Interior_Solar_Modifier_Set')
generic_modifier_set_solar.aperture_set.window_modifier = \
    modifiers.generic_exterior_window_solar
generic_modifier_set_solar.aperture_set.skylight_modifier = \
    modifiers.generic_exterior_window_solar
generic_modifier_set_solar.aperture_set.operable_modifier = \
    modifiers.generic_exterior_window_solar
generic_modifier_set_solar.aperture_set.interior_modifier = \
    modifiers.generic_interior_window_solar
generic_modifier_set_solar.lock()

# create the generic exterior visible set
generic_modifier_set_visible_exterior = \
    ModifierSet('Generic_Exterior_Visible_Modifier_Set')
generic_modifier_set_visible_exterior.wall_set.exterior_modifier = \
    modifiers.generic_wall_exterior
generic_modifier_set_visible_exterior.floor_set.exterior_modifier = \
    modifiers.generic_floor_exterior
generic_modifier_set_visible_exterior.roof_ceiling_set.exterior_modifier = \
    modifiers.generic_roof_exterior
generic_modifier_set_visible_exterior.lock()

# create the generic exterior solar set
generic_modifier_set_solar_exterior = \
    ModifierSet('Generic_Exterior_Solar_Modifier_Set')
generic_modifier_set_solar_exterior.wall_set.exterior_modifier = \
    modifiers.generic_wall_exterior
generic_modifier_set_solar_exterior.floor_set.exterior_modifier = \
    modifiers.generic_floor_exterior
generic_modifier_set_solar_exterior.roof_ceiling_set.exterior_modifier = \
    modifiers.generic_roof_exterior
generic_modifier_set_solar_exterior.aperture_set.window_modifier = \
    modifiers.generic_exterior_window_solar
generic_modifier_set_solar_exterior.aperture_set.skylight_modifier = \
    modifiers.generic_exterior_window_solar
generic_modifier_set_solar_exterior.aperture_set.operable_modifier = \
    modifiers.generic_exterior_window_solar
generic_modifier_set_solar_exterior.aperture_set.interior_modifier = \
    modifiers.generic_interior_window_solar
generic_modifier_set_solar_exterior.lock()
