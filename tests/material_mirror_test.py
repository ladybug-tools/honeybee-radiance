from honeybee_radiance.modifier.material import Mirror
from honeybee_radiance.primitive import VOID

import pytest


def test_mirror():
    mir = Mirror('test_mirror')
    assert mir.r_reflectance == 1
    assert mir.g_reflectance == 1
    assert mir.b_reflectance == 1
    assert mir.to_radiance(minimal=True) == \
        'void mirror test_mirror 0 0 3 1.0 1.0 1.0'


def test_assign_values():
    mir = Mirror('test_mirror', 0.6, 0.7, 0.8)
    assert mir.r_reflectance == 0.6
    assert mir.g_reflectance == 0.7
    assert mir.b_reflectance == 0.8
    assert mir.to_radiance(minimal=True) == \
        'void mirror test_mirror 0 0 3 0.6 0.7 0.8'


def test_material_lockability():
    """Test the lockability of Mirror."""
    mir = Mirror('test_mirror', 0.6, 0.7, 0.8)
    mir.r_reflectance = 0.5
    mir.lock()
    with pytest.raises(AttributeError):
        mir.r_reflectance = 0.7
    mir.unlock()
    mir.r_reflectance = 0.7


def test_material_equivalency():
    """Test the equality of a material to another."""
    mir_1 = Mirror('test_mirror', 0.6, 0.7, 0.8)
    mir_2 = mir_1.duplicate()
    mir_3 = Mirror('test_mirror2', 0.8, 0.7, 0.8)

    assert mir_1 is mir_1
    assert mir_1 is not mir_2
    assert mir_1 == mir_2
    assert isinstance(mir_2, Mirror)
    assert mir_1 != mir_3
    collection = [mir_1, mir_2, mir_3]
    assert len(set(collection)) == 2

    mir_2.r_reflectance = 0.7
    assert mir_1 != mir_2


def test_update_values():
    mir = Mirror('test_mirror', 0.6, 0.7, 0.8)
    mir.r_reflectance = 0.5
    mir.g_reflectance = 0.4
    mir.b_reflectance = 0.3
    assert mir.r_reflectance == 0.5
    assert mir.g_reflectance == 0.4
    assert mir.b_reflectance == 0.3
    assert mir.to_radiance(minimal=True) == \
        'void mirror test_mirror 0 0 3 0.5 0.4 0.3'


def test_from_string():
    mirror_str = """void mirror mirror_alt_mat
        0
        0
        3
            0.91 0.92 0.93
    """
    mir = Mirror.from_string(mirror_str)
    assert mir.identifier == 'mirror_alt_mat'
    assert mir.r_reflectance == 0.91
    assert mir.g_reflectance == 0.92
    assert mir.b_reflectance == 0.93
    assert mir.to_radiance(minimal=True) == ' '.join(mirror_str.split())


def test_from_string_w_modifier():

    material_string = """
    void brightfunc glass_angular_effect
    3 A1+(1-A1) (exp(-5.85 Rdot)-0.00287989916) .
    0
    1 0.08

    glass_angular_effect mirror glass_mat
    0
    0
    3 1 1 1
    """
    gg = Mirror.from_string(material_string)
    assert gg.to_radiance(minimal=True, include_modifier=False) == \
        'glass_angular_effect mirror glass_mat 0 0 3 1.0 1.0 1.0'
    assert gg.modifier.to_radiance(minimal=True) == \
        'void brightfunc glass_angular_effect 3 A1+(1-A1)' \
        ' (exp(-5.85 Rdot)-0.00287989916) . 0 1 0.08'


def test_from_single_value():
    mir = Mirror.from_single_reflectance('mirror_test', 0.95)
    assert mir.r_reflectance == 0.95
    assert mir.g_reflectance == 0.95
    assert mir.b_reflectance == 0.95


def test_with_alternate_material():
    material_string = """
    void glass glass_alt_mat
    0
    0
    3 0.96 0.96 0.96

    void brightfunc glass_angular_effect
    3 A1+(1-A1) (exp(-5.85 Rdot)-0.00287989916) .
    0
    1 0.08

    glass_angular_effect mirror glass_mat
    1 glass_alt_mat
    0
    3 1 1 1
    """
    mm = Mirror.from_string(material_string)
    assert mm.to_radiance(
        minimal=True, include_modifier=False, include_dependencies=False) == \
        'glass_angular_effect mirror glass_mat 1 glass_alt_mat 0 3 1.0 1.0 1.0'
    assert mm.modifier.to_radiance(minimal=True) == \
        'void brightfunc glass_angular_effect 3 A1+(1-A1)' \
        ' (exp(-5.85 Rdot)-0.00287989916) . 0 1 0.08'
    assert mm.alternate_material.to_radiance(minimal=True) == \
        'void glass glass_alt_mat 0 0 3 0.96 0.96 0.96'

    # alternate material should show up in dependencies for to_radiance to work correctly
    assert mm.dependencies[0] == mm.alternate_material
    # but it should not be part of the private dependencies
    assert mm._dependencies == []


def test_from_to_dict_with_alternate_material():
    material_string = """
    void glass glass_alt_mat
    0
    0
    3 0.96 0.96 0.96

    void brightfunc glass_angular_effect
    3 A1+(1-A1) (exp(-5.85 Rdot)-0.00287989916) .
    0
    1 0.08

    glass_angular_effect mirror glass_mat
    1 glass_alt_mat
    0
    3 1 1 1
    """
    mm = Mirror.from_string(material_string)
    mmc = Mirror.from_dict(mm.to_dict())
    assert mm == mmc


def test_from_primitive_dict_with_alt_material():
    alt_mat = {
        'modifier': 'void',
        'type': 'glass',
        'identifier': 'glass_alt_mat',
        'values': [[], [], [0.96, 0.96, 0.96]]
    }

    input_dict = {
        'modifier': 'void',
        'type': 'mirror',
        'identifier': 'mirror_mat',
        'values': [[alt_mat], [], [1, 1, 1]]
    }

    mm = Mirror.from_primitive_dict(input_dict)
    assert mm.alternate_material.modifier == VOID
    assert mm.alternate_material.type == 'glass'


def test_from_to_dict_with_void_alternate_material():
    material_string = """
    void mirror mirror_mat
    1 void
    0
    3 1 1 1
    """
    mm = Mirror.from_string(material_string)
    mmc = Mirror.from_dict(mm.to_dict())
    assert mm == mmc


def test_material_with_void_alternate():
    mm = Mirror('mirror_mat', alternate_material=VOID)
    assert mm.to_radiance(minimal=True) == \
        'void mirror mirror_mat 1 void 0 3 1.0 1.0 1.0'
