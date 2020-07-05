"""Test SensorGrid class."""
from honeybee_radiance.lightsource.sunpath import Sunpath
from ladybug.sunpath import Sunpath as LBSunpath
from ladybug.wea import Wea
from ladybug.location import Location
from ladybug.analysisperiod import AnalysisPeriod

import pytest
import os

location_dict = {
    'city': 'Denver-Stapleton',
    'state': 'CO',
    'country': 'USA',
    'latitude': 39.76,
    'longitude': -104.86,
    'time_zone': -7.0,
    'elevation': 1611.0,
    'station_id': '724690',
    'source': 'TMY--23062',
    'type': 'Location'
}

location = Location.from_dict(location_dict)
epw_file = './tests/assets/epw/denver.epw'


def test_creation():
    sp = Sunpath(location, 10)
    assert sp.location == location
    assert sp.north == 10


def test_updating_values():
    sp = Sunpath(location)
    assert sp.north == 0
    sp.north = 10
    assert sp.north == 10
    sp.north = 0
    assert sp.north == 0


def test_invalid_input():
    with pytest.raises(AssertionError):
        Sunpath('Denver')


def test_write_to_fie():
    sp = Sunpath(location)
    lb_sp = LBSunpath.from_location(location)
    folder = './tests/assets/temp'
    filename = 'sunpath_annual'
    sp.to_file(folder, filename)
    sp_file = os.path.join(folder, '%s.rad' % filename)
    sp_mod_file = os.path.join(folder, '%s.mod' % filename)
    assert os.path.isfile(sp_file)
    assert os.path.isfile(sp_mod_file)
    with open(sp_mod_file) as inf:
        for count, _ in enumerate(inf):
            pass
    lb_tot = [i for i in range(8760) if lb_sp.calculate_sun_from_hoy(i).is_during_day]
    assert count == len(lb_tot) - 1  # number of suns - 1
    with open(sp_file) as inf:
        for count, _ in enumerate(inf):
            pass
    assert count == len(lb_tot) - 1  # number of suns - 1

    # check line info
    with open(sp_file) as inf:
        data = inf.readline().split()
    
    assert data[6] == data[6] == data[6] == '1000000.0'
    assert data[-1] == '0.533'
    assert float(data[-2]) < 0  # z vector is looking down


def test_write_to_file_hoy():
    ap = AnalysisPeriod(12, 21, 0, 12, 21, 23)
    sp = Sunpath(location)
    folder = './tests/assets/temp'
    filename = 'sunpath_dec_21'
    sp.to_file(folder, filename, hoys=ap.hoys)
    sp_file = os.path.join(folder, '%s.rad' % filename)
    sp_mod_file = os.path.join(folder, '%s.mod' % filename)
    assert os.path.isfile(sp_file)
    assert os.path.isfile(sp_mod_file)
    with open(sp_mod_file) as inf:
        for count, _ in enumerate(inf):
            pass
    assert count == 8  # number of suns - 1
    with open(sp_file) as inf:
        for count, _ in enumerate(inf):
            pass
    assert count == 8  # number of suns - 1


def test_write_to_file_timestep():
    ap = AnalysisPeriod(12, 21, 0, 12, 21, 23, timestep=4)
    sp = Sunpath(location)
    folder = './tests/assets/temp'
    filename = 'sunpath_dec_21_timestep'
    sp.to_file(folder, filename, hoys=ap.hoys)
    sp_file = os.path.join(folder, '%s.rad' % filename)
    sp_mod_file = os.path.join(folder, '%s.mod' % filename)
    assert os.path.isfile(sp_file)
    assert os.path.isfile(sp_mod_file)
    with open(sp_mod_file) as inf:
        for count, _ in enumerate(inf):
            pass
    assert count == 36  # number of suns - 1
    with open(sp_file) as inf:
        for count, _ in enumerate(inf):
            pass
    assert count == 36  # number of suns - 1


def test_write_to_file_wea():
    wea = Wea.from_epw_file(epw_file, timestep=1)
    ap = AnalysisPeriod(12, 21, 0, 12, 21, 23, timestep=1)
    sp = Sunpath(location)
    folder = './tests/assets/temp'
    filename = 'sunpath_dec_21_climate_based'
    sp.to_file(folder, filename, hoys=ap.hoys, wea=wea)
    sp_file = os.path.join(folder, '%s.rad' % filename)
    sp_mod_file = os.path.join(folder, '%s.mod' % filename)
    assert os.path.isfile(sp_file)
    assert os.path.isfile(sp_mod_file)
    with open(sp_mod_file) as inf:
        for count, _ in enumerate(inf):
            pass
    assert count == 8  # number of suns - 1
    with open(sp_file) as inf:
        for count, _ in enumerate(inf):
            pass
    assert count == 8  # number of suns - 1
    # check line info
    with open(sp_file) as inf:
        data = inf.readline().split()
    
    assert data[6] == data[6] == data[6] != '1000000.0'


def test_split_modifiers():
    ap = AnalysisPeriod(timestep=4)
    sp = Sunpath(location)
    lb_sp = LBSunpath.from_location(location)
    folder = './tests/assets/temp'
    filename = 'sunpath_timestep_4'
    sp.to_file(folder, filename, hoys=ap.hoys)
    sp_file = os.path.join(folder, '%s.rad' % filename)
    sp_mod_files = [
        os.path.join(folder, '%s_%d.mod' % (filename, count)) for count in range(2)
    ]
    assert os.path.isfile(sp_file)

    lb_tot = [i for i in ap.hoys if lb_sp.calculate_sun_from_hoy(i).is_during_day]
    sun_count = [int(len(lb_tot) / 2) - 1, int(len(lb_tot) / 2)]
    for sp_count, sp_mod_file in enumerate(sp_mod_files):
        assert os.path.isfile(sp_mod_file)
        with open(sp_mod_file) as inf:
            for count, _ in enumerate(inf):
                pass
        assert count == sun_count[sp_count]
