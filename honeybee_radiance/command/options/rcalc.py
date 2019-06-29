"""Rcalc parameters."""
from .optionbase import OptionCollection, FileOption, TupleOption, IntegerOption, \
    BoolOption, StringOption, StringOptionJoined
import warnings


class RcalcOptions(OptionCollection):
    """
    [ -b ][ -l ][ -p ][ -n ][ -w ][ -u ][ -tS ][ -i format ][ -o format ][ -f source ]
    [ -e expr ][ -s svar=sval ]

    Also see: https://floyd.lbl.gov/radiance/man_html/rcalc.1.html
    """

    __slots__ = ('_b', '_l', '_p', '_n', '_w', '_u', '_tS', '_i', '_o', '_f', '_e', '_s')

    def __init__(self):
        """rcalc command options."""
        OptionCollection.__init__(self)
        self._tS = StringOption('ts', 'alternative tab character')
        self._i = StringOptionJoined('i', 'alternative input format',
            valid_values=['d', 'f', 'D', 'F'])
        self._o = StringOptionJoined('o', 'alternative output format',
            valid_values=['d', 'f', 'D', 'F'])
        self._p = BoolOption('p', 'alternative / passive mode for input format')
        self._b = BoolOption('b', 'accept exact matches')
        self._l = BoolOption('l', 'ignore newlines in the input')
        self._w = BoolOption('w', 'warning messages - default: off')
        self._u = BoolOption('u', 'flush output after each record - default: off')
        self._n = BoolOption('n', 'produce single output record')
        self._f = StringOption('f', 'source file')
        self._s = StringOption('s', 'assign a string variable a string value')
        self._e = StringOption('e', 'expression', pattern_out='"%s"')
        self._on_setattr_check = True

    def on_setattr(self):
        if self.p.is_set and not self.i.is_set:
            warnings.warn('rcalc: -p has no effect unless -i is also specified.')

    @property
    def tS(self):
        """alternative tab character."""
        return self._tS

    @tS.setter
    def tS(self, value):
        self._tS.value = value

    @property
    def i(self):
        """alternative input format.
        
        A -i format option specifies a template for an alternate input record format.
        Format is interpreted as a specification string if it contains a dollar sign `$`.
        Otherwise, it is interpreted as the name of the file containing the format
        specification. In either case, if the format does not end with a newline, one
        will be added automatically. A special form of the -i option may be followed
        immediately by a `d` or an `f` and an optional count, which defaults to 1,
        indicating the number of double or float binary values to read per record on the
        input file. If the input is byte-swapped, the -iD or -iF options may be
        substituted. If binary input is specified, no format string or file is needed. 
        """
        return self._i

    @i.setter
    def i(self, value):
        self._i.value = value

    @property
    def o(self):
        """alternative output format.
        
        A -o format option specifies an alternate output record format. It is interpreted
        the same as an input specification, except that the special -od or -of options do
        not require a count, as this will be determined by the number of output channels
        in the given expressions. If byte-swapped output is desired, the -oD or -oF
        options may be substituted. 
        """
        return self._o

    @o.setter
    def o(self, value):
        self._o.value = value

    @property
    def p(self):
        """alternative / passive mode for input format.
        
        The -p option specifies "passive mode," where characters that do not match the
        input format are passed unaltered to the output. This option has no effect unless
        -i is also specified, and does not make much sense unless -o is also given. With
        both input and output formats, the passive mode can effectively substitute
        information in the middle of a file or stream without affecting the rest of the
        data.
        """
        return self._p

    @p.setter
    def p(self, value):
        self._p.value = value

    @property
    def b(self):
        """accept exact matches.
        
        The -b option instructs the program to accept only exact matches. By default,
        tabs and spaces are ignored except as field separators. 
        """
        return self._b

    @b.setter
    def b(self, value):
        self._b.value = value

    @property
    def l(self):
        """ignore newlines in the input.
        
        The -l option instructs the program to ignore newlines in the input, basically
        treating them the same as tabs and spaces. Normally, the beginning of the input
        format matches the beginning of a line, and the end of the format matches the end
        of a line. With the -l option, the input format can match anywhere on a line. 
        """
        return self._l

    @l.setter
    def l(self, value):
        self._l.value = value

    @property
    def w(self):
        """warning messages - default: on"""
        return self._w

    @w.setter
    def w(self, value):
        self._w.value = value

    @property
    def u(self):
        """flush output after each record."""
        return self._u

    @u.setter
    def u(self, value):
        self._u.value = value

    @property
    def n(self):
        """produce single output record.
        
        The -n option tells the program not to get any input, but to produce a single
        output record. Otherwise, if no files are given, the standard input is read.
        """
        return self._n

    @n.setter
    def n(self, value):
        self._n.value = value

    @property
    def f(self):
        """source file.
        
        The variable and function definitions in each -f source file are read and
        compiled.
        """
        return self._f

    @f.setter
    def f(self, value):
        self._f.value = value

    @property
    def s(self):
        """assign a string variable a string value.
        
        The -s svar=sval option can be used to assign a string variable a string value.
        If this string variable appears in an input format, only records with the
        specified value will be processed. 
        """
        return self._s

    @s.setter
    def s(self, value):
        self._s.value = value

    @property
    def e(self):
        """expression.
        
        The -e expr option can be used to define variables on the command line. Since
        many of the characters in an expression have special meaning to the shell, it
        should usually be enclosed in single quotes. 
        """
        return self._e

    @e.setter
    def e(self, value):
        self._e.value = value
