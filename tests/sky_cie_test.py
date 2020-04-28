from honeybee_radiance.lightsource.sky import CIE
from ladybug.location import Location
import os


def test_check_defaults():
    sky = CIE(38.186734, 270.410387)
    assert sky.altitude == 38.186734
    assert sky.azimuth == 270.410387
    assert sky.ground_reflectance == 0.2
    sky_radiance = sky.to_radiance()
    assert '!gensky -ang 38.186734 90.410387 +s -g 0.200' in sky_radiance
    assert sky.ground_hemisphere.to_radiance() in sky_radiance
    assert sky.sky_hemisphere.to_radiance() in sky_radiance
    assert sky.is_climate_based is False
    assert sky.is_point_in_time is True


def test_sky_types():
    sky = CIE(0, 0, 0)
    assert sky.sky_type == 0
    assert sky.sky_type_radiance == '+s'
    sky.sky_type = 1
    assert sky.sky_type == 1
    assert sky.sky_type_radiance == '-s'
    sky.sky_type = 2
    assert sky.sky_type == 2
    assert sky.sky_type_radiance == '+i'
    sky.sky_type = 3
    assert sky.sky_type == 3
    assert sky.sky_type_radiance == '-i'
    sky.sky_type = 4
    assert sky.sky_type == 4
    assert sky.sky_type_radiance == '-c'
    sky.sky_type = 5
    assert sky.sky_type == 5
    assert sky.sky_type_radiance == '-u'


def test_from_lat_long():
    latitude = 37.815214
    longitude = -122.040010
    time_zone = -8
    sky = CIE.from_lat_long(latitude, longitude, time_zone, 7, 4, 14.5)
    # Radiance output
    # gensky 7 4 14:30 +s
    # Local solar time: 14.30
    # Solar altitude and azimuth: 57.0 73.1
    assert round(sky.altitude, 1) == 57.0
    assert round(sky.azimuth - 180) == 73  # ladybug's sun position is more accurate
    assert sky.ground_reflectance == 0.2
    sky_radiance = sky.to_radiance()
    assert '!gensky -ang 57.042579 72.808289 +s -g 0.200' in sky_radiance
    assert sky.ground_hemisphere.to_radiance() in sky_radiance
    assert sky.sky_hemisphere.to_radiance() in sky_radiance


def test_from_location():
    latitude = 37.815214
    longitude = -122.040010
    time_zone = -8
    location = Location(latitude=latitude, longitude=longitude, time_zone=time_zone)
    sky = CIE.from_location(location, 7, 4, 14.5)
    assert round(sky.altitude, 1) == 57.0
    assert round(sky.azimuth - 180) == 73  # ladybug's sun position is more accurate
    assert sky.ground_reflectance == 0.2
    sky_radiance = sky.to_radiance()
    assert '!gensky -ang 57.042579 72.808289 +s -g 0.200' in sky_radiance
    assert sky.ground_hemisphere.to_radiance() in sky_radiance
    assert sky.sky_hemisphere.to_radiance() in sky_radiance


def test_to_and_from_dict():
    sky = CIE(38.186734, 270.410387)
    sky_from_dict = CIE.from_dict(sky.to_dict())

    assert sky == sky_from_dict


def test_to_file():
    sky = CIE(38.186734, 270.410387)
    sky_file = sky.to_file('./tests/assets/temp', mkdir=True)
    assert os.path.isfile(sky_file)
    with open(sky_file, 'r') as skyf:
        content = skyf.read()

    assert sky.to_radiance() in str(content)
