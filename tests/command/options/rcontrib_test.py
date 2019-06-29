"""Test rcontrib options."""
from honeybee_radiance.command.options.rcontrib import RcontribOptions
import pytest
import honeybee.typing as typing
import honeybee_radiance.exception as exception


def test_default():
    options = RcontribOptions()
    assert options.to_radiance() == ''


def test_assignment():
    options = RcontribOptions()
    options.c = 10000
    assert options.c == 10000
    assert options.to_radiance() == '-c 10000'
    # handle wrong value type like a boss
    options.c = '3.2'
    assert options.c == 3
    assert options.to_radiance() == '-c 3'


def test_reassignment():
    options = RcontribOptions()
    options.ab = 5
    assert options.ab == 5
    assert options.to_radiance() == '-ab 5'
    # remove assigned values
    options.ab = None
    assert options.ab == None
    assert options.to_radiance() == ''


def test_multiple_assignment():
    options = RcontribOptions()
    options.ab = 2
    options.ad = 546
    options.M = r'.\file with space'
    assert '-ab 2' in options.to_radiance()
    assert 'ad 546' in options.to_radiance()
    assert options.M == typing.normpath(r'.\file with space')


def test_boolean_assignment():
    options = RcontribOptions()
    options.w = False
    options.h = True
    assert '-w-' in options.to_radiance()
    assert '-h' in options.to_radiance()


def test_invalid_assignment():
    opts = RcontribOptions()
    with pytest.raises(AttributeError):
        opts.mm = 20

    with pytest.raises(TypeError):
        opts.ab = 'ambient bounces'  # must be a numeric value


def test_exclusives_m():
    opt = RcontribOptions()
    opt.m = 'modifier'
    with pytest.raises(exception.ExclusiveOptionsError):
        opt.M = './suns.mod'


def test_from_string_non_standard():
    opt = RcontribOptions()
    opt_str = '-g 200'
    opt.update_from_string(opt_str)
    assert '-g 200' in opt.to_radiance()


def test_from_string():
    opt = RcontribOptions()
    opt_str = '-x 600 -y 392 -ld- -ffc -fo -o vmx/window_%03d.hdr -f klems_ang.cal' \
        ' -b kbinS -bn Nkbins -m windowglow -ab 2 -ad 50000 -lw 2e-5'
    
    opt.update_from_string(opt_str)
    assert opt.x == 600
    assert opt.y == 392
    assert opt.ld == False
    assert opt.fio == 'fc'
    assert opt.fo == True
    assert opt.o == 'vmx/window_%03d.hdr'
    assert opt.f == 'klems_ang.cal'
    assert opt.b == 'kbinS'
    assert opt.bn == 'Nkbins'
    assert opt.m == 'windowglow'
    assert opt.ab == 2
    assert opt.ad == 50000
    assert opt.lw == 2e-5
