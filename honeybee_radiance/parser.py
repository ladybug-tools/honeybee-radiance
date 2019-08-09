"""A collection of auxiliary functions for working with radiance files and objects."""
import re
import os
import collections
from honeybee_radiance_command.cutil import parse_radiance_options


# TODO: Add support for comments [#] and commands [!]
def parse_from_string(full_string):
    """
    separate a Radiance file string into multiple strings for each object.

    Args:
        rad_fileString: Radiance data as a single string. The string can be multiline.

    Returns:
        A list of strings. Each string represents a different Radiance Object
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
        rad_objects = get_radiance_objects_from_file('some_file.rad')
    """

    assert os.path.isfile(file_path), "Can't find %s." % file_path

    with open(file_path, "r") as rad_file:
        return parse_from_string(rad_file.read())


def string_to_dicts(string):
    """convert a radiance string to a list of honeybee dictionary object.

    If the primitive modifier is not void or it has other dependencies the dependency
    must also be part of the input string.

    returns:
        A list of dictionaries.
    """
    def find_object(target, index):
        for o_count, other_obj in enumerate(objects[:-(index + 1)]):
            if other_obj['name'] == target:
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
                        obj['modifier'], obj['name']
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
    """Return a single Radiance string object as a dictionary."""
    data = [
        d for dt in re.split(split_pattern_one, string)
        for d in re.split(split_pattern_one, str(dt))
    ]

    modifier, type, name = data[:3]
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
        'type': type,
        'name': name,
        'values': {0: l1, 1: l2, 2: l3},
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
        #python 2
        inf = open(filepath, 'r')
    try:
        first_line = next(inf)
        if first_line[:10] != '#?RADIANCE':
            raise ValueError(
                'File with Radiance header must start with #?RADIANCE '
                'not {}.'.format(first_line)
                )
        header_lines =[first_line]
        for line in inf:
            header_lines.append(line)
            if line[:7] == 'FORMAT=':
                break
        return len(header_lines) + 1, '\n'.join(header_lines)
    finally:
        inf.close()
