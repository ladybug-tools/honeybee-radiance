# coding=utf-8
"""Methods to write to rad."""
from ladybug.futil import write_to_file_by_name, preparedir, nukedir
from honeybee.config import folders
from honeybee.boundarycondition import Surface
from honeybee_radiance_folder.folder import ModelFolder

from .geometry import Polygon
from .modifier.material import BSDF
from .lib.modifiers import black

import os
import shutil


def shade_to_rad(shade, blk=False, minimal=False):
    """Generate an RAD string representation of a Shade.

    Note that the resulting string does not include modifier definitions. Nor
    does it include any states for dynamic geometry.

    Args:
        shade: A honeybee Shade for which a RAD representation will be returned.
        blk: Boolean to note whether the "blacked out" version of the Shade should
            be output, which is useful for direct studies and isolation studies
            to understand the contribution of individual apertures.
        minimal: Boolean to note whether the radiance string should be written
            in a minimal format (with spaces instead of line breaks). Default: False.
    """
    rad_prop = shade.properties.radiance
    modifier = rad_prop.modifier_blk if blk else rad_prop.modifier
    rad_poly = Polygon(shade.identifier, shade.vertices, modifier)
    return rad_poly.to_radiance(minimal, False, False)


def door_to_rad(door, blk=False, minimal=False):
    """Generate an RAD string representation of a Door.

    Note that the resulting string does not include modifier definitions. Nor
    does it include any states for dynamic geometry. However, it does include
    any of the shades assigned to the Door.

    Args:
        door: A honeybee Door for which a RAD representation will be returned.
        blk: Boolean to note whether the "blacked out" version of the Door should
            be output, which is useful for direct studies and isolation studies
            to understand the contribution of individual apertures.
        minimal: Boolean to note whether the radiance string should be written
            in a minimal format (with spaces instead of line breaks). Default: False.
    """
    rad_prop = door.properties.radiance
    modifier = rad_prop.modifier_blk if blk else rad_prop.modifier
    rad_poly = Polygon(door.identifier, door.vertices, modifier)
    door_strs = [rad_poly.to_radiance(minimal, False, False)]
    for shd in door.shades:
        door_strs.append(shade_to_rad(shd, blk, minimal))
    return '\n\n'.join(door_strs)


def aperture_to_rad(aperture, blk=False, minimal=False):
    """Generate an RAD string representation of an Aperture.

    Note that the resulting string does not include modifier definitions. Nor
    does it include any states for dynamic geometry. However, it does include
    the shade geometry assigned to the Aperture.

    Args:
        aperture: A honeybee Aperture for which a RAD representation will be returned.
        blk: Boolean to note whether the "blacked out" version of the Aperture should
            be output, which is useful for direct studies and isolation studies
            to understand the contribution of individual apertures.
        minimal: Boolean to note whether the radiance string should be written
            in a minimal format (with spaces instead of line breaks). Default: False.
    """
    rad_prop = aperture.properties.radiance
    modifier = rad_prop.modifier_blk if blk else rad_prop.modifier
    rad_poly = Polygon(aperture.identifier, aperture.vertices, modifier)
    ap_strs = [rad_poly.to_radiance(minimal, False, False)]
    for shd in aperture.shades:
        ap_strs.append(shade_to_rad(shd, blk, minimal))
    return '\n\n'.join(ap_strs)


def face_to_rad(face, blk=False, minimal=False):
    """Get Face as a Radiance string.

    Note that the resulting string does not include modifier definitions. Nor
    does it include any states for dynamic geometry. However, it does include
    any of the shades assigned to the Face along with the Apertures and Doors
    in the Face.

    Args:
        face: A honeybee Face for which a RAD representation will be returned.
        blk: Boolean to note whether the "blacked out" version of the Face should
            be output, which is useful for direct studies and isolation studies
            to understand the contribution of individual apertures.
        minimal: Boolean to note whether the radiance string should be written
            in a minimal format (with spaces instead of line breaks). Default: False.
    """
    rad_prop = face.properties.radiance
    modifier = rad_prop.modifier_blk if blk else rad_prop.modifier
    rad_poly = Polygon(face.identifier, face.punched_vertices, modifier)
    face_strs = [rad_poly.to_radiance(minimal, False, False)]
    for shd in face.shades:
        face_strs.append(shade_to_rad(shd, blk, minimal))
    for dr in face.doors:
        face_strs.append(door_to_rad(dr, blk, minimal))
    for ap in face.apertures:
        face_strs.append(aperture_to_rad(ap, blk, minimal))
    return '\n\n'.join(face_strs)


