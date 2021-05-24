from honeybee_radiance.lightsource.sky import ClimateBased
from ladybug.location import Location
from ladybug.wea import Wea
from ladybug.epw import EPW
import os
import sys


def test_check_defaults():
    sky = ClimateBased(38.186734, 270.410387, 702, 225)
    assert sky.altitude == 38.186734
    assert sky.azimuth == 270.410387
    assert sky.ground_reflectance == 0.2
    sky_radiance = sky.to_radiance()
    assert '!gendaylit -ang 38.186734 90.410387 -O 0 -W 702 225 -g 0.200' in sky_radiance
    assert sky.ground_hemisphere.to_radiance() in sky_radiance
    assert sky.sky_hemisphere.to_radiance() in sky_radiance
    assert sky.is_climate_based is True
    assert sky.is_point_in_time is True


def test_from_lat_long():
    latitude = 37.815214
    longitude = -122.040010
    time_zone = -8
    sky = ClimateBased.from_lat_long(
        latitude, longitude, time_zone, 7, 4, 14.5, 702, 225)
    # Radiance output
    # gendaylit 7 4 14.5 -W 702 225
    # Local solar time: 14.30
    # Solar altitude and azimuth: 57.0 73.1
    assert round(sky.altitude, 1) == 57.0
    assert round(sky.azimuth - 180) == 73  # ladybug's sun position is more accurate
    assert sky.ground_reflectance == 0.2
    sky_radiance = sky.to_radiance()
    assert '!gendaylit -ang 57.042579 72.808289 -O 0 -W 702 225 -g 0.200' in sky_radiance
    assert sky.ground_hemisphere.to_radiance() in sky_radiance
    assert sky.sky_hemisphere.to_radiance() in sky_radiance


def test_from_location():
    latitude = 37.815214
    longitude = -122.040010
    time_zone = -8
    location = Location(latitude=latitude, longitude=longitude, time_zone=time_zone)
    sky = ClimateBased.from_location(location, 7, 4, 14.5, 702, 225)
    assert round(sky.altitude, 1) == 57.0
    assert round(sky.azimuth - 180) == 73  # ladybug's sun position is more accurate
    assert sky.ground_reflectance == 0.2
    sky_radiance = sky.to_radiance()
    assert '!gendaylit -ang 57.042579 72.808289 -O 0 -W 702 225 -g 0.200' in sky_radiance
    assert sky.ground_hemisphere.to_radiance() in sky_radiance
    assert sky.sky_hemisphere.to_radiance() in sky_radiance


def test_from_wea():
    wea = './tests/assets/wea/denver.wea'
    wea = Wea.from_file(wea)
    sky = ClimateBased.from_wea(wea, 1, 1, 8)
    assert sky.direct_normal_irradiance == 68
    assert sky.diffuse_horizontal_irradiance == 87


def test_from_epw():
    epw = './tests/assets/epw/denver.epw'
    epw = EPW(epw)
    sky = ClimateBased.from_epw(epw, 1, 1, 8)
    assert sky.direct_normal_irradiance == 68
    assert sky.diffuse_horizontal_irradiance == 87


def test_from_monthly_average():
    wea = './tests/assets/wea/denver.wea'
    wea = Wea.from_file(wea)
    sky1 = ClimateBased.from_wea_monthly_average(wea, 1, 8)

    epw = './tests/assets/epw/denver.epw'
    epw = EPW(epw)
    sky2 = ClimateBased.from_epw_monthly_average(epw, 1, 8)
    assert sky1.direct_normal_irradiance == sky2.direct_normal_irradiance
    assert sky1.diffuse_horizontal_irradiance == sky2.diffuse_horizontal_irradiance


def test_to_and_from_dict():
    sky = ClimateBased(38.186734, 270.410387, 702, 225)
    sky_from_dict = ClimateBased.from_dict(sky.to_dict())

    assert sky == sky_from_dict


def test_to_and_from_string():
    sky_string = 'climate-based 21 Jun 12:00 -lat 41.78 -lon -87.75 -tz -6 ' \
        ' -dni 800 -dhi 120 -n 0 -g 0.2'
    sky = ClimateBased.from_string(sky_string)
    sky_from_str = ClimateBased.from_string(str(sky))

    if (sys.version_info >= (3, 7)):
        assert sky == sky_from_str

    sky_string = 'climate-based -alt 71.6 -az 185.2 -dni 800 -dhi 120'
    sky = ClimateBased.from_string(sky_string)


def test_to_file():
    sky = ClimateBased(38.186734, 270.410387, 702, 225)
    sky_file = sky.to_file('./tests/assets/temp', mkdir=True)
    assert os.path.isfile(sky_file)
    with open(sky_file, 'r') as skyf:
        content = skyf.read()

    assert sky.to_radiance() in str(content)
