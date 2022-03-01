"""Test cli threephase module."""
import os

from click.testing import CliRunner

from ladybug.futil import nukedir, preparedir

from honeybee_radiance.cli.threephase import three_phase_calc
from honeybee_radiance.cli.threephase import three_phase_rmtxop


def test_three_phase_calc():
    runner = CliRunner()
    sky_vector = "./tests/assets/sky/sky.mtx"
    view_matrix = "./tests/assets/multi_phase/matrices/view.vmx"
    t_matrix = "./tests/assets/clear.xml"
    daylight_matrix = "./tests/assets/multi_phase/matrices/daylight.dmx"
    output_folder = "./tests/assets/temp"
    preparedir(output_folder)
    output_matrix = "./tests/assets/temp/three_phase.res"
    cmd_args = [sky_vector, view_matrix, t_matrix, daylight_matrix, output_matrix]

    result = runner.invoke(three_phase_calc, cmd_args)
    assert result.exit_code == 0
    assert os.path.isfile("./tests/assets/temp/three_phase.res")
    nukedir(output_folder)


def test_three_phase_rmtxop():
    runner = CliRunner()
    sky_vector = "./tests/assets/sky/sky.mtx"
    view_matrix = "./tests/assets/multi_phase/matrices/view.vmx"
    t_matrix = "./tests/assets/clear.xml"
    daylight_matrix = "./tests/assets/multi_phase/matrices/daylight.dmx"
    output_folder = "./tests/assets/temp"
    preparedir(output_folder)
    output_matrix = "./tests/assets/temp/three_phase.res"
    cmd_args = [view_matrix, t_matrix, daylight_matrix, sky_vector, output_matrix]

    result = runner.invoke(three_phase_rmtxop, cmd_args)
    assert result.exit_code == 0
    assert os.path.isfile("./tests/assets/temp/three_phase.res")
    nukedir(output_folder)