def room_to_rad(room, blk=False, minimal=False):
    """Generate an RAD string representation of a Room.

    This method will write all geometry associated with a Room including all
    Faces, Apertures, Doors, and Shades. However, it does not include modifiers
    for this geometry. Nor does it include any states for dynamic geometry and
    will only write the default state for each dynamic object.

    Args:
        room: A honeybee Room for which a RAD representation will be returned.
        blk: Boolean to note whether the "blacked out" version of the geometry
            should be output, which is useful for direct studies and isolation
            studies to understand the contribution of individual apertures.
        minimal: Boolean to note whether the radiance string should be written
            in a minimal format (with spaces instead of line breaks). Default: False.
    """
    room_strs = []
    for face in room.faces:
        room_strs.append(face_to_rad(face, blk, minimal))
    for shd in room.shades:
        room_strs.append(shade_to_rad(shd, blk, minimal))
    return '\n\n'.join(room_strs)


def model_to_rad(model, blk=False, minimal=False):
    r"""Generate an RAD string representation of a Model.

    The resulting strings will include all geometry (Rooms, Faces, Shades, Apertures,
    Doors) and all modifiers. However, it does not include any states for dynamic
    geometry and will only write the default state for each dynamic object. To
    correctly account for dynamic objects, the model_to_rad_folder should be used.

    Note that this method will also ensure that any Faces, Apertures, or Doors
    with Surface boundary condition only have one of such objects in the output
    string.

    Args:
        model: A honeybee Model for which a RAD representation will be returned.
        blk: Boolean to note whether the "blacked out" version of the geometry
            should be output, which is useful for direct studies and isolation
            studies to understand the contribution of individual apertures.
        minimal: Boolean to note whether the radiance string should be written
            in a minimal format (with spaces instead of line breaks). Default: False.
    
    Returns:
        A tuple of two strings.

        -   model_str: A radiance string that contains all geometry of the Model.

        -   modifier_str: A radiance string that contains all of the modifiers
            in the model. These will be modifier_blk if blk is True.
    """
    # write all modifiers into the file
    modifier_str = ['#   ============== MODIFIERS ==============\n']
    rad_prop = model.properties.radiance
    modifiers = rad_prop.blk_modifiers if blk else rad_prop.modifiers
    for mod in modifiers:
        modifier_str.append(mod.to_radiance(minimal))

    # write all Faces into the file
    model_str = ['#   ================ MODEL ================\n']
    faces = model.faces
    interior_faces = set()
    if len(faces) != 0:
        model_str.append('#   ================ FACES ================\n')
        for face in faces:
            if isinstance(face.boundary_condition, Surface):
                if face.identifier in interior_faces:
                    continue
                interior_faces.add(face.boundary_condition.boundary_condition_object)
            model_str.append(face_to_rad(face, blk, minimal))

    # write all orphaned Apertures into the file
    apertures = model.orphaned_apertures
    interior_aps = set()
    if len(apertures) != 0:
        model_str.append('#   ============== APERTURES ==============\n')
        for ap in apertures:
            if isinstance(ap.boundary_condition, Surface):
                if ap.identifier in interior_aps:
                    continue
                interior_aps.add(ap.boundary_condition.boundary_condition_object)
            model_str.append(aperture_to_rad(ap, blk, minimal))

    # write all orphaned Doors into the file
    doors = model.orphaned_doors
    interior_drs = set()
    if len(doors) != 0:
        model_str.append('#   ================ DOORS ================\n')
        for dr in doors:
            if isinstance(dr.boundary_condition, Surface):
                if dr.identifier in interior_drs:
                    continue
                interior_drs.add(dr.boundary_condition.boundary_condition_object)
            model_str.append(door_to_rad(dr, blk, minimal))

    # write all Room shades into the file
    rooms = model.rooms
    if len(rooms) != 0:
        model_str.append('#   ============== ROOM SHADES ==============\n')
        for room in rooms:
            for shd in room.shades:
                model_str.append(shade_to_rad(shd, blk, minimal))

    # write all orphaned Shades into the file
    shades = model.orphaned_shades
    if len(shades) != 0:
        model_str.append('#   ============= CONTEXT SHADES =============\n')
        for shd in shades:
            model_str.append(shade_to_rad(shd, blk, minimal))

    return '\n\n'.join(model_str), '\n\n'.join(modifier_str)


