"""Commands to compute view factors to geometry."""
import click
import os
import sys
import logging
import math
from itertools import islice

from honeybee_radiance.config import folders
from honeybee_radiance.geometry import Polygon
from honeybee_radiance.modifier.material import Plastic

from honeybee_radiance_command.oconv import Oconv
from honeybee_radiance_command.rcontrib import Rcontrib, RcontribOptions
from honeybee_radiance_command._command_util import run_command

from honeybee.model import Model
from honeybee.facetype import AirBoundary
from honeybee.boundarycondition import Surface
from ladybug.futil import preparedir

_logger = logging.getLogger(__name__)


@click.group(help='Commands to compute view factors to geometry.')
def view_factor():
    pass


@view_factor.command('modifiers')
@click.argument('model-file', type=click.Path(
    exists=True, file_okay=True, dir_okay=False, resolve_path=True))
@click.option(
    '--exclude-sky/--include-sky', ' /-s',
    help='Flag to note whether a sky dome should be included in the resulting octree. '
    'The inclusion of the sky dome enables the sky view to be computed in the '
    'resulting calculation.', default=True, show_default=True
)
@click.option(
    '--exclude-ground/--include-ground', ' /-g',
    help='Flag to note whether a ground dome should be included in the resulting octree. '
    'The inclusion of the ground dome enables the ground view to be computed in the '
    'resulting calculation.', default=True, show_default=True
)
@click.option(
    '--individual-shades/--grouped-shades', ' /-shd',
    help='Flag to note whether the shade geometries should be included in the '
    'list of modifiers. Note that they are still included in the resulting octree '
    'but are just excluded from the list of modifiers.', default=True, show_default=True
)
@click.option(
    '--triangulate/--skip-triangulate', ' /-t', help='Flag to note whether '
    'the Apertures and Doors of the output model should be triangulated if '
    'they have more than 4 vertices. This triangulation is necessary to '
    'align a model with EnergyPlus results since E+ cannot accept sub-faces '
    'with more than 4 vertices.', default=True
)
@click.option(
    '--folder', default='.', help='Output folder into which the modifier and '
    'octree files will be written.'
)
@click.option(
    '--name', default='scene', help='File name, which will be used for both the '
    'modifiers and the octree.'
)
def create_view_factor_modifiers(
        model_file, exclude_sky, exclude_ground, individual_shades, triangulate,
        folder, name):
    """Translate a Model into an Octree and corresponding modifier list for view factors.

    \b
    Args:
        model_file: Full path to a Model JSON file (HBJSON) or a Model pkl (HBpkl) file.
    """
    try:
        # create the directory if it's not there
        if not os.path.isdir(folder):
            preparedir(folder)

        # load the model and ensure the properties align with the energy model
        model = Model.from_file(model_file)
        if model.units != 'Meters':
            model.convert_to_units('Meters')
        for room in model.rooms:
            room.remove_colinear_vertices_envelope(
                tolerance=0.01, delete_degenerate=True)

        # triangulate the sub-faces if requested
        if triangulate:
            apertures, parents_to_edit = model.triangulated_apertures()
            for tri_aps, edit_infos in zip(apertures, parents_to_edit):
                if len(edit_infos) == 3:
                    for room in model._rooms:
                        if room.identifier == edit_infos[2]:
                            break
                    for face in room._faces:
                        if face.identifier == edit_infos[1]:
                            break
                    for i, ap in enumerate(face._apertures):
                        if ap.identifier == edit_infos[0]:
                            break
                    face._apertures.pop(i)  # remove the aperture to replace
                    face._apertures.extend(tri_aps)
            doors, parents_to_edit = model.triangulated_doors()
            for tri_drs, edit_infos in zip(doors, parents_to_edit):
                if len(edit_infos) == 3:
                    for room in model._rooms:
                        if room.identifier == edit_infos[2]:
                            break
                    for face in room._faces:
                        if face.identifier == edit_infos[1]:
                            break
                    for i, dr in enumerate(face._doors):
                        if dr.identifier == edit_infos[0]:
                            break
                    face._doors.pop(i)  # remove the doors to replace
                    face._doors.extend(tri_drs)

        # set values to be used throughout the modifier assignment
        offset = model.tolerance * -1
        white_plastic = Plastic('white_plastic', 1, 1, 1)
        geo_strs, mod_strs, mod_names = [], [], []

        def _add_geo_and_modifier(hb_obj):
            """Add a honeybee object to the geometry and modifier strings."""
            mod_name = '%s_mod' % hb_obj.identifier
            mod_names.append(mod_name)
            white_plastic.identifier = mod_name
            rad_poly = Polygon(hb_obj.identifier, hb_obj.vertices, white_plastic)
            geo_strs.append(rad_poly.to_radiance(False, False, False))
            mod_strs.append(white_plastic.to_radiance(True, False, False))

        # loop through all geometry in the model and get radiance strings
        for room in model.rooms:
            for face in room.faces:
                if not isinstance(face.type, AirBoundary):
                    if isinstance(face.boundary_condition, Surface):
                        face.move(face.normal * offset)
                    _add_geo_and_modifier(face)
                for ap in face.apertures:
                    _add_geo_and_modifier(ap)
                for dr in face.doors:
                    _add_geo_and_modifier(dr)
        all_shades = model.shades + model._orphaned_faces + \
            model._orphaned_apertures + model._orphaned_doors
        if individual_shades:
            for shade in all_shades:
                _add_geo_and_modifier(shade)
        else:
            white_plastic.identifier = 'shade_plastic_mod'
            mod_names.append(white_plastic.identifier)
            mod_strs.append(white_plastic.to_radiance(True, False, False))
            for shade in all_shades:
                rad_poly = Polygon(shade.identifier, shade.vertices, white_plastic)
                geo_strs.append(rad_poly.to_radiance(False, False, False))

        # add the ground and sky domes if requested
        if not exclude_sky:
            mod_names.append('sky_glow_mod')
            mod_strs.append('void glow sky_glow_mod 0 0 4 1 1 1 0')
            geo_strs.append('sky_glow_mod source sky_dome 0 0 4 0 0 1 180')
        if not exclude_ground:
            mod_names.append('ground_glow_mod')
            mod_strs.append('void glow ground_glow_mod 0 0 4 1 1 1 0')
            geo_strs.append('ground_glow_mod source ground_dome 0 0 4 0 0 1 180')

        # write the radiance strings to the output folder
        geo_file = os.path.join(folder, '{}.rad'.format(name))
        mod_file = os.path.join(folder, '{}.mod'.format(name))
        oct_file = os.path.join(folder, '{}.oct'.format(name))
        with open(geo_file, 'w') as gf:
            gf.write('\n\n'.join(mod_strs + geo_strs))
        with open(mod_file, 'w') as mf:
            mf.write('\n'.join(mod_names))

        # use the radiance files to create an octree
        cmd = Oconv(output=oct_file, inputs=[geo_file])
        cmd.options.f = True
        run_command(cmd.to_radiance(), env=folders.env)
    except Exception as e:
        _logger.exception('Model translation failed.\n{}'.format(e))
        sys.exit(1)
    else:
        sys.exit(0)


