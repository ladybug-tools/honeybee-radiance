"""Base classes for Radiance Options."""
import honeybee.typing as typing
import honeybee_radiance.parser as parser
import honeybee_radiance.exception as exception
import ladybug.futil as futil
import os
import warnings
from itertools import chain
import re


class Option(object):
    """Radiance Option base class."""
    __slots__ = ('_name', '_value', '_description')

    def __init__(self, name, description, value=None):
        """Create Radiance option.

        Args:
            name: Short name for Radiance option (e.g. ab).
            description: Longer description for Radiance option (e.g. ambient bounces)
            value: Optional value for option (Defult: None).
        """
        self.name = name
        self.description = description
        self.value = value

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, description):
        self._description = description

    @property
    def value(self):
        """Option value."""
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    @property
    def is_set(self):
        """Return True if the value is set by user."""
        return self.value is not None

    def to_radiance(self):
        """Translate option to Radiance format."""
        if self.is_set:
            return '-%s %s' % (self.name, self.value)
        else:
            return ''

    def ToString(self):
        return self.__repr__()

    def __repr__(self):
        if self.is_set:
            return '%s\t\t# %s' % (self.to_radiance(), self.description)
        else:
            return '-%s <unset>\t# %s' % (self.name, self.description)

    def __eq__(self, other):
        return self._value == other

    def __ne__(self, other):
        return self._value != other

    def __add__(self, other):
        return self._value + other

    def __nonzero__(self):
        return bool(self._value)

    def __bool__(self):
        # python 3
        return bool(self._value)

    def __iter__(self):
        return iter(self.value)

    def __contains__(self, value):
        return value in self._value


class FileOption(Option):
    __slots__ = ()

    @property
    def value(self):
        """Option value."""
        return self._value

    @value.setter
    def value(self, value):
        if value is None:
            self._value = value
        else:
            self._value = typing.normpath(value)

    def to_radiance(self):
        """Translate option to Radiance format."""
        if self.is_set:
            return '-%s %s' % (
                self.name,
                self.value.replace('"', typing.wrapper).replace("'", typing.wrapper)
            )
        else:
            return ''


class StringOption(FileOption):
    __slots__ = ('valid_values', 'whole', 'pattern_in', 'pattern_out')

    def __init__(self, name, description, value=None, valid_values=None, whole=True,
            pattern_in=None, pattern_out=None):
        """A string Radiance option.

        Args:
            name: Option name (e.g.: aa)
            description: Longer description for Radiance option (e.g. ambient accuracy).
            value: Optional value for aa (Default: None).
            valid_values: An optional list of valid values. By default all the string
                values are valid.
            whole: Set to true if the whole input string should be compared against valid
                values. If set to False the validator will run for each charecter in
                input string.
            pattern_in: A regex pattern that input values should match (Default: None).
            pattern_out: A format pattern to be applied to value for output e.g. "'%s'"
                (Default: None).
        """
        self.valid_values = valid_values
        self.whole = whole
        FileOption.__init__(self, name, description)
        self.pattern_in = pattern_in
        self.pattern_out = pattern_out
        self.value = value

    @property
    def value(self):
        """Option value."""
        return self._value

    @value.setter
    def value(self, value):
        if value is None:
            self._value = value
        else:
            if self.pattern_in is not None:
                if not re.match(self.pattern_in, value):
                    raise ValueError(
                        'Input values for {} must match "{}" pattern.'
                        ' Invalid input value: "{}".'.format(
                            self.name, self.pattern_in, value)
                        )
            if self.valid_values is not None:
                if self.whole:
                    if value not in self.valid_values:
                        raise exception.InvalidValueError(self.name, value,
                                                          self.valid_values)
                else:
                    for v in value:
                        if v not in self.valid_values:
                            raise exception.InvalidValueError(self.name, v,
                                                              self.valid_values)

            self._value = value if not self.pattern_out else self.pattern_out % value


