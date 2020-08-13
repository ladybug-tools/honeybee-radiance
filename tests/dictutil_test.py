# coding=utf-8
from honeybee_radiance.dictutil import dict_to_object
from honeybee_radiance.modifier.material import Glass
from honeybee_radiance.modifierset import ModifierSet
from honeybee_radiance.lightsource.sky import CIE
from honeybee_radiance.lightsource.sky import SkyMatrix
from honeybee_radiance.sensor import Sensor
from honeybee_radiance.sensorgrid import SensorGrid
from honeybee_radiance.view import View
from ladybug.wea import Wea


def test_dict_to_object_modifier():
    """Test the dict_to_object method with Modifier objects."""
    gl_obj = Glass('test_glass', 0.6, 0.7, 0.8, 1.52)
    gl_dict = gl_obj.to_dict()
    new_gl = dict_to_object(gl_dict)
    assert isinstance(new_gl, Glass)


def test_dict_to_object_modifier_set():
    """Test the dict_to_object method with Modifier objects."""
    default_set = ModifierSet('Tinted_Window_Set')
    glass_material = Glass.from_single_transmittance('test_glass', 0.6)
    glass_material_dark = Glass.from_single_transmittance('test_glass_dark', 0.3)
    default_set.aperture_set.exterior_modifier = glass_material
    default_set.aperture_set.skylight_modifier = glass_material_dark

    mod_set_dict = default_set.to_dict()
    new_mod_set = dict_to_object(mod_set_dict)
    assert isinstance(new_mod_set, ModifierSet)


def test_dict_to_object_cie_sky():
    """Test the dict_to_object method with Sky objects."""
    sky_obj = CIE(38.186734, 270.410387)
    sky_dict = sky_obj.to_dict()
    new_sky = dict_to_object(sky_dict)
    assert isinstance(new_sky, CIE)


def test_dict_to_object_sky_mtx():
    """Test the dict_to_object method with SkyMatrix objects."""
    wea = './tests/assets/wea/denver.wea'
    wea = Wea.from_file(wea)
    sky_mtx_obj = SkyMatrix(wea)
    sky_mtx_dict = sky_mtx_obj.to_dict()
    new_sky_mtx = dict_to_object(sky_mtx_dict)
    assert isinstance(new_sky_mtx, SkyMatrix)


def test_dict_to_object_sensor_grid():
    """Test the dict_to_object method with SensorGrid objects."""
    sensors = [Sensor((0, 0, 0), (0, 0, 1)), Sensor((0, 0, 10), (0, 0, 1))]
    sg_obj = SensorGrid('sg_1', sensors)
    sg_dict = sg_obj.to_dict()
    new_sg = dict_to_object(sg_dict)
    assert isinstance(new_sg, SensorGrid)


def test_dict_to_object_view():
    """Test the dict_to_object method with View objects."""
    v_obj = View('test_view', (0, 0, 10), (0, 1, 0), (0, 0, 1), 'l', 240, 300, -10, -25)
    v_dict = v_obj.to_dict()
    new_v = dict_to_object(v_dict)
    assert isinstance(new_v, View)
