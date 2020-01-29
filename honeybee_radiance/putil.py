"""Primitive utility functions."""
import honeybee_radiance.modifier.material as material
import honeybee_radiance.modifier.mixture as mixture
import honeybee_radiance.modifier.pattern as pattern
import honeybee_radiance.modifier.texture as texture
import honeybee_radiance.geometry as geometry
from honeybee_radiance.primitive import Primitive


def primitive_class_from_type_string(type_string):
    """Get the class of a primitive using its 'type' string.

    Note that this function returns the class itself and not a class instance.

    Args:
        type_string: Text for the name of a primitive module/class. This should
            usually be lowercase and should be the same as the 'type' key used
            in the dictionary representation of the primitve.
    """
    _mapper = {'bsdf': 'BSDF', 'brtdfunc': 'BRTDfunc'}
    if type_string in Primitive.GEOMETRYTYPES:
        target_module = geometry
    elif type_string in Primitive.MATERIALTYPES:
        target_module = material
    elif type_string in Primitive.MIXTURETYPES:
        target_module = mixture
    elif type_string in Primitive.PATTERNTYPES:
        target_module = pattern
    elif type_string in Primitive.TEXTURETYPES:
        target_module = texture
    else:
        raise NotImplementedError('Honeybee currently does not support %s' % type_string)

    class_name = type_string.capitalize() if type_string not in _mapper \
        else _mapper[type_string]
    
    return getattr(target_module, class_name)


def dict_to_primitive(pdict):
    """Convert a dictionary representation of any primitive to a class instance.

    The returned object will have the correct class type and will not be the
    generic Primitive base class. Note that this function is recursive and will
    re-serialize modifiers of modifiers.
    
    Args:
        pdict: A dictionary of any Radiance Primitive (Geometry or Modifier).
    """
    primitive_class = primitive_class_from_type_string(pdict['type'])

    if 'values' in pdict:
        return primitive_class.from_primitive_dict(pdict)
    else:
        return primitive_class.from_dict(pdict)