class StringOptionJoined(StringOption):
    """Joined String Radiance option (e.g.: vtv, fa, etc.)."""
    __slots__ = ()

    def to_radiance(self):
        """Translate option to Radiance format."""
        if self.value is not None:
            return '-%s%s' % (self.name, self.value)
        else:
            return ''


class NumericOption(Option):
    """Numerical Radiance option."""

    __slots__ = ('min_value', 'max_value')

    def __init__(self, name, description, value=None, min_value=float('-inf'),
                 max_value=float('inf')):
        """A numerical Radiance option. For integer type use IntOption class.

        Args:
            name: Option name (e.g.: aa)
            description: Longer description for Radiance option (e.g. ambient accuracy).
            value: Optional value for aa (Default: None).
            min_value: Minimum valid value for this option.
            max_value: Maximum valid value for this option.
        """
        Option.__init__(self, name, description)
        self.min_value = min_value
        self.max_value = max_value
        self.value = value

    @property
    def value(self):
        """Option value."""
        return self._value

    @value.setter
    def value(self, value):
        if value is not None:
            self._value = typing.float_in_range(
                value, self.min_value, self.max_value, self.name)
        else:
            self._value = None

    def __int__(self):
        return int(self._value)

    def __float__(self):
        return float(self._value)

    def __sub__(self, other):
        return self._value - other

    def __lt__(self, other):
        return self._value < other

    def __gt__(self, other):
        return self._value > other

    def __le__(self, other):
        return self._value <= other

    def __ge__(self, other):
        return self._value >= other

    def __mul__(self, other):
        return self._value * other

    def __floordiv__(self, other):
        return self._value // other

    def __div__(self, other):
        return self._value / other

    def __mod__(self, other):
        return self._value % other

    def __pow__(self, other):
        return self._value ** other

    def __radd__(self, other):
        return self.__add__(other)

    def __rsub__(self, other):
        return other - self._value

    def __rmul__(self, other):
        return self.__mul__(other)

    def __rfloordiv__(self, other):
        return other // self._value

    def __rdiv__(self, other):
        return other / self._value

    def __rmod__(self, other):
        return other % self._value

    def __rpow__(self, other):
        return other ** self._value


class IntegerOption(NumericOption):
    """Integer Radiance option."""

    __slots__ = ()

    @property
    def value(self):
        """Option value."""
        return self._value

    @value.setter
    def value(self, value):
        if value is not None:
            self._value = typing.int_in_range(
                value, self.min_value, self.max_value, self.name)
        else:
            self._value = None


class BoolOption(Option):
    """Boolean Radiance option."""

    __slots__ = ()

    @property
    def value(self):
        """Option value."""
        return self._value

    @value.setter
    def value(self, value):
        if value is not None:
            # this is a special case to handle read from string when + is not used
            # in Radiance -I means -I+ and -h means -h+ and so on.
            value = True if value == '' else value 
            self._value = False if value == '-' else bool(value)
        else:
            self._value = None

    def to_radiance(self):
        """Translate option to Radiance format."""
        if self.value is not None:
            return '-%s%s' % (self.name, '' if self.value else '-')
        else:
            return ''


class TupleOption(Option):
    """Tuple Radiance option."""

    __slots__ = ('length', 'numtype')

    def __init__(self, name, description, value=None, length=3, numtype=float):
        """A numerical tuple Radiance option.

        Args:
            name: Option name (e.g.: aa)
            description: Longer description for Radiance option (e.g. ambient accuracy).
            value: Optional value for aa (Default: None).
            length: Number of items in tuple (Default: 3).
            numtype: Numerical type (Default: int).
        """
        Option.__init__(self, name, description)
        self.length = length
        self.numtype = numtype
        self.value = value

    @property
    def value(self):
        """Option value."""
        return self._value

    @value.setter
    def value(self, value):
        if value is not None:
            self._value = typing.tuple_with_length(
                value, self.length, self.numtype, self.name)
        else:
            self._value = None

    def to_radiance(self):
        """Translate option to Radiance format."""
        if self.value is not None:
            return '-%s %s' % (self.name, ' '.join(str(s) for s in self.value))
        else:
            return ''

    def __getitem__(self, key):
        return self._value[key]

    def __setitem__(self, key, val):
        self._value[key] = val


