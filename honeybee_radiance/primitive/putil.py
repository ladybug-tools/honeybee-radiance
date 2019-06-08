"""Primitive utility functions."""
import honeybee_radiance.primitive.material as material
import honeybee_radiance.primitive.mixture as mixture
import honeybee_radiance.primitive.pattern as pattern
import honeybee_radiance.primitive.texture as texture
import honeybee_radiance.primitive.geometry as geometry
from honeybee_radiance.primitive.primitivebase import Primitive


def dict_to_primitive(pdict):
    """convert a dictionary to a primitive."""
    _mapper = {'bsdf': 'BSDF', 'brtdfunc': 'BRTDfunc'}
    ptype = pdict['type']
    if ptype in Primitive.GEOMETRYTYPES:
        target_module = geometry
    elif ptype in Primitive.MATERIALTYPES:
        target_module = material
    elif ptype in Primitive.MIXTURETYPES:
        target_module = mixture
    elif ptype in Primitive.PATTERNTYPES:
        target_module = pattern
    elif ptype in Primitive.TEXTURETYPES:
        target_module = texture
    else:
        raise NotImplementedError('Honeybee currently does not support %s' % ptype)

    class_name = ptype.capitalize() if ptype not in _mapper else _mapper[ptype]

    if 'values' in pdict:
        return getattr(target_module, class_name).from_values(pdict)
    else:
        return getattr(target_module, class_name).from_dict(pdict)
