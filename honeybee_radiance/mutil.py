"""Modifier utility functions."""
import honeybee_radiance.modifier.material as material
import honeybee_radiance.modifier.mixture as mixture
import honeybee_radiance.modifier.pattern as pattern
import honeybee_radiance.modifier.texture as texture
from honeybee_radiance.primitive import Primitive, Void


def modifier_class_from_type_string(type_string):
    """Get the class of any modifier using its 'type' string.

    This function is equivalent to the primitive_class_from_type_string function
    but it is only for modifiers (not geometry) and is slightly faster when one
    is sure that the type_string is a modifier.

    Note that this function returns the class itself and not a class instance.

    Args:
        type_string: Text for the name of a modifier module/class. This should
            be the same as the 'type' key used in the dictionary representation
            of the modifier.
    """
    _mapper = {'bsdf': 'BSDF', 'BSDF': 'BSDF',
               'brtdfunc': 'BRTDfunc', 'BRTDfunc': 'BRTDfunc'}
    lower_str = type_string.lower()
    if lower_str == 'void':
        return Void
    elif lower_str in Primitive.MATERIALTYPES:
        target_module = material
    elif lower_str in Primitive.MIXTURETYPES:
        target_module = mixture
    elif lower_str in Primitive.PATTERNTYPES:
        target_module = pattern
    elif lower_str in Primitive.TEXTURETYPES:
        target_module = texture
    else:
        raise ValueError('%s is not a Radiance modifier.' % type_string)

    class_name = lower_str.capitalize() if lower_str not in _mapper \
        else _mapper[lower_str]

    return getattr(target_module, class_name)


def dict_to_modifier(mdict):
    """Convert a dictionary representation of any modifier to a class instance.

    The returned object will have the correct class type and will not be the
    generic Modifier base class. Note that this function is recursive and will
    re-serialize modifiers of modifiers.

    Args:
        mdict: A dictionary of any Radiance Modifier.
    """
    mod_class = modifier_class_from_type_string(mdict['type'])

    if 'values' in mdict:
        return mod_class.from_primitive_dict(mdict)
    else:
        return mod_class.from_dict(mdict)