def model_to_rad_folder(model, folder=None, minimal=False):
    r"""Write a honeybee model to a rad folder.

    The rad files in the resulting folders will include all geometry
    (Rooms, Faces, Shades, Apertures, Doors), all modifiers, and all states
    of dynamic objects.

    Args:
        model: A honeybee Model for which radiance folder will be written.
        folder: An optional folder to be used as the root of the model's
            Radiance folder. If None, the files will be written into a sub-directory
            of the honeybee-core default_simulation_folder. This sub-directory
            is specifically: default_simulation_folder/[MODEL IDENTIFIER]/Radiance
        minimal: Boolean to note whether the radiance strings should be written
            in a minimal format (with spaces instead of line breaks). Default: False.
    """
    # prepare the folder for simulation
    model_id = model.identifier
    if folder is None:
        folder = os.path.join(folders.default_simulation_folder, model_id, 'Radiance')
    if os.path.isdir(folder):
        nukedir(folder, rmdir=True)  # delete the folder if it already exists
    else:
        preparedir(folder)  # create the directory if it's not there
    model_folder = ModelFolder(folder)
    model_folder.write()

    # gather static apertures
    exterior_aps, exterior_aps_blk, interior_aps, interior_aps_blk = \
        model.properties.radiance.subfaces_by_interior_exterior()

    # write exterior static apertures
    ext_mods, ext_mods_blk, mod_combs, mod_names = \
        _collect_modifiers(exterior_aps, exterior_aps_blk, True)
    _write_static_files(folder, model_folder.STATIC_APERTURE_EXTERIOR, model_id,
                        exterior_aps, exterior_aps_blk, ext_mods, ext_mods_blk,
                        mod_combs, mod_names, False, minimal)

    # write interior static apertures
    int_mods, int_mods_blk, mod_combs, mod_names = \
        _collect_modifiers(interior_aps, interior_aps_blk, True)
    _write_static_files(folder, model_folder.STATIC_APERTURE_INTERIOR, model_id,
                        interior_aps, interior_aps_blk, int_mods, int_mods_blk,
                        mod_combs, mod_names, False, minimal)

    # gather static faces
    opaque_faces, opaque_faces_blk, nonopaque_faces, nonopaque_faces_blk = \
        model.properties.radiance.faces_by_opaque()

    # write opaque static faces
    of_mods, of_mods_blk, mod_combs, mod_names = \
        _collect_modifiers(opaque_faces, opaque_faces_blk, True)
    _write_static_files(folder, model_folder.STATIC_OPAQUE_ROOT, model_id,
                        opaque_faces, opaque_faces_blk, of_mods, of_mods_blk,
                        mod_combs, mod_names, True, minimal)
    
    # write nonopaque static faces
    nof_mods, nof_mods_blk, mod_combs, mod_names = \
        _collect_modifiers(nonopaque_faces, nonopaque_faces_blk, False)
    _write_static_files(folder, model_folder.STATIC_NONOPAQUE_ROOT, model_id,
                        nonopaque_faces, nonopaque_faces_blk, nof_mods, nof_mods_blk,
                        mod_combs, mod_names, True, minimal)

    # gather static indoor shades
    opaque_shades, opaque_shades_blk, nonopaque_shades, nonopaque_shades_blk = \
        model.properties.radiance.indoor_shades_by_opaque()

    # write opaque static indoor shades
    os_mods, os_mods_blk, mod_combs, mod_names = \
        _collect_modifiers(opaque_shades, opaque_shades_blk, True)
    _write_static_files(folder, model_folder.STATIC_OPAQUE_INDOOR, model_id,
                        opaque_shades, opaque_shades_blk, os_mods, os_mods_blk,
                        mod_combs, mod_names, False, minimal)
    
    # write nonopaque static indoor shades
    nos_mods, nos_mods_blk, mod_combs, mod_names = \
        _collect_modifiers(nonopaque_shades, nonopaque_shades_blk, False)
    _write_static_files(folder, model_folder.STATIC_NONOPAQUE_INDOOR, model_id,
                        nonopaque_shades, nonopaque_shades_blk, nos_mods, nos_mods_blk,
                        mod_combs, mod_names, False, minimal)

    # gather static outdoor shades
    opaque_shades, opaque_shades_blk, nonopaque_shades, nonopaque_shades_blk = \
        model.properties.radiance.outdoor_shades_by_opaque()

    # write opaque static outdoor shades
    os_mods, os_mods_blk, mod_combs, mod_names = \
        _collect_modifiers(opaque_shades, opaque_shades_blk, True)
    _write_static_files(folder, model_folder.STATIC_OPAQUE_OUTDOOR, model_id,
                        opaque_shades, opaque_shades_blk, os_mods, os_mods_blk,
                        mod_combs, mod_names, False, minimal)

    # write nonopaque static outdoor shades
    nos_mods, nos_mods_blk, mod_combs, mod_names = \
        _collect_modifiers(nonopaque_shades, nonopaque_shades_blk, False)
    _write_static_files(folder, model_folder.STATIC_NONOPAQUE_OUTDOOR, model_id,
                        nonopaque_shades, nonopaque_shades_blk, nos_mods, nos_mods_blk,
                        mod_combs, mod_names, False, minimal)


