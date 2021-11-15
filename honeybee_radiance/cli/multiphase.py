"""honeybee radiance ray-tracing command commands."""
import click
import sys
import logging
import os
import traceback


from honeybee_radiance.config import folders
from honeybee_radiance_command.rfluxmtx import RfluxmtxOptions, Rfluxmtx
from honeybee_radiance.reader import sensor_count_from_file


_logger = logging.getLogger(__name__)


@click.group(help="Commands to run multi-phase operations in Radiance.")
def multi_phase():
    pass


@multi_phase.command("view-matrix")
@click.argument(
    "receiver-file", type=click.Path(exists=True, file_okay=True, resolve_path=True)
)
@click.argument(
    "octree", type=click.Path(exists=True, file_okay=True, resolve_path=True)
)
@click.argument(
    "sensor-grid", type=click.Path(exists=True, file_okay=True, resolve_path=True)
)
@click.option(
    "--sensor-count",
    type=click.INT,
    show_default=True,
    help="Number of sensors in sensor grid file. Number of sensors will be parsed form"
    " the sensor file if not provided.",
)
@click.option("--rad-params", show_default=True, help="Radiance parameters.")
@click.option(
    "--rad-params-locked",
    show_default=True,
    help="Protected Radiance parameters. "
    "These values will overwrite user input rad parameters.",
)
@click.option(
    "--output",
    "-o",
    show_default=True,
    help="Path to output file. If a relative path"
    " is provided it should be relative to project folder.",
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    show_default=True,
    help="A flag to show the command without running it.",
)
def view_matrix_command(
    receiver_file,
    octree,
    sensor_grid,
    sensor_count,
    rad_params,
    rad_params_locked,
    output,
    dry_run,
):
    """Calculate view matrix for a receiver file.

    \b
    Args:
        receiver_file: Path to receiver file.
        octree: Path to octree file.
        sensor_grid: Path to sensor grid file.
    """

    try:
        options = RfluxmtxOptions()
        # parse input radiance parameters
        if rad_params:
            options.update_from_string(rad_params.strip())
        # overwrite input values with protected ones
        if rad_params_locked:
            options.update_from_string(rad_params_locked.strip())

        if not sensor_count:
            sensor_count = sensor_count_from_file(sensor_grid)

        options.update_from_string('-aa 0.0 -y {}'.format(sensor_count))

        # create command.
        rfluxmtx_cmd = Rfluxmtx(
            options=options, output=output, octree=octree, sensors=sensor_grid,
            receivers=receiver_file
        )

        if dry_run:
            click.echo(rfluxmtx_cmd)
            sys.exit(0)

        env = None
        if folders.env != {}:
            env = folders.env
        env = dict(os.environ, **env) if env else None
        rfluxmtx_cmd.run(env=env)

    except Exception:
        _logger.exception("Failed to run view-matrix command.")
        traceback.print_exc()
        sys.exit(1)
    else:
        sys.exit(0)
