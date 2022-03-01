from honeybee_radiance.modifier.material import aBSDF
import os
import json

klems_bsdf_file = './tests/assets/klemsfull.xml'
tt_bsdf_file = './tests/assets/tensortree.xml'
temp_folder = './tests/assets/temp'

def test_absdf():
    mt = aBSDF(klems_bsdf_file)
    assert os.path.normpath(mt.bsdf_file) == os.path.normpath(klems_bsdf_file)
    assert list(mt.up_orientation) == [0.01, 0.01, 1.0]
    assert mt.identifier == 'klemsfull'
    assert str(mt.modifier) == 'void'
    assert mt.function_file == '.'
    assert mt.angle_basis == 'Klems Full'
    assert mt.transform == None


def test_assign_values():
    mt = aBSDF(
        klems_bsdf_file, identifier='klemsklems', up_orientation=(0, 0, 10))
    assert os.path.normpath(mt.bsdf_file) == os.path.normpath(klems_bsdf_file)
    assert list(mt.up_orientation) == [0, 0, 10]
    assert mt.identifier == 'klemsklems'


def test_update_angle_basis_on_file_change():
    mt = aBSDF(klems_bsdf_file)
    assert mt.angle_basis == 'Klems Full'
    mt = aBSDF(tt_bsdf_file)
    assert mt.angle_basis == 'TensorTree'


def test_from_string():
    absdf_str = """
    void aBSDF klemsfull
        5 ./tests/assets/klemsfull.xml 0.01 0.01 1.0 .
    0
        0
    """
    mt = aBSDF.from_string(absdf_str)
    assert os.path.normpath(mt.bsdf_file) == os.path.normpath(klems_bsdf_file)
    assert list(mt.up_orientation) == [0.01, 0.01, 1.0]
    assert mt.identifier == 'klemsfull'
    assert str(mt.modifier) == 'void'
    assert mt.function_file == '.'
    assert mt.angle_basis == 'Klems Full'
    assert mt.transform == None


def test_to_and_from_dict():
    absdf_in = aBSDF(tt_bsdf_file)
    absdf_in_dict = absdf_in.to_dict()

    # create a new absdf from dict
    absdf_from_dict = aBSDF.from_dict(absdf_in_dict, temp_folder)

    # compare the files
    with open(absdf_in.bsdf_file, 'r') as f1, \
            open(absdf_from_dict.bsdf_file, 'r') as f2:
        assert f1.read() == f2.read()


def test_bsdf_to_json():
    """Ensure that the BSDF dictionary is serialize-able to JSON."""
    test_absdf = aBSDF(klems_bsdf_file)
    bsdf_dict = test_absdf.to_dict()
    absdf_str = json.dumps(bsdf_dict)
    new_absdf = aBSDF.from_dict(json.loads(absdf_str))

    os.remove(new_absdf.bsdf_file)