def _write_static_files(
        folder, sub_folder, model_id, geometry, geometry_blk, modifiers, modifiers_blk,
        mod_combs, mod_names, punched_verts=False, minimal=False):
    """Write out the three files that need to go into any static radiance model folder.

    This includes a .rad, .mat, and .blk file for the folder.
    This method will also catch any cases of BSDF modifiers and copy the XML files
    to the bsdf folder of the model folder.

    Args:
        folder: The model folder location on this machine.
        sub_folder: The sub-folder for the three files (relative to the model folder).
        model_id: A Model identifier to be used for the names of each of the files.
        geometry: A list of geometry objects all with default blk modifiers.
        geometry_blk: A list of geometry objects with overridden blk modifiers.
        modifiers: A list of modifiers to write.
        modifiers_blk: A list of modifier_blk to write.
        mod_combs: Dictionary of modifiers from _unique_modifier_blk_combinations method.
        mod_names: Modifier names from the _unique_modifier_blk_combinations method.
        punched_verts: Boolean noting whether punched geometry should be written
        minimal: Boolean noting whether radiance strings should be written minimally.
    """
    if len(geometry) != 0 or len(geometry_blk) != 0:
        # write the strings for the geometry
        face_strs = []
        if punched_verts:
            for face in geometry:
                modifier = face.properties.radiance.modifier
                rad_poly = Polygon(face.identifier, face.punched_vertices, modifier)
                face_strs.append(rad_poly.to_radiance(minimal, False, False))
            for face, mod_name in zip(geometry_blk, mod_names):
                modifier = mod_combs[mod_name][0]
                rad_poly = Polygon(face.identifier, face.punched_vertices, modifier)
                face_strs.append(rad_poly.to_radiance(minimal, False, False))
        else:
            for face in geometry:
                modifier = face.properties.radiance.modifier
                rad_poly = Polygon(face.identifier, face.vertices, modifier)
                face_strs.append(rad_poly.to_radiance(minimal, False, False))
            for face, mod_name in zip(geometry_blk, mod_names):
                modifier = mod_combs[mod_name][0]
                rad_poly = Polygon(face.identifier, face.vertices, modifier)
                face_strs.append(rad_poly.to_radiance(minimal, False, False))

        # write the strings for the modifiers
        mod_strs = []
        mod_blk_strs = []
        for mod in modifiers:
            if isinstance(mod, BSDF):
                _process_bsdf_modifier(folder, mod, mod_strs, minimal)
            else:
                mod_strs.append(mod.to_radiance(minimal))
        for mod in modifiers_blk:
            if isinstance(mod, BSDF):
                _process_bsdf_modifier(folder, mod, mod_strs, minimal)
            else:
                mod_blk_strs.append(mod.to_radiance(minimal))

        # write the three files for the model sub-folder
        dest = os.path.join(folder, sub_folder)
        write_to_file_by_name(dest, '{}.rad'.format(model_id), '\n\n'.join(face_strs))
        write_to_file_by_name(dest, '{}.mat'.format(model_id), '\n\n'.join(mod_strs))
        write_to_file_by_name(dest, '{}.blk'.format(model_id), '\n\n'.join(mod_blk_strs))