class OptionCollection(object):
    """Collection of Radiance Options.

    This is base class for difference Radiance command options.
    """
    __slots__ = ('additional_options', '_on_setattr_check', '_protected')

    def __init__(self):
        # run on_setattr method on every attribute assignment
        # set to False if you are assigning several attributes all together when
        # initiating a new instance. 
        object.__setattr__(self, '_on_setattr_check', False)
        self.additional_options = {}
        # collection of protected options that cannot be set by user. This is necessary
        # for cases like rfluxmtx. Even though rfluxmtx options subclasses from rcontrib
        # a handful number of options are controlled by rfluxmtx and may not be set by
        # user.
        self._protected = ()

    @property
    def command(self):
        """Command name."""
        return self.__class__.__name__.replace('Options', '').lower()

    @property
    def slots(self):
        """Return slots including the ones from the baseclass if any."""
        slots = set(self.__slots__)
        for cls in self.__class__.__mro__[1:-2]:
            for s in getattr(cls, '__slots__', tuple()):
                if s in slots:
                    continue
                slots.add(s)
        slots = [s for s in slots if s not in self._protected]
        slots.sort()
        return slots

    @property
    def options(self):
        """Print out list of options."""
        options = []
        for opt in self.slots:
            option = getattr(self, opt)
            if not isinstance(option, Option):
                continue
            options.append(str(option))
        for k, v in self.additional_options.items():
            options.append('-%s %s\t\t# additional option with no description' % (k, v))
        return '\n'.join(options)

    def update_from_string(self, string):
        """Update options from a standard radiance string.

        If the option is not currently part of the collection, it will be added to
        additional_options.
        """
        slots = self.slots
        opt_dict = parser.parse_radiance_options(string)
        for p, v in opt_dict.items():
            if '_%s' % p in slots:
                setattr(self, p, v)
            else:
                if len(p) > 1:
                    # joined string
                    # catch special case -fio
                    try:
                        if p.startswith('f') and '_fio' in slots:
                            setattr(self, 'fio', p[1:])
                        else:
                            setattr(self, p[1], p[1:])
                    except AttributeError:
                        # fall back to unknown item 
                        pass
                    else:
                        # it is assigned - go for the next one
                        continue
                warnings.warn(
                    '"%s" is a non-standard option for %s.' % (
                        p, self.__class__.__name__
                    )
                )
                # add to additional options
                self.additional_options[p] = v

    def to_radiance(self):
        """Translate options to Radiance format."""
        options = \
            ' '.join(getattr(self, opt).to_radiance() for opt in self.slots)
        additional_options = \
            ' '.join('-%s %s' % (k, v) for k, v in self.additional_options.items())

        return ' '.join(' '.join((options, additional_options)).split())

    def to_file(self, folder, file_name, mkdir=False):
        """Write options to a file."""
        name = file_name or self.__class__.__name__ + '.opt'
        return futil.write_to_file_by_name(folder, name, self.to_radiance(), mkdir)

    def __repr__(self):
        return self.options

    def __setattr__(self, name, value):
        try:
            object.__setattr__(self, name, value)
        except AttributeError:
            try:
                object.__setattr__(self, '_' + name, value)
            except AttributeError:
                raise AttributeError(
                    '"{1}" object has no attribute "{0}".'
                    '\nYou can still try to use `update_from_string` method to add or'
                    ' update the value for "{0}" from a string. Note that there will be'
                    ' no checks for the input value from string inputs'.format(
                        name, self.__class__.__name__)
                )
        else:
            if self._on_setattr_check:
                self.on_setattr()

    def on_setattr(self):
        """This method executes after setting each new attribute.

        Use this method to add checks that are necessary for OptionCollection. For
        instance in rtrace option collection -ti and -te are exclusive. You can include a
        check to ensure this is always correct.
        """
        pass
