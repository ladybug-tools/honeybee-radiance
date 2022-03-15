"""Load all modifiers from the IDF libraries."""
from honeybee_radiance.config import folders
from honeybee_radiance.reader import string_to_dicts
from honeybee_radiance.mutil import dict_to_modifier, modifier_class_from_type_string

import os
import json


# empty dictionary to hold loaded modifiers
_loaded_modifiers = {}


# first load the honeybee defaults
with open(folders.defaults_file) as json_file:
    default_data = json.load(json_file)['modifiers']
for mod_dict in default_data:
    m_class = modifier_class_from_type_string(mod_dict['type'])
    mod = m_class.from_dict(mod_dict)
    mod.lock()
    _loaded_modifiers[mod_dict['identifier']] = mod
_default_mods = set(list(_loaded_modifiers.keys()))


# then load modifiers from the user-supplied files
def load_modifier_object(mod_dict, user_modifiers):
    """Load a modifier object from a dictionary and add it to the library dict."""
    try:
        m_class = modifier_class_from_type_string(mod_dict['type'])
        mod = m_class.from_dict(mod_dict)
        mod.lock()
        assert mod_dict['identifier'] not in _default_mods, 'Cannot overwrite ' \
            'default modifier "{}".'.format(mod_dict['identifier'])
        user_modifiers[mod_dict['identifier']] = mod
    except (TypeError, KeyError):
        pass  # not a Honeybee Modifier JSON; possibly a comment


def load_modifiers_from_folder(modifier_lib_folder):
    """Load all of the material layer objects from a modifier standards folder.

    Args:
        modifier_lib_folder: Path to a modifiers sub-folder within a
            honeybee standards folder.
    """
    user_modifiers = {}
    for f in os.listdir(modifier_lib_folder):
        f_path = os.path.join(modifier_lib_folder, f)
        if os.path.isfile(f_path):
            if f_path.endswith('.mat') or f_path.endswith('.rad'):
                with open(f_path) as f:
                    try:
                        rad_dicts = string_to_dicts(f.read())
                        for mod_dict in rad_dicts:
                            mod = dict_to_modifier(mod_dict)
                            mod.lock()
                            user_modifiers[mod.identifier] = mod
                    except ValueError:
                        pass  # empty rad file with no modifiers in them
            if f_path.endswith('.json'):
                with open(f_path) as json_file:
                    data = json.load(json_file)
                if 'type' in data:  # single object
                    load_modifier_object(data, user_modifiers)
                else:  # a collection of several objects
                    for mod_identifier in data:
                        load_modifier_object(data[mod_identifier], user_modifiers)
    return user_modifiers


user_mods = load_modifiers_from_folder(folders.modifier_lib)
_loaded_modifiers.update(user_mods)
