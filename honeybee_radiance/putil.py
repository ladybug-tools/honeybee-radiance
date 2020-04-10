"""Primitive utility functions."""
from honeybee_radiance.mutil import modifier_class_from_type_string
import honeybee_radiance.geometry as geometry
from honeybee_radiance.primitive import Primitive


def primitive_class_from_type_string(type_string):
    """Get the class of any primitive using its 'type' string.

    Note that this function returns the class itself and not a class instance.

    Args:
        type_string: Text for the name of a primitive module/class. This should
            usually be lowercase and should be the same as the 'type' key used
            in the dictionary representation of the primitive.
    """
    if type_string in Primitive.GEOMETRYTYPES:
        target_module = geometry
    else:
        try:
            return modifier_class_from_type_string(type_string)
        except ValueError:
            raise NotImplementedError(
                'Honeybee currently does not support %s' % type_string)
    class_name = type_string.capitalize()
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
