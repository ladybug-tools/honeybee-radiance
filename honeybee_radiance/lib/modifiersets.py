"""Collection of modifier sets."""
from honeybee_radiance.modifierset import ModifierSet
from ._loadmodifiersets import _loaded_modifier_sets

import honeybee_radiance.lib.modifiers as _m


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
        modifier_set_identifier: A text string for the identifier of the ModifierSet.
    """
    try:
        return _loaded_modifier_sets[modifier_set_identifier]
    except KeyError:
        raise ValueError('"{}" was not found in the modifier set library.'.format(
            modifier_set_identifier))


def lib_dict_abridged_to_modifier_set(mod_set_dict, modifiers):
    """Get a Python object of a ModifierSet from an abridged dictionary.

    When the sub-objects needed to create the modifier set are not available
    in the resources provided, the current standards library will be searched.

    Args:
        mod_set_dict: An abridged dictionary of a Honeybee ModifierSet.
        modifiers: Dictionary of all modifier objects that might be used in the
            modifier set with the modifier identifiers as the keys.

    Returns:
        A Python object derived from the input mod_set_dict.
    """
    for key in mod_set_dict:
        if isinstance(mod_set_dict[key], dict):
            sub_dict = mod_set_dict[key]
            for sub_key in sub_dict:
                if sub_key == 'type' or sub_key in modifiers:
                    continue
                if sub_dict[sub_key] not in modifiers:
                    modifiers[sub_dict[sub_key]] = \
                        _m.modifier_by_identifier(sub_dict[sub_key])
        elif key == 'air_boundary_modifier' \
                and mod_set_dict[key] not in modifiers:
            modifiers[mod_set_dict[key]] = \
                _m.modifier_by_identifier(mod_set_dict[key])
    return ModifierSet.from_dict_abridged(mod_set_dict, modifiers)