def _unique_modifiers(geometry_objects):
    """Get a list of unique modifiers across an array of geometry objects.
    
    Args:
        geometry_objects: An array of geometry objects (Faces, Apertures,
            Doors, Shades) for which unique modifiers will be determined.

    Returns:
        A list of all unique modifiers across the input geometry_objects
    """
    modifiers = []
    for obj in geometry_objects:
        mod = obj.properties.radiance.modifier
        if not _instance_in_array(mod, modifiers):
            modifiers.append(mod)
    return list(set(modifiers))


def _unique_modifier_blk_combinations(geometry_objects):
    """Get lists of unique modifier/mofidier_blk combinations across geometry objects.

    Args:
        geometry_objects: An array of geometry objects (Faces, Apertures,
            Doors, Shades) for which unique combinations of modifier and
            modifier_blk will be determined.
    
    Returns:
        A tuple with two objects.

        -   modifier_combs: A dictionary of modifiers with identifiers of
            modifiers as keys and tuples with two modifiers as values. Each
            item in the dictionary represents a unique combination of modifier
            and modifer_blk found in the objects. Both modifiers in the pair
            have the same identifier (making them write-able into a radiance
            folder). The first item in the tuple is the true modifier while
            the second one is the modifier_blk.

        -   modifier_names: A list of modifier names with one name for each of
            the input geometry_objects. These names can be looked up in the
            modifier_combs dictionary to get the modifier combination for a
            given geometry object
    """
    modifier_combs = {}
    modifier_names = []
    for obj in geometry_objects:
        mod = obj.properties.radiance.modifier
        mod_blk = obj.properties.radiance.modifier_blk
        comb_name = '{}_{}'.format(mod.identifier, mod_blk.identifier)
        modifier_names.append(comb_name)
        try:  # test to see if the combination already exists
            modifier_combs[comb_name]
        except KeyError:  # new combination of modifier and modifier_blk
            new_mod = mod.duplicate()
            new_mod.identifier = comb_name
            new_mod_blk = mod_blk.duplicate()
            new_mod_blk.identifier = comb_name
            modifier_combs[comb_name] = (new_mod, new_mod_blk)
    return modifier_combs, modifier_names


def _collect_modifiers(geo, geo_blk, opaque_or_aperture):
    """Collect all modifier and modifier_blk across geometry."""
    mods = _unique_modifiers(geo)
    if opaque_or_aperture:
        mods_blk = [black.duplicate() for mod in mods]
        for i, mod in enumerate(mods):
            mods_blk[i].identifier = mod.identifier
    else:
        mods_blk = mods[:]  # copy the list
    mod_combs, mod_names = _unique_modifier_blk_combinations(geo_blk)
    mods.extend([mod_comb[0] for mod_comb in mod_combs.values()])
    mods_blk.extend([mod_comb[1] for mod_comb in mod_combs.values()])
    return mods, mods_blk, mod_combs, mod_names


def _process_bsdf_modifier(folder, modifier, mod_strs, minimal):
    """Process a BSDF modifier for a radiance model folder."""
    # copy the BSDF to the model radiance folder
    model_bsdf_folder = os.path.join(folder, 'model', 'bsdf')
    bsdf_name = os.path.split(modifier.bsdf_file)[-1]
    new_bsdf_path = os.path.join(model_bsdf_folder, bsdf_name)
    shutil.copy(modifier.bsdf_file, new_bsdf_path)

    # write a radiance string using the correct path to the BSDF
    mod_dup = modifier.duplicate()  # duplicate to avoid editing the original
    mod_dup.bsdf_file = new_bsdf_path
    mod_strs.append(mod_dup.to_radiance(minimal))


def _instance_in_array(object_instance, object_array):
    """Check if a specific object instance is already in an array.

    This can be much faster than  `if object_instance in object_arrary`
    when you expect to be testing a lot of the same instance of an object for
    inclusion in an array since the builtin method uses an == operator to
    test inclusion.
    """
    for val in object_array:
        if val is object_instance:
            return True
    return False
