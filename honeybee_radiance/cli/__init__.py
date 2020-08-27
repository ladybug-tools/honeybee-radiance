"""honeybee-radiance commands which will be added to honeybee command line interface."""

try:
    import click
except ImportError:
    raise ImportError(
        'click is not installed. Try `pip install honeybee-radiance[cli]` command.'
    )

from honeybee.cli import main
from .translate import translate
from .lib import lib
from .sky import sky
from .grid import grid
from .sunpath import sunpath
from .octree import octree
from .raytrace import raytrace
from .dc import dc

# command group for all radiance extension commands.
@click.group(help='honeybee radiance commands.')
def radiance():
    pass


# add sub-commands to radiance
radiance.add_command(translate)
radiance.add_command(lib)
radiance.add_command(sky)
radiance.add_command(grid)
radiance.add_command(sunpath)
radiance.add_command(octree)
radiance.add_command(raytrace)
radiance.add_command(dc)

# add radiance sub-commands to honeybee CLI
main.add_command(radiance)
