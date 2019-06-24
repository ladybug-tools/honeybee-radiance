"""Base classes for Radiance Options."""
import honeybee_radiance.typing as typing
import honeybee_radiance.parser as parser
import ladybug.futil as futil


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

    def to_radiance(self):
        """Translate option to Radiance format."""
        if self.value is not None:
            return '-%s %s' % (self.name, self.value)
        else:
            return ''

    def ToString(self):
        return self.__repr__()

    def __repr__(self):
        if self.value is not None:
            return '%s\t\t# %s' % (self.to_radiance(), self.description)
        else:
            return '-%s <unset>\t\t# %s' % (self.name, self.description)


class StringOption(Option):
    __slots__ = ('valid_values')

    def __init__(self, name, description, value=None, valid_values=None):
        """A string Radiance option.

        Args:
            name: Option name (e.g.: aa)
            description: Longer description for Radiance option (e.g. ambient accuracy).
            value: Optional value for aa (Default: None).
            valid_values: An optional list of valid values. By default all the string
                values are valid.
        """
        self.valid_values = valid_values
        Option.__init__(self, name, description)
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
            if self.valid_values is not None:
                assert value in self.valid_values, \
                    'Invalid input value. Valid values are: %s' % self.valid_values
            self._value = value


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
        self.value = value
        self.min_value = min_value
        self.max_value = max_value

    @property
    def value(self):
        """Option value."""
        return self._value

    @value.setter
    def value(self, value):
        if value is not None:
            self._value = typing.float_in_range(value, self.min_value, self.max_value)
        else:
            self._value = None


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
            self._value = typing.int_in_range(value, self.min_value, self.max_value)
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
            self._value = False if value == '-' else bool(value)
        else:
            self._value = None

    def to_radiance(self):
        """Translate option to Radiance format."""
        if self.value is not None:
            return '-%s%s' % (self.name, '+' if self.value else '-')
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
        self.value = value
        self.length = length
        self.numtype = numtype

    @property
    def value(self):
        """Option value."""
        return self._value

    @value.setter
    def value(self, value):
        if value is not None:
            self._value = typing.tuple_with_length(value, self.length, self.num_type)
        else:
            self._value = None

    def to_radiance(self):
        """Translate option to Radiance format."""
        if self.value is not None:
            return '-%s %s' % (self.name, ' '.join(str(s) for s in self.value))
        else:
            return ''


# TODO: catch assignment of additional values if not a property
class OptionCollection(object):
    """Collection of objects."""
    __slots__ = ('additional_options',)

    def __init__(self):
        self.additional_options = {}

    @property
    def options(self):
        """Print out list of options."""
        options = []
        for opt in self.__slots__:
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
        opt_dict = parser.parse_radiance_options(string)
        for p, v in opt_dict.items():
            if '_%s' % p in self.__slots__:
                setattr(self, p, v)
            else:
                # add to additional options
                self.additional_options[p] = v

    def to_radiance(self):
        """Translate options to Radiance format."""
        options = \
            ' '.join(getattr(self, opt).to_radiance() for opt in self.__slots__)
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
                '"{1}" object has no attribute "{0}".' \
                '\nYou can still try to use `update_from_string` method to add or' \
                ' update the value for "{0}".'.format(name, self.__class__.__name__)
                )
