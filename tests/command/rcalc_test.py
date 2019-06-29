from honeybee_radiance.command.rcalc import Rcalc
import pytest
import warnings
import os


def test_defaults():
    rcalc = Rcalc()
    assert rcalc.command == 'rcalc'
    assert rcalc.options.to_radiance() == ''
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter('always')
        rcalc.to_radiance()
        # verify a warning has been raised for empty scene.
        assert len(w) == 1
        assert 'no inputs.' in str(w[0].message)


input_path = os.path.normpath('result/input.dat')
input_path_1 = os.path.normpath('result/input_1.dat')
input_path_2 = os.path.normpath('result/input_2.dat')
output_path = os.path.normpath('result/output.ill')


def test_assigning_inputs():
    rcalc = Rcalc()

    rcalc.inputs = input_path
    assert rcalc.to_radiance() == 'rcalc %s' % input_path

    rcalc.inputs = [input_path]
    assert rcalc.to_radiance() == 'rcalc %s' % input_path

    rcalc.inputs = [input_path_1, input_path_2]
    assert rcalc.to_radiance() == 'rcalc %s %s' % (input_path_1, input_path_2)

def test_assigning_output():
    rcalc = Rcalc()
    rcalc.inputs = [input_path_1, input_path_2]
    rcalc.output = output_path
    assert rcalc.to_radiance() == \
        'rcalc %s %s > %s' % (input_path_1, input_path_2, output_path)


def test_updating_options():
    rcalc = Rcalc()
    rcalc.inputs = input_path
    rcalc.output = output_path
    rcalc.options.e = '$1=(0.265*$1+0.67*$2+0.065*$3)*179/1000'
    
    if os.name == 'nt':
        assert rcalc.to_radiance() == \
            'rcalc -e "$1=(0.265*$1+0.67*$2+0.065*$3)*179/1000" %s > %s' % (
                input_path, output_path
            )
    else:
        assert rcalc.to_radiance() == \
            'rcalc -e \'$1=(0.265*$1+0.67*$2+0.065*$3)*179/1000\' %s > %s' % (
                input_path, output_path
            )


def test_to_radiance_piped():
    rcalc = Rcalc()
    rcalc.inputs = input_path
    rcalc.output = output_path
    rcalc.options.e = '$1=(0.265*$1+0.67*$2+0.065*$3)*179/1000'
    if os.name == 'nt':
        assert rcalc.to_radiance(stdin_input=True) == \
            'rcalc -e "$1=(0.265*$1+0.67*$2+0.065*$3)*179/1000" > %s' % output_path
    else:
        assert rcalc.to_radiance(stdin_input=True) == \
            'rcalc -e \'$1=(0.265*$1+0.67*$2+0.065*$3)*179/1000\' > %s' % output_path
