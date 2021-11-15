"""A collection of auxiliary functions for working with radiance files and objects."""
import re
import os


# TODO: Add support for comments [#] and commands [!]
def parse_from_string(full_string):
    """Separate a Radiance file string into multiple strings for each object.

    Args:
        full_string: Radiance data as a single string. The string can be multiline.

    Returns:
        A list of strings. Each string represents a different Radiance primitive
        (geometry or modifier). Comments [#] and commands [!] are excluded.
    """
    raw_rad_objects = re.findall(
        r'^\s*([^0-9].*(\s*[\d.-]+.*)*)',
        full_string,
        re.MULTILINE)

    rad_objects = (' '.join(radiance_object[0].split())
                   for radiance_object in raw_rad_objects)

    filtered_objects = tuple(rad_object for rad_object in rad_objects
                             if rad_object and rad_object[0] not in ['#', '!'])

    return filtered_objects


def parse_from_file(file_path):
    """Parse a Radiance file.

    This function breaks down the file into a list of radiance objects as separate
    strings.

    Args:
        file_path: Path to Radiance file

    Returns:
        A list of strings. Each string represents a different Radiance object.

    Usage:

    .. code-block:: python

        rad_obj_strs = parse_from_file('some_file.rad')
    """

    assert os.path.isfile(file_path), "Can't find %s." % file_path

    with open(file_path, "r") as rad_file:
        return parse_from_string(rad_file.read())


def string_to_dicts(string):
    """Convert a radiance string to a list of primitive dictionaries.

    These primitive dictionaries can be seralized to honeybee-radiance Python
    objects using the from_primitive_dict methods on all primitive classes.

    If the primitive modifier is not void or the primitive has other dependencies,
    the dependency must also be part of the input string and this method will
    ensure that the dependent output dictionaries are correctly nested so that
    they can be correctly serialized.

    Returns:
        A list of dictionaries.
    """
    def find_object(target, index):
        for o_count, other_obj in enumerate(objects[:-(index + 1)]):
            if other_obj['identifier'] == target:
                return o_count, other_obj

    input_objects = parse_from_string(string)

    if not input_objects:
        raise ValueError(
            '{} includes no radiance objects.'.format(string)
        )

    # break down each object and convert it to a dict
    objects = [string_to_dict(inp) for inp in input_objects]

    # start from the last material and try to find dependencies if any)
    rev_objects = list(reversed(objects))
    remove_index = []
    for count, obj in enumerate(rev_objects):

        if obj['modifier'] != 'void':
            # try to find it in objects and add replace it
            try:
                o_count, other_obj = find_object(obj['modifier'], count)
            except TypeError:
                # didn't find any
                raise ValueError(
                    'Failed to find "{}" modifier for "{}" in input string'.format(
                        obj['modifier'], obj['identifier']
                    )
                )
            else:
                objects[-(count + 1)]['modifier'] = other_obj
                remove_index.append(o_count)

        if len(obj['values'][0]) != 0:
            for value in obj['values'][0]:
                if '(' in value or '"' in value:
                    continue
                # search for dependencies
                try:
                    o_count, other_obj = find_object(value, count)
                except TypeError:
                    # didn't find any
                    pass
                else:
                    objects[-(count + 1)]['dependencies'].append(other_obj)
                    remove_index.append(o_count)

    if remove_index:
        return [obj for index, obj in enumerate(objects) if index not in remove_index]
    else:
        return objects


# pattern one handles whitespaces inside ( )
# pattern two handles whitespaces inside " "
# I assume someone who knows re better than I do can do this in a single run!
split_pattern_one = re.compile(r"\s+(?=[^(\")]*(?:\(|$))")
split_pattern_two = re.compile(r"\s+(?=[^()]*(?:\"\w))")


def string_to_dict(string):
    """Get a single Radiance string object as a primitive dictionary."""
    data = [
        d for dt in re.split(split_pattern_one, string)
        for d in re.split(split_pattern_one, str(dt))
    ]

    modifier, primitive_type, identifier = data[:3]
    base_data = data[3:]

    count_1 = int(base_data[0])
    count_2 = int(base_data[count_1 + 1])
    count_3 = int(base_data[count_1 + count_2 + 2])

    l1 = [] if count_1 == 0 else base_data[1: count_1 + 1]
    l2 = [] if count_2 == 0 \
        else base_data[count_1 + 2: count_1 + count_2 + 2]
    l3 = [] if count_3 == 0 \
        else base_data[count_1 + count_2 + 3: count_1 + count_2 + count_3 + 3]

    return {
        'modifier': modifier,
        'type': primitive_type,
        'identifier': identifier,
        'values': [l1, l2, l3],
        'dependencies': []
    }


def parse_header(filepath):
    """Return radiance file header if exist.

    This method returns all the lines between `#?RADIANCE` and `FORMAT=*` and number of
    header lines including the white line after last header line.

    Args:
        filepath: Full path to Radiance file.

    Returns:
        line_count, header as a single multiline string
    """
    try:
        inf = open(filepath, 'r', encoding='utf-8')
    except:
        # python 2
        inf = open(filepath, 'r')
    try:
        first_line = next(inf)
        if first_line[:10] != '#?RADIANCE':
            raise ValueError(
                'File with Radiance header must start with #?RADIANCE '
                'not {}.'.format(first_line)
                )
        header_lines = [first_line]
        for line in inf:
            header_lines.append(line)
            if line[:7] == 'FORMAT=':
                break
        return len(header_lines) + 1, '\n'.join(header_lines)
    finally:
        inf.close()


def sensor_count_from_file(filepath):
    """Return sensor count of a sensor grid file.

    This function returns the sensor count of a sensor grid file. Comments [#] and
    empty lines will not be counted.

    Args:
        filepath: Full path to Radiance pts file.

    Returns:
        sensor_count
    """
    sensor_count = 0
    with open(filepath, 'r') as pts_file:
        for l in pts_file:
            if not l.strip() or l[0] == '#':
                pass
            else:
                sensor_count += 1
    return sensor_count