"""Test octree subcommands."""

from click.testing import CliRunner
from honeybee_radiance.cli.octree import create_octree_from_folder
import os


def test_octree_from_folder():
    project_folder = './tests/assets/sample_office'
    model_folder = './tests/assets/sample_office/model'
    output = 'temp/scene.oct'
    runner = CliRunner()
    result = runner.invoke(
        create_octree_from_folder, [model_folder, '--output', output]
    )
    assert result.exit_code == 0

    # check the file exist and the size is not 0
    oct_file = os.path.join(project_folder, output)
    assert os.path.isfile(oct_file) is True
    size = os.path.getsize(oct_file)
    assert size > 3200
    os.remove(oct_file)
