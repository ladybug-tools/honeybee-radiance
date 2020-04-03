# coding=utf-8
"""Methods to write to rad."""
from .geometry import Polygon


def shade_to_rad(shade, blk=False, minimal=False):
    """Generate an RAD string representation of a Shade.

    Note that the resulting string does not include modifier definitions. Nor
    does it include any states for dynamic geometry.

    Args:
        shade: A honeyee Shade for which an RAD representation will be returned.
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
        door: A honeyee Door for which an RAD representation will be returned.
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
        aperture: A honeyee Aperture for which an RAD representation will be returned.
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
        face: A honeyee Face for which a RAD representation will be returned.
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
        room: A honeyee Room for which an RAD representation will be returned.
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

    The resulting string will include all geometry (Rooms, Faces, Shades, Apertures,
    Doors) and all modifiers. However, it does not include any states for dynamic
    geometry and will only write the default state for each dynamic object. To
    correctly account for dynamic objects, the model_to_rad_folder should be used.

    Args:
        model: A honeyee Model for which an RAD representation will be returned.
        blk: Boolean to note whether the "blacked out" version of the geometry
            should be output, which is useful for direct studies and isolation
            studies to understand the contribution of individual apertures.
        minimal: Boolean to note whether the radiance string should be written
            in a minimal format (with spaces instead of line breaks). Default: False.
    """
    model_str = ['#   ================ MODEL ================\n']
    rad_prop = model.properties.radiance

    # write all modifiers into the file
    model_str.append('#   ============== MODIFIERS ==============\n')
    modifiers = rad_prop.blk_modifiers if blk else rad_prop.modifiers
    for mod in modifiers:
        model_str.append(mod.to_radiance(minimal, False, False))

    # write all Rooms into the file
    rooms = model.rooms
    if len(rooms) != 0:
        model_str.append('#   ================ ROOMS ================\n')
        for room in rooms:
            model_str.append(room_to_rad(room, blk, minimal))

    # write all orphaned Faces into the file
    faces = model.orphaned_faces
    if len(faces) != 0:
        model_str.append('#   ================ FACES ================\n')
        for face in faces:
            model_str.append(face_to_rad(face, blk, minimal))

    # write all orphaned Apertures into the file
    apertures = model.orphaned_apertures
    if len(apertures) != 0:
        model_str.append('#   ============== APERTURES ==============\n')
        for ap in apertures:
            model_str.append(aperture_to_rad(ap, blk, minimal))

    # write all orphaned Doors into the file
    doors = model.orphaned_doors
    if len(doors) != 0:
        model_str.append('#   ================ DOORS ================\n')
        for dr in doors:
            model_str.append(door_to_rad(dr, blk, minimal))

    # write all orphaned Shades into the file
    shades = model.orphaned_shades
    if len(shades) != 0:
        model_str.append('#   ================ SHADES ================\n')
        for shd in shades:
            model_str.append(shade_to_rad(shd, blk, minimal))

    return '\n\n'.join(model_str)
