"""Face writer to rad."""


def face_to_rad(face, direct=False):
    """generate face radiance representation."""
    rad_prop = face.properties.radiance
    if direct:
        modifier = rad_prop.modifier_dir
    else:
        modifier = rad_prop.modifier

    # TODO: Replace with default modifier set
    modifier_name = modifier.name if modifier else 'unassigned'

    rad_string = '%s polygon %s\n0\n0\n%d %s' % (
        modifier_name,
        face.name,
        len(face.vertices) * 3,
        ' '.join('\t%f %f %f\n' % (v.x, v.y, v.z) for v in face.vertices)
    )

    return rad_string
