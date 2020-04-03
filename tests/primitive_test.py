"""test primitive class."""
from honeybee_radiance.primitive import Primitive
from honeybee_radiance.putil import primitive_class_from_type_string, dict_to_primitive
from honeybee_radiance.reader import parse_from_file, string_to_dicts
from honeybee_radiance.geometry import Polygon, Sphere
from honeybee_radiance.modifier.material import Plastic, Glass
from .rad_string_collection import frit

import pytest


def test_illegal_identifier():
    with pytest.raises(Exception):
        p = Primitive('$$%name  of material')


def test_from_string():
    """from_string uses from_dict under the hood."""
    p = Primitive.from_string(frit)
    assert p.identifier == 'glass_mat'
    assert len(p.values[0]) == 1
    assert p.values[0][0] == 'glass_alt_mat'
    assert p.values[1] == []
    assert p.values[2] == ['1', '1', '1']
    assert len(p.dependencies) == 1
    # check modifier
    assert p.modifier.identifier == 'glass_angular_effect'
    assert p.modifier.type == 'brightfunc'


def test_to_radiance():
    p = Primitive.from_string(frit)
    assert ' '.join(p.to_radiance().split()) == ' '.join(frit.split())


def test_primitive_class_from_type_string():
    assert primitive_class_from_type_string('polygon') == Polygon
    assert primitive_class_from_type_string('sphere') == Sphere
    assert primitive_class_from_type_string('plastic') == Plastic
    assert primitive_class_from_type_string('glass') == Glass


def test_dict_to_primitive():
    f_path = './tests/assets/model/test_model.rad'
    with open(f_path) as f:
        rad_dicts = string_to_dicts(f.read())
        for rad_dict in rad_dicts:
            prim_obj = dict_to_primitive(rad_dict)
            assert isinstance(prim_obj, Primitive)
            assert prim_obj.__class__ != Primitive  # ensure it's inherited type
