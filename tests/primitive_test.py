"""test primitive class."""
from honeybee_radiance.primitive import Primitive
from .rad_string_collection import frit


def test_illegal_name():
    p = Primitive('$$%name  of material')
    assert p.name == 'nameofmaterial'


def test_from_string():
    """from_string uses from_dict under the hood."""
    p = Primitive.from_string(frit)
    assert p.name == 'glass_mat'
    assert len(p.values[0]) == 1
    assert p.values[0][0] == 'glass_alt_mat'
    assert p.values[1] == []
    assert p.values[2] == ['1', '1', '1']
    assert len(p.dependencies) == 1
    # check modifier
    assert p.modifier.name == 'glass_angular_effect'
    assert p.modifier.type == 'brightfunc'


def test_to_radiance():
    p = Primitive.from_string(frit)
    assert ' '.join(p.to_radiance().split()) == ' '.join(frit.split())
