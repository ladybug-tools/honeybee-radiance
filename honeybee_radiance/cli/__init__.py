"""honeybee-radiance commands which will be added to honeybee command line interface."""

try:
    import click
except ImportError:
    raise ImportError(
        'click is not installed. Try `pip install . [cli]` command.'
    )

from honeybee.cli import main
from .sky import sky
from .grid import grid
from .sunpath import sunpath

# command group for all radiance extension commands.
@click.group(help='honeybee radiance commands.')
def radiance():
    pass

# add sub-commands to radiance
radiance.add_command(sky)
radiance.add_command(grid)
radiance.add_command(sunpath)

# add radiance sub-commands to honeybee CLI
main.add_command(radiance)
