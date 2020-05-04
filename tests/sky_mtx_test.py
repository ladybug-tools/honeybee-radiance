from honeybee_radiance.lightsource.sky import SkyMatrix
from ladybug.wea import Wea
import os


def test_check_defaults():
    wea = './tests/assets/wea/denver.wea'
    wea = Wea.from_file(wea)
    sky_mtx = SkyMatrix(wea)
    assert sky_mtx.wea == wea
    assert sky_mtx.north == 0
    assert sky_mtx.density == 1
    assert sky_mtx.location == wea.location
    sky_mtx_radiance = sky_mtx.to_radiance()
    # gendaymtx -O0 in.wea > sky.mtx
    assert '> sky.mtx' in sky_mtx_radiance
    assert '-O0 in.wea' in sky_mtx_radiance
    assert sky_mtx.is_climate_based is True
    assert sky_mtx.is_point_in_time is False


def test_north():
    wea = './tests/assets/wea/denver.wea'
    wea = Wea.from_file(wea)
    sky_mtx = SkyMatrix(wea, 120)
    assert sky_mtx.north == 120
    assert '-r 120' in sky_mtx.to_radiance()


def tets_to_radiance_options():
    wea = './tests/assets/wea/denver.wea'
    wea = Wea.from_file(wea)
    sky_mtx = SkyMatrix(wea, density=4)
    assert '-m 4' in sky_mtx.to_radiance()
    assert '-O1' in sky_mtx.to_radiance(output_type=1)
    assert '-A' in sky_mtx.to_radiance(cumulative=True)
    assert '-d' in sky_mtx.to_radiance(components=1)
    assert '-s' in sky_mtx.to_radiance(components=2)

def test_to_and_from_dict():
    wea = './tests/assets/wea/denver.wea'
    wea = Wea.from_file(wea)
    sky_mtx = SkyMatrix(wea)
    sky_mtx_from_dict = sky_mtx.from_dict(sky_mtx.to_dict())

    # update this once Wea class has equality method implemeneted
    assert sky_mtx.wea.location == sky_mtx_from_dict.wea.location
    assert sky_mtx.wea.direct_normal_irradiance.values == \
        sky_mtx_from_dict.wea.direct_normal_irradiance.values
    assert sky_mtx.wea.direct_normal_irradiance.datetimes == \
        sky_mtx_from_dict.wea.direct_normal_irradiance.datetimes


def test_to_file():
    wea = './tests/assets/wea/denver.wea'
    wea = Wea.from_file(wea)
    sky_mtx = SkyMatrix(wea)
    sky_mtx_file = sky_mtx.to_file('./tests/assets/temp', mkdir=True)
    assert os.path.isfile(sky_mtx_file)
    with open(sky_mtx_file, 'r') as skyf:
        content = skyf.read()

    assert sky_mtx.to_radiance() in str(content)
