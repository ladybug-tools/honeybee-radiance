from honeybee_radiance.lightsource.sky.certainirradiance import CertainIrradiance
import os
import sys


def test_check_defaults():
    sky = CertainIrradiance()
    assert sky.irradiance == 558.659
    assert round(sky.illuminance) == 100000
    assert sky.ground_reflectance == 0.2
    sky_radiance = sky.to_radiance()
    assert '!gensky -ang 45 0 -c -B 558.659000 -g 0.200' in sky_radiance
    assert sky.ground_hemisphere.to_radiance() in sky_radiance
    assert sky.sky_hemisphere.to_radiance() in sky_radiance


def test_from_illuminance():
    sky = CertainIrradiance.from_illuminance(100000)
    assert round(sky.irradiance, 3) == 558.659
    assert round(sky.illuminance) == 100000
    assert sky.ground_reflectance == 0.2
    sky_radiance = sky.to_radiance()
    assert '!gensky -ang 45 0 -c -B 558.659218 -g 0.200' in sky_radiance
    assert sky.ground_hemisphere.to_radiance() in sky_radiance
    assert sky.sky_hemisphere.to_radiance() in sky_radiance


def test_update_values():
    """Updating values for ground is not encouraged but is possible."""
    sky = CertainIrradiance()

    sky.irradiance = 800.0
    sky.ground_reflectance = 0.5

    assert sky.irradiance == 800.0
    assert sky.ground_reflectance == 0.5
    sky_radiance = sky.to_radiance()

    assert '!gensky -ang 45 0 -c -B 800.000000 -g 0.500' in sky_radiance
    assert sky.ground_hemisphere.to_radiance() in sky_radiance
    assert sky.sky_hemisphere.to_radiance() in sky_radiance


def test_to_and_from_dict():
    sky = CertainIrradiance()
    sky_from_dict = CertainIrradiance.from_dict(sky.to_dict())

    assert sky == sky_from_dict


def test_to_and_from_string():
    sky_string = 'irradiance 800'
    sky = CertainIrradiance.from_string(sky_string)

    sky_from_str = CertainIrradiance.from_string(str(sky))
    if (sys.version_info >= (3, 7)):
        assert sky == sky_from_str

    sky_string = 'illuminance 100000'
    sky = CertainIrradiance.from_string(sky_string)
    assert not sky.uniform

    sky_string = 'illuminance 100000 -u'
    sky = CertainIrradiance.from_string(sky_string)
    assert sky.uniform


def test_to_file():
    sky = CertainIrradiance()
    sky_file = sky.to_file('./tests/assets/temp', mkdir=True)
    assert os.path.isfile(sky_file)
    with open(sky_file, 'r') as skyf:
        content = skyf.read()

    assert sky.to_radiance() in str(content)
