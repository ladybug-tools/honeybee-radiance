"""Load all modifiers from the IDF libraries."""
from honeybee_radiance.config import folders
from honeybee_radiance.reader import string_to_dicts
from honeybee_radiance.mutil import dict_to_modifier, modifier_class_from_type_string

import os
import json


# empty dictionaries to hold rad-loaded modifiers
_rad_modifiers = {}


# load modifiers from the default and user-supplied files
for f in os.listdir(folders.modifier_lib):
    f_path = os.path.join(folders.modifier_lib, f)
    if os.path.isfile(f_path):
        if f_path.endswith('.mat') or f_path.endswith('.rad'):
            with open(f_path) as f:
                try:
                    rad_dicts = string_to_dicts(f.read())
                    for mod_dict in rad_dicts:
                        mod = dict_to_modifier(mod_dict)
                        mod.lock()
                        _rad_modifiers[mod.identifier] = mod
                except ValueError:
                    pass  # empty rad file with no modifiers in them
        if f_path.endswith('.json'):
            with open(f_path) as json_file:
                data = json.load(json_file)
            for mod_identifier in data:
                try:
                    mod_dict = data[mod_identifier]
                    m_class = modifier_class_from_type_string(mod_dict['type'].lower())
                    mod = m_class.from_dict(mod_dict)
                    mod.lock()
                    _rad_modifiers[mod_identifier] = mod
                except Exception:
                    raise ValueError(
                        'Honeybee JSON file {} is not formatted correctly for inclusion '
                        'in the honeybee_radiance modifier library.\nJSONs must be '
                        'formatted with modifier identifiers as keys and modifier '
                        'dictionaries as values'.format(f_path))