@view_factor.command('contrib')
@click.argument(
    'octree', type=click.Path(exists=True, file_okay=True, resolve_path=True)
)
@click.argument(
    'sensor-grid', type=click.Path(exists=True, file_okay=True, resolve_path=True)
)
@click.argument(
    'modifiers', type=click.Path(exists=True, file_okay=True, resolve_path=True)
)
@click.option(
    '--ray-count', type=click.INT, default=6, show_default=True,
    help='The number of rays to be equally distributed over a sphere to compute '
    'the view factor for each of the input sensors.'
)
@click.option(
    '--rad-params', show_default=True, help='Radiance parameters.'
)
@click.option(
    '--rad-params-locked', show_default=True, help='Protected Radiance parameters. '
    'These values will overwrite user input rad parameters.'
)
@click.option(
    '--folder', default='.', help='Output folder into which the modifier and '
    'octree files will be written.'
)
@click.option(
    '--name', default='view_factor', help='File name, which will be used for the '
    'rebuilt sensor-grid, the matrix and the resulting CSV with view factors.'
)
def rcontrib_command_with_view_postprocess(
        octree, sensor_grid, modifiers, ray_count, rad_params, rad_params_locked,
        folder, name
):
    """Run rcontrib to get spherical view factors from a sensor grid.

    \b
    Args:
        octree: Path to octree file.
        sensor-grid: Path to sensor grid file.
        modifiers: Path to modifiers file.
    """
    try:
        # create the directory if it's not there
        if not os.path.isdir(folder):
            preparedir(folder)

        # generate the ray vectors to be used in the view factor calculation
        if ray_count == 6:
            rays = ((1, 0, 0), (0, 1, 0), (0, 0, 1), (-1, 0, 0), (0, -1, 0), (0, 0, -1))
        else:
            rays = _fibonacci_spiral(ray_count)
        ray_str = [' {} {} {}\n'.format(*ray) for ray in rays]

        # create a new .pts file with the view vectors
        ray_file = os.path.abspath(os.path.join(folder, '{}.pts'.format(name)))
        total_rays = 0
        with open(sensor_grid) as sg_file:
            with open(ray_file, 'w') as r_file:
                for line in sg_file:
                    for ray in ray_str:
                        try:
                            r_file.write(' '.join(line.split()[:3]) + ray)
                            total_rays += 1
                        except Exception:
                            pass  # we are at the end of the file

        # set up the Rcontrib options
        options = RcontribOptions()
        if rad_params:  # parse input radiance parameters
            options.update_from_string(rad_params.strip())
        if rad_params_locked:  # overwrite input values with protected ones
            options.update_from_string(rad_params_locked.strip())
        # overwrite specific options that would otherwise break the command
        options.M = modifiers
        options.update_from_string('-I -V- -y {}'.format(total_rays))

        # create the rcontrib command and run it
        mtx_file = os.path.abspath(os.path.join(folder, '{}.mtx'.format(name)))
        rcontrib = Rcontrib(options=options, octree=octree, sensors=ray_file)
        #rcontrib.output = mtx_file
        cmd = rcontrib.to_radiance().replace('\\', '/')
        cmd = '{} | rmtxop -fa - -c .333 .333 .334'.format(cmd)
        cmd = '{}  | getinfo - > {}'.format(cmd, mtx_file.replace('\\', '/'))
        run_command(cmd, env=folders.env)
        
        # load the resulting matrix and process the results into view factors
        view_fac_mtx = []
        with open(mtx_file) as mtx_data:
            while True:
                sens_lines = list(islice(mtx_data, ray_count))
                if not sens_lines:
                    break
                sens_mtx = ((float(v) for v in l.strip().split()) for l in sens_lines)
                s_facs = []
                for sens_facs in zip(*sens_mtx):
                    s_facs.append(sum(sens_facs) / (math.pi * ray_count))
                view_fac_mtx.append(s_facs)
        
        # write the final view factors into a CSV file
        view_file = os.path.join(folder, '{}.csv'.format(name))
        with open(view_file, 'w') as v_file:
            for facs in view_fac_mtx:
                v_file.write(','.join((str(v) for v in facs)) + '\n')
    except Exception:
        _logger.exception('Failed to comput view factor contributions.')
        sys.exit(1)
    else:
        sys.exit(0)


def _fibonacci_spiral(point_count=24):
    """Get points distributed uniformly across a unit spherical surface.

    Args:
        point_count: Integer for the number of points to be distributed.

    Returns:
        List of tuple, each with 3 values representing the XYZ coordinates of
        the points that were generated.
    """
    points = []
    phi = math.pi * (3. - math.sqrt(5.))

    for i in range(point_count):
        y = 1 - (i / float(point_count - 1)) * 2
        radius = math.sqrt(1 - y * y)
        theta = phi * i
        x = math.cos(theta) * radius
        z = math.sin(theta) * radius
        points.append((x, y, z))

    return points
