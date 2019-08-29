"""Collection of modifier sets."""
from ..modifierset import ModifierSet
import honeybee_radiance.lib.modifiers as modifiers

generic_modifier_set_visible = ModifierSet('Default Generic Visible Modifier Set')
generic_modifier_set_visible.lock()

generic_modifier_set_solar = ModifierSet('Default Generic Solar Modifier Set')

# update glass modifiers
generic_modifier_set_solar.aperture_set.window_modifier = \
    modifiers.generic_exterior_glass_solar
generic_modifier_set_solar.aperture_set.skylight_modifier = \
    modifiers.generic_exterior_glass_solar
generic_modifier_set_solar.aperture_set.operable_modifier = \
    modifiers.generic_exterior_glass_solar
generic_modifier_set_solar.aperture_set.interior_modifier = \
    modifiers.generic_interior_glass_solar

generic_modifier_set_solar.lock()
