from honeybee_radiance.command.oconv import Oconv
import pytest
import warnings


def test_defaults():
    oconv = Oconv()
    assert oconv.command == 'oconv'
    assert oconv.options.to_radiance() == ''
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter('always')
        oconv.to_radiance()
        # verify a warning has been raised for empty scene.
        assert len(w) == 1
        assert 'no inputs.' in str(w[0].message)


def test_assigning_inputs():
    oconv = Oconv()
    with pytest.raises(ValueError):
        oconv.inputs = 'input.rad'
    
    oconv.inputs = ['input.rad']
    assert oconv.to_radiance() == 'oconv input.rad'

    oconv.inputs = ['sky.rad', 'input.rad']
    assert oconv.to_radiance() == 'oconv sky.rad input.rad'

def test_assigning_output():
    oconv = Oconv()
    oconv.inputs = ['sky.rad', 'input.rad']
    oconv.output = 'output.oct'
    assert oconv.to_radiance() == 'oconv sky.rad input.rad > output.oct'


def test_updating_options():
    oconv = Oconv()
    oconv.inputs = ['input.rad']
    oconv.output = 'output.oct'
    oconv.options.f = True
    assert oconv.to_radiance() == 'oconv -f input.rad > output.oct'


def test_to_radiance_piped():
    oconv = Oconv()
    oconv.inputs = ['input.rad']
    oconv.output = 'output.oct'
    oconv.options.f = True
    assert oconv.to_radiance(stdin_input=True) == 'oconv -f - > output.oct'
