from honeybee_radiance.modifier.material import BSDF
import os
import json

klems_bsdf_file = './tests/assets/klemsfull.xml'
tt_bsdf_file = './tests/assets/tensortree.xml'
temp_folder = './tests/assets/temp'

def test_bsdf():
    mt = BSDF(klems_bsdf_file)
    assert os.path.normpath(mt.bsdf_file) == os.path.normpath(klems_bsdf_file)
    assert list(mt.up_orientation) == [0.01, 0.01, 1.0]
    assert mt.identifier == 'klemsfull'
    assert str(mt.modifier) == 'void'
    assert mt.function_file == '.'
    assert mt.angle_basis == 'Klems Full'
    assert mt.transform == None


def test_assign_values():
    mt = BSDF(
        klems_bsdf_file, identifier='klemsklems', up_orientation=(0, 0, 10),
        thickness=10)
    assert os.path.normpath(mt.bsdf_file) == os.path.normpath(klems_bsdf_file)
    assert list(mt.up_orientation) == [0, 0, 10]
    assert mt.identifier == 'klemsklems'
    assert mt.thickness == 10


def test_update_angle_basis_on_file_change():
    mt = BSDF(klems_bsdf_file)
    assert mt.angle_basis == 'Klems Full'
    mt = BSDF(tt_bsdf_file)
    assert mt.angle_basis == 'TensorTree'


def test_from_string():
    bsdf_str = """
    void BSDF klemsfull
        6 0.0 ./tests/assets/klemsfull.xml 0.01 0.01 1.0 .
    0
        0
    """
    mt = BSDF.from_string(bsdf_str)
    assert os.path.normpath(mt.bsdf_file) == os.path.normpath(klems_bsdf_file)
    assert list(mt.up_orientation) == [0.01, 0.01, 1.0]
    assert mt.identifier == 'klemsfull'
    assert str(mt.modifier) == 'void'
    assert mt.function_file == '.'
    assert mt.angle_basis == 'Klems Full'
    assert mt.transform == None


def test_to_and_from_dict():
    bsdf_in = BSDF(tt_bsdf_file)
    bsdf_in_dict = bsdf_in.to_dict()

    # create a new bsdf from dict
    bsdf_from_dict = BSDF.from_dict(bsdf_in_dict, temp_folder)

    # compare the files
    with open(bsdf_in.bsdf_file, 'r') as f1, \
            open(bsdf_from_dict.bsdf_file, 'r') as f2:
        assert f1.read() == f2.read()


def test_bsdf_to_json():
    """Ensure that the BSDF dictionary is serialize-able to JSON."""
    test_bsdf = BSDF(klems_bsdf_file)
    bsdf_dict = test_bsdf.to_dict()
    bsdf_str = json.dumps(bsdf_dict)
    new_bsdf = BSDF.from_dict(json.loads(bsdf_str))

    os.remove(new_bsdf.bsdf_file)
