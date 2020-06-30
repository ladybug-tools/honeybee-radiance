"""Collection of modifier sets."""
from ._loadmodifiersets import _loaded_modifier_sets


# establish variables for the default modifier sets used across the library
generic_modifier_set_visible = \
    _loaded_modifier_sets['Generic_Interior_Visible_Modifier_Set']
generic_modifier_set_solar = \
    _loaded_modifier_sets['Generic_Interior_Solar_Modifier_Set']
generic_modifier_set_visible_exterior = \
    _loaded_modifier_sets['Generic_Exterior_Visible_Modifier_Set']
generic_modifier_set_solar_exterior = \
    _loaded_modifier_sets['Generic_Exterior_Solar_Modifier_Set']


# make lists of modifier sets to look up items in the library
MODIFIER_SETS = tuple(_loaded_modifier_sets.keys())


def modifier_set_by_identifier(modifier_set_identifier):
    """Get a modifier_set from the library given its identifier.

    Args:
        modifier_set_identifier: A text string for the identifier of the ConstructionSet.
    """
    try:
        return _loaded_modifier_sets[modifier_set_identifier]
    except KeyError:
        raise ValueError('"{}" was not found in the modifier set library.'.format(
            modifier_set_identifier))
