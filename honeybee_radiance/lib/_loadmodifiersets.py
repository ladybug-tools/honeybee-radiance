"""Load all modifier sets from the JSON libraries."""
from honeybee_radiance.config import folders
from honeybee_radiance.modifierset import ModifierSet

from ._loadmodifiers import _rad_modifiers

import os
import json


# empty dictionary to hold loaded modifier sets
_json_modifier_sets = {}


# first load the honeybee defaults
with open(folders.defaults_file) as json_file:
    default_data = json.load(json_file)['modifier_sets']
for mset_dict in default_data:
    modifierset = ModifierSet.from_dict_abridged(mset_dict, _rad_modifiers)
    modifierset.lock()
    _json_modifier_sets[mset_dict['identifier']] = modifierset


# then load modifier sets from the user-supplied files
def load_modifier_set_object(mset_dict):
    """Load a modifier set object from a dictionary and add it to the lib dict."""
    try:
        if mset_dict['type'] == 'ModifierSetAbridged':
            modifierset = ModifierSet.from_dict_abridged(mset_dict, _rad_modifiers)
        else:
            modifierset = ModifierSet.from_dict(mset_dict)
        modifierset.lock()
        _json_modifier_sets[mset_dict['identifier']] = modifierset
    except (TypeError, KeyError, ValueError):
        pass  # not a Honeybee ModifierSet JSON; possibly a comment


for f in os.listdir(folders.modifierset_lib):
    f_path = os.path.join(folders.modifierset_lib, f)
    if os.path.isfile(f_path) and f_path.endswith('.json'):
        with open(f_path, 'r') as json_file:
            mod_set_dict = json.load(json_file)
        if 'type' in mod_set_dict:  # single object
            load_modifier_set_object(mod_set_dict)
        else:  # a collection of several objects
            for mod_set_id in mod_set_dict:
                load_modifier_set_object(mod_set_dict[mod_set_id])
