"""Load all modifier sets from the JSON libraries."""
from honeybee_radiance.config import folders
from honeybee_radiance.modifierset import ModifierSet

from ._loadmodifiers import _rad_modifiers

import os
import json


# empty dictionaries to hold json-loaded modifier sets
_json_modifier_sets = {}


# load modifier sets from the default and user-supplied files
for f in os.listdir(folders.modifierset_lib):
    f_path = os.path.join(folders.modifierset_lib, f)
    if os.path.isfile(f_path) and f_path.endswith('.json'):
        with open(f_path, 'r') as json_file:
            mod_set_dict = json.load(json_file)
        for mod_set_id in mod_set_dict:
            try:
                modifierset = ModifierSet.from_dict_abridged(
                    mod_set_dict[mod_set_id], _rad_modifiers)
                modifierset.lock()
                _json_modifier_sets[mod_set_id] = modifierset
            except Exception:
                raise ValueError(
                        'Honeybee JSON file {} is not formatted correctly for inclusion '
                        'in the honeybee_radiance modifier set library.\nJSONs must be '
                        'formatted with ModifierSet identifiers as keys and abridged '
                        'ModifierSet dictionaries as values'.format(f_path))
