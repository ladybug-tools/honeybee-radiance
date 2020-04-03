"""Collection of modifier sets."""
from ..modifierset import ModifierSet
from ._loadmodifiersets import _json_modifier_sets
import honeybee_radiance.lib.modifiers as modifiers


# establish variables for the default modifier sets used across the library
# and auto-generate modifier sets if they were not loaded from default.idf

try:  # create the generic interior visible set
    generic_modifier_set_visible = \
        _json_modifier_sets['Generic_Interior_Visible_Modifier_Set']
except KeyError:
    generic_modifier_set_visible = ModifierSet('Generic_Interior_Visible_Modifier_Set')
    generic_modifier_set_visible.lock()
    _json_modifier_sets['Generic_Interior_Visible_Modifier_Set'] = \
        generic_modifier_set_visible


try:  # create the generic interior solar set
    generic_modifier_set_solar = \
        _json_modifier_sets['Generic_Interior_Solar_Modifier_Set']
except KeyError:
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
    _json_modifier_sets['Generic_Interior_Solar_Modifier_Set'] = \
        generic_modifier_set_solar


try:  # create the generic exterior visible set
    generic_modifier_set_visible_exterior = \
        _json_modifier_sets['Generic_Exterior_Visible_Modifier_Set']
except KeyError:
    generic_modifier_set_visible_exterior = \
        ModifierSet('Generic_Exterior_Visible_Modifier_Set')
    generic_modifier_set_visible_exterior.wall_set.exterior_modifier = \
        modifiers.generic_wall_exterior
    generic_modifier_set_visible_exterior.floor_set.exterior_modifier = \
        modifiers.generic_floor_exterior
    generic_modifier_set_visible_exterior.roof_ceiling_set.exterior_modifier = \
        modifiers.generic_roof_exterior
    generic_modifier_set_visible_exterior.lock()
    _json_modifier_sets['Generic_Exterior_Visible_Modifier_Set'] = \
        generic_modifier_set_visible_exterior


try:  # create the generic exterior solar set
    generic_modifier_set_solar_exterior = \
        _json_modifier_sets['Generic_Exterior_Solar_Modifier_Set']
except KeyError:
    generic_modifier_set_solar_exterior = generic_modifier_set_solar.duplicate()
    generic_modifier_set_solar_exterior.identifier = \
        'Generic_Exterior_Solar_Modifier_Set'
    generic_modifier_set_solar_exterior.wall_set.exterior_modifier = \
        modifiers.generic_wall_exterior
    generic_modifier_set_solar_exterior.floor_set.exterior_modifier = \
        modifiers.generic_floor_exterior
    generic_modifier_set_solar_exterior.roof_ceiling_set.exterior_modifier = \
        modifiers.generic_roof_exterior
    generic_modifier_set_solar_exterior.lock()
    _json_modifier_sets['Generic_Exterior_Solar_Modifier_Set'] = \
        generic_modifier_set_solar_exterior


# make lists of modifier sets to look up items in the library
MODIFIER_SETS = tuple(_json_modifier_sets.keys())


def modifier_set_by_identifier(modifier_set_identifier):
    """Get a modifier_set from the library given its identifier.

    Args:
        modifier_set_identifier: A text string for the identifier of the ConstructionSet.
    """
    try:
        return _json_modifier_sets[modifier_set_identifier]
    except KeyError:
        raise ValueError('"{}" was not found in the modifier set library.'.format(
            modifier_set_identifier))
