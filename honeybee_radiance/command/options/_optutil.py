import subprocess
from typing import Union, Tuple, List
import os


def _gen_opt_file(command, folder='.'):
    """This method generate a module for Radiance command options.

    It parses the output of `command -defaults`. Check the command manually to ensure it
    follows the expected structure. Here is an example.

    > rtrace -defaults
    -n 1                            # number of rendering processes
    -x 0                            # flush interval
    -y 0                            # y resolution
    -ld-                            # limit distance off
    ...

    NOTE:
        This function is only meant to be used by developers to generating a draft file
        which still needs to be reviewed.
    """
    imports = \
        'from .optionbase import OptionCollection, BoolOption, NumericOption,' \
        ' StringOption,\\\n    StringOptionJoined, IntegerOption, TupleOption'
    

    HEADER = '{0}\n\nclass {1}Options(OptionCollection):\n' \
    '    """{2} command options."""\n\n' \
    '    __slots__ = ({3})\n\n' \
    '    def __init__(self):\n' \
    '        """{2} command options."""\n'
    '        OptionCollection.__init__(self)\n' \

    # run the command a parse the output
    def get_defaults(command):
        data = subprocess.check_output([command, '-defaults'])
        # only works in python 3
        return "".join(chr(x) for x in data).split('\r\n')


    def get_set_property(parameter: str, comment: str) -> str:
        """Create @property setter and getter string."""
        base_get = '\t@property\n\tdef {0}(self):\n\t\t"""{1}"""\n\t\treturn self._{0}'
        base_set = '\t@{0}.setter\n\tdef {0}(self, value):\n\t\tself._{0}.value = value'
        getter = base_get.format(parameter, comment).replace('\t', '    ')
        setter = base_set.format(parameter).replace('\t', '    ')
        get_set = '\n\n'.join((getter, setter))
        # print(get_set)
        return get_set

    def bool_option(parameter: str, value: str, raw_comment: str) -> Tuple[str]:
        slot = "'_%s'" % parameter
        if raw_comment.endswith(' off'):
            comment = raw_comment[:-4] + ' - default: off'
        elif raw_comment.endswith(' on'):
            comment = raw_comment[:-3] + ' - default: on'
        else:
            if value == '+':
                comment = raw_comment + ' - default: on'
            elif value == '-':
                comment = raw_comment + ' - default: off'
            else:
                comment = raw_comment

        init_line = "\t\tself.%s = BoolOption('%s', '%s')" % (
            slot.replace("'", ''), parameter, comment)

        init_line = init_line.replace('\t', '    ')
        return slot, init_line, get_set_property(parameter, comment) 


    def string_option(parameter: str, value: str, raw_comment: str) -> Tuple[str]:
        slot = "'_%s'" % parameter
        comment = raw_comment + ' - default: %s%s' % (parameter, value)
        init_line = "\t\tself.%s = StringOptionJoined('%s', '%s')" % (
            slot.replace("'", ''), parameter, comment)

        init_line = init_line.replace('\t', '    ')
        return slot, init_line, get_set_property(parameter, comment) 


    def numeric_option(parameter: str, value: str, raw_comment: str) -> Tuple[str]:
        if parameter == 'as':
            parameter = 'as_'
        slot = "'_%s'" % parameter
        comment = raw_comment + ' - default: %s' % (value)
        try:
            _ = int(value)
            init_line = "\t\tself.%s = IntegerOption('%s', '%s')" % (
                slot.replace("'", ''), parameter, comment)
        except ValueError:
            # float
            init_line = "\t\tself.%s = NumericOption('%s', '%s')" % (
                slot.replace("'", ''), parameter, comment)

        init_line = init_line.replace('\t', '    ')
        return slot, init_line, get_set_property(parameter, comment) 

    def tuple_option(parameter: str, values: List[str], raw_comment: str) -> Tuple[str]:
        slot = "'_%s'" % parameter
        comment = raw_comment + ' - default: %s' % (' '.join(values))
        try:
            _ = int(values[0])
            numtype = 'int'
        except ValueError:
            # float
            numtype = 'float'

        init_line = "\t\tself.%s = TupleOption('%s', '%s', %d, %s)" % (
                slot.replace("'", ''), parameter, comment, len(values), numtype
        )

        init_line = init_line.replace('\t', '    ')
        return slot, init_line, get_set_property(parameter, comment) 

    def parse_line(line: str):
        """Parse input line."""
        data, comment = line.split('#')
        comment = comment.strip()
        data_breakdown = data.strip().split()
        if len(data_breakdown) == 1:
            # boolean or joined string
            parameter = data_breakdown[0][1:-1]
            value = data_breakdown[0][-1]
            if value in ['+', '-']:
                return bool_option(parameter, value, comment)
            else:
                # joined string
                return string_option(parameter, value, comment)
        elif len(data_breakdown) == 2:
            # intger or number
            parameter = data_breakdown[0][1:]
            value = data_breakdown[1]
            return numeric_option(parameter, value, comment)
        else:
            # tuple
            parameter = data_breakdown[0][1:]
            values = data_breakdown[1:]
            return tuple_option(parameter, values, comment)

    lines = get_defaults(command)
    # analyze each line
    slots = []
    inits = []
    get_sets = []
    for line in lines:
        if not line.strip():
            continue
        slot, init, get_set= parse_line(line)
        slots.append(slot)
        inits.append(init)
        get_sets.append(get_set)

    # generate the content for the final file.
    header = HEADER.format(imports, command.capitalize(), command, ', '.join(slots))
    fdir = os.path.dirname(__file__)
    os.chdir(fdir)
    file_path = os.path.join(folder, '%s.py' % command)
    
    with open(file_path, 'w') as output:
        output.write(header)
        output.write('\n'.join(inits))
        output.write('\n        self._on_setattr_check = True')
        output.write('\n\n')
        output.write('\n\n'.join(get_sets))
    print('created %s' % file_path)

if __name__ == '__main__':
    folder = '.'
    _gen_opt_file('rcontrib', folder)
