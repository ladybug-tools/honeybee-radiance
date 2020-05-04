from honeybee_radiance.lightsource.sky import SunMatrix
from ladybug.wea import Wea
import os


def test_check_defaults():
    wea = './tests/assets/wea/denver.wea'
    wea = Wea.from_file(wea)
    sun_mtx = SunMatrix(wea)
    assert sun_mtx.wea == wea
    assert sun_mtx.north == 0
    assert sun_mtx.location == wea.location
    sun_mtx_radiance = sun_mtx.to_radiance()
    assert 'gendaymtx -n -D suns.mtx' in sun_mtx_radiance
    assert '-M suns.mod' in sun_mtx_radiance
    assert '-O1 in.wea' in sun_mtx_radiance
    assert sun_mtx.is_climate_based is True
    assert sun_mtx.is_point_in_time is False


def test_north():
    wea = './tests/assets/wea/denver.wea'
    wea = Wea.from_file(wea)
    sun_mtx = SunMatrix(wea, 120)
    assert sun_mtx.north == 120
    assert '-r 120' in sun_mtx.to_radiance()


def tets_to_radiance_options():
    wea = './tests/assets/wea/denver.wea'
    wea = Wea.from_file(wea)
    sun_mtx = SunMatrix(wea)
    assert '-O0' in sun_mtx.to_radiance(output_type=0)


def test_to_and_from_dict():
    wea = './tests/assets/wea/denver.wea'
    wea = Wea.from_file(wea)
    sun_mtx = SunMatrix(wea)
    sun_mtx_from_dict = sun_mtx.from_dict(sun_mtx.to_dict())

    # update this once Wea class has equality method implemeneted
    assert sun_mtx.wea.location == sun_mtx_from_dict.wea.location
    assert sun_mtx.wea.direct_normal_irradiance.values == \
        sun_mtx_from_dict.wea.direct_normal_irradiance.values
    assert sun_mtx.wea.direct_normal_irradiance.datetimes == \
        sun_mtx_from_dict.wea.direct_normal_irradiance.datetimes


def test_to_file():
    wea = './tests/assets/wea/denver.wea'
    wea = Wea.from_file(wea)
    sun_mtx = SunMatrix(wea)
    sun_mtx_file = sun_mtx.to_file('./tests/assets/temp', mkdir=True)
    assert os.path.isfile(sun_mtx_file)
    with open(sun_mtx_file, 'r') as skyf:
        content = skyf.read()

    assert sun_mtx.to_radiance() in str(content)
