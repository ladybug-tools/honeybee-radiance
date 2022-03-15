"""Load all modifier sets from the JSON libraries."""
from honeybee_radiance.config import folders
from honeybee_radiance.modifierset import ModifierSet

from ._loadmodifiers import _loaded_modifiers

import os
import json


# empty dictionary to hold loaded modifier sets
_loaded_modifier_sets = {}


# first load the honeybee defaults
with open(folders.defaults_file) as json_file:
    default_data = json.load(json_file)['modifier_sets']
for mset_dict in default_data:
    modifierset = ModifierSet.from_dict_abridged(mset_dict, _loaded_modifiers)
    modifierset.lock()
    _loaded_modifier_sets[mset_dict['identifier']] = modifierset
_default_mod_sets = set(list(_loaded_modifier_sets.keys()))


# then load modifier sets from the user-supplied files
def load_modifier_set_object(mset_dict, load_mods, mod_sets, misc_mods):
    """Load a modifier set object from a dictionary and add it to the lib dict."""
    try:
        if mset_dict['type'] == 'ModifierSetAbridged':
            modifierset = ModifierSet.from_dict_abridged(mset_dict, load_mods)
        else:
            modifierset = ModifierSet.from_dict(mset_dict)
            misc_mods.extend(modifierset.modified_modifiers)
        modifierset.lock()
        assert mset_dict['identifier'] not in _default_mod_sets, 'Cannot overwrite ' \
            'default modifier set "{}".'.format(mset_dict['identifier'])
        mod_sets[mset_dict['identifier']] = modifierset
    except (TypeError, KeyError, ValueError):
        pass  # not a Honeybee ModifierSet JSON; possibly a comment


def load_modifiersets_from_folder(modifierset_lib_folder, loaded_modifiers):
    """Load all of the ModifierSet objects from a modifierset standards folder.

    Args:
        modifierset_lib_folder: Path to a modifiersets sub-folder within a
            honeybee standards folder.
        loaded_modifiers: A dictionary of modifiers that have already
            been loaded from the library.
    """
    mod_sets, misc_mods = {}, []
    for f in os.listdir(modifierset_lib_folder):
        f_path = os.path.join(modifierset_lib_folder, f)
        if os.path.isfile(f_path) and f_path.endswith('.json'):
            with open(f_path, 'r') as json_file:
                mod_set_dict = json.load(json_file)
            if 'type' in mod_set_dict:  # single object
                load_modifier_set_object(
                    mod_set_dict, loaded_modifiers, mod_sets, misc_mods)
            else:  # a collection of several objects
                for mod_set_id in mod_set_dict:
                    load_modifier_set_object(
                        mod_set_dict[mod_set_id], loaded_modifiers, mod_sets, misc_mods)
    return mod_sets, misc_mods


loaded_m_sets, misc_m = \
    load_modifiersets_from_folder(folders.modifierset_lib, _loaded_modifiers)
_loaded_modifier_sets.update(loaded_m_sets)
