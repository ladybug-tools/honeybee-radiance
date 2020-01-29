"""Base class for all Radiance Primitives.

The term "Primitive" can refer to either a geometry object or a modifer that can
be applied to geometry in order to change its reflectance, transmittance, etc.
All primitives share a similar format for how they are represented within .rad
files and the Primitive class provides common code used to serialize/de-serrialize
such objects from .rad strings among other functionalities.

Because the Primitive class is so abstract, you most likely want to use one of
the sub-classes of Primitive instead of using this class directly. You will find
such sub-classes in the honeybee_radiance.modifier and honeybee_radiance.geometry
sub-packages. More information on Radiance Primitives can be found at:

http://radsite.lbl.gov/radiance/refer/ray.html
"""
from honeybee.typing import valid_rad_string, list_with_length
from honeybee._lockable import lockable

from honeybee_radiance.reader import string_to_dicts


class Void(object):
    """Void modifier.
    
    Properties:
        * name
        * is_modifier
        * is_opaque
    """
    __slots__ = ()

    @property
    def name(self):
        """Void."""
        return 'void'

    @property
    def is_modifier(self):
        """True."""
        return True

    @property
    def is_opaque(self):
        """False for a void."""
        return True

    def to_radiance(self):
        """Return full radiance definition."""
        return 'void'

    def to_dict(self):
        """Return void."""
        return self.to_radiance()

    def ToString(self):
        """Overwrite .NET ToString."""
        return self.to_radiance()

    def __repr__(self):
        return self.to_radiance()


@lockable
class Primitive(object):
    """Base class for Radiance Primitives.
    
    Properties:
        * name
        * values
        * modifier
        * dependencies
        * is_geometry
        * is_modifier
        * is_material
        * is_texture
        * is_pattern
        * is_mixture
        * is_opaque
    """
    __slots__ = ('_name', '_modifier', '_values', '_is_opaque', '_dependencies',
                 '_type', '_locked')

    # All Radiance geometry types
    GEOMETRYTYPES = set(('source', 'sphere', 'bubble', 'polygon', 'cone', 'cup',
                         'cylinder', 'tube', 'ring', 'instance', 'mesh'))

    # All Radiance material types
    MATERIALTYPES = \
        set(('plastic', 'glass', 'trans', 'metal', 'mirror', 'illum',
             'mixedfunc', 'dielectric', 'transdata', 'light', 'glow', 'BSDF',
             'void', 'spotlight', 'prism1', 'prism2', 'mist', 'plastic2',
             'metal2', 'trans2', 'ashik2', 'dielectric', 'interface',
             'plasfunc', 'metfunc', 'transfunc', 'BRTDfunc',
             'plasdata', 'metdata', 'transdata', 'antimatter'))

    TEXTURETYPES = set(('texfunc', 'texdata'))

    PATTERNTYPES = set(('colorfunc', 'brightfunc', 'colordata', 'brightdata',
                        'colorpict', 'colortext', 'brighttext'))

    MIXTURETYPES = set(('mixfunc', 'mixdata', 'mixpict', 'mixtext'))

    # All modifier types (everything except geometry)
    MODIFIERTYPES = set().union(MATERIALTYPES, MIXTURETYPES, TEXTURETYPES, PATTERNTYPES)
    
    # All Radiance primitive types
    TYPES = set().union(GEOMETRYTYPES, MODIFIERTYPES)

    # Modifierts that are not usually opaque. This will be used to set is_opaque property
    # if it is not overridded by the user by setting the is_opaque property
    NONEOPAQUETYPES = set(('glass', 'trans', 'trans2', 'transdata', 'transfunc',
                           'dielectric', 'BSDF', 'mixfunc', 'BRTDfunc', 'mist',
                           'prism1', 'prism2'))

    VOID = Void()

    def __init__(self, name, modifier=None, values=None, is_opaque=None,
                 dependencies=None):
        """Create primitive base.

        Args:
            name: Primitive name as a string. Cannot contain white spaces or special
                characters.
            modifier: Modifier. It can be primitive, mixture, texture or pattern.
                (Default: "void").
            values: An array 3 arrays for primitive data. Each of the 3 sub-arrays
                refer to a line number in the radiance primitve definitions and the
                values in each array correspond to values occurring within each line.
                For example, [[], [], ['0.500', '0.500', '0.500', '0.000', '0.050']]
                corresponds to values one would find for a Plastic material.
                (Default: [[], [], []]).
            is_opaque: A boolean to indicate whether this primitive is opaque.
            dependencies: A list of primitives that this primitive depends on. This
                argument is only useful for defining advanced primitives that are
                defined based on other primitives. (Default: []).

        """
        self.name = name
        self.type = self.__class__.__name__.lower()
        self.modifier = modifier
        self.values = values or [[], [], []]
        self._is_opaque = is_opaque
        self._dependencies = []
        dependencies = dependencies or []
        for dep in dependencies:
            self.add_dependent(dep)

    @classmethod
    def from_string(cls, primitive_string):
        """Create a Radiance primitive from a string.

        If the primitive modifier is not void or it has other dependencies,
        the modifier and/or dependencies must also be part of the input string.
        """
        pr_dict = string_to_dicts(primitive_string)
        assert len(pr_dict) == 1, \
            'Input string includes more than one Radiance objects.'
        return cls.from_primitive_dict(pr_dict[0])

    @classmethod
    def from_primitive_dict(cls, primitive_dict):
        """Initialize the object from a primitive dict.

        The primitive_dict is a dictionary following the base Primitive schema
        of a Radiance object. This base Primitive schema is the same for all
        Radiance Primitives (including Modifiers and Geometry) whereas the
        from_dict classmethod accepts a different schema that is customized
        to each subclass inheriting from the Radiance Primitive.

        Args:
            data: A dictionary in the format below.

            .. code-block:: python

            {
                "modifier": "", // primitive modifier (Default: "void")
                "type": "custom", // primitive type
                "name": "", // primitive name
                "values": [] // values,
                "dependencies": []
            }
        """
        modifier, dependencies = cls.filter_dict_input(primitive_dict)

        cls_ = cls(
            name=primitive_dict['name'],
            modifier=modifier,
            values=primitive_dict['values'],
            dependencies=dependencies
        )

        if cls_.type == 'primitive':
            cls_.type = primitive_dict['type']

        return cls_

    @classmethod
    def from_dict(cls, data):
        """Initialize the object from a dictionary.

        Args:
            data: A dictionary in the format below.

            .. code-block:: python

            {
                "modifier": "", // primitive modifier (Default: "void")
                "type": "custom", // primitive type
                "name": "", // primitive name
                "values": [] // values,
                "dependencies": []
            }
        """
        return cls.from_primitive_dict(data)

    @property
    def type(self):
        """Get or set a string for the primitive type."""
        return self._type

    @type.setter
    def type(self, type_str):
        _mapper = {'bsdf': 'BSDF', 'brtdfunc': 'BRTDfunc'}

        if type_str != 'primitive':
            if type_str not in self.TYPES:
                # try base classes for subclasses
                for base in self.__class__.__mro__:
                    if base.__name__.lower() in _mapper:
                        type_str = _mapper[base.__name__.lower()]
                        break
                    if base.__name__.lower() in self.TYPES:
                        type_str = base.__name__.lower()
                        break

            assert type_str in self.TYPES, \
                "%s is not a supported Radiance primitive type." % type_str + \
                "Try one of these primitives:\n%s" % str(self.TYPES)

        self._type = type_str
    
    @property
    def name(self):
        """Get or set the primitive name."""
        return self._name

    @name.setter
    def name(self, name):
        self._name = valid_rad_string(name)

    @property
    def values(self):
        """Get or set the values of the current primitive as a dictionary.
        
        The keys of this dictionary should be integers between 0 and 2.

        Usage:

        .. code-block:: python

        # This will erase all values except the first line, which has 9 custom items
        primitive.values = [
            [0.5, 0.5, 0.5, "/usr/oakfloor.pic", ".", "frac(U)", "frac(V)", "-s", 1.1667],
            [],
            []
            ]
        """
        self._update_values()
        return self._values

    @values.setter
    def values(self, new_values):
        self._values  = list_with_length(new_values, 3, list, 'radiance primitive values')

    @property
    def modifier(self):
        """Get or set an object for the primitive modifier."""
        return self._modifier

    @modifier.setter
    def modifier(self, modifier):
        if not modifier or modifier == 'void':
            self._modifier = self.VOID
        else:
            try:
                assert modifier.is_modifier, \
                    'A {} cannot be a modifier. Modifiers must be materials, mixtures, ' \
                    'textures or patterns'.format(type(modifier))
            except AttributeError:
                raise TypeError('Invalid modifier: %s' % modifier)
            except AssertionError as e:
                raise AssertionError(e)
            else:
                self._modifier = modifier

    @property
    def dependencies(self):
        """Get list of dependencies for this primitive.
        
        Additional dependencies can be added with the add_dependent method.
        """
        return self._dependencies

    @property
    def is_geometry(self):
        """Get a boolean noting whether this object is a Radiance geometry."""
        return False

    @property
    def is_modifier(self):
        """Get a boolean indicating whether this object is a Radiance modifier.

        Modifiers include materials, mixtures, textures and patterns.
        """
        return self.type in self.MODIFIERTYPES

    @property
    def is_material(self):
        """Get a boolean noting whether this object is a material modifier."""
        return self.type in self.MATERIALTYPES

    @property
    def is_texture(self):
        """Get a boolean noting whether this object is a texture modifier."""
        return self.type in self.TEXTURETYPES

    @property
    def is_pattern(self):
        """Get a boolean noting whether this object is a pattern modifier."""
        return self.type in self.PATTERNTYPES

    @property
    def is_mixture(self):
        """Get a boolean noting whether this object is a mixture modifier."""
        return self.type in self.MIXTURETYPES

    @property
    def is_opaque(self):
        """Get or set a boolean to indicate whether this primitive is opaque.

        This property is used to separate opaque and non-opaque geometries as
        well as modifiers.
        """
        if self._is_opaque:  # opaque modifier
            return self._is_opaque
        elif self.type in self.NONEOPAQUETYPES:  # non-opaque modifier
            self._is_opaque = False
            return self._is_opaque
        else:  # it's a geometry or it has a void modifier; check the modifier
            return self.modifier.is_opaque

    @is_opaque.setter
    def is_opaque(self, is_opaque):
        self._is_opaque = bool(is_opaque)

    def _update_values(self):
        """update value dictionaries.

        _update_values must be implemented in each subclass.
        """
        pass

    def add_dependent(self, dep):
        """Add dependent."""
        assert isinstance(dep, Primitive), \
            '{} is not a valid dependent type'.format(type(dep))
        self._dependencies.append(dep)

    @staticmethod
    def _to_radiance(primitive, minimal=False):
        """Return Radiance representation of primitive."""
        header = "%s %s %s" % (primitive.modifier.name,
                               primitive.type, primitive.name)
        output = [header]
        for line_count in range(3):
            try:
                values = (str(v) for v in  primitive.values[line_count])
            except BaseException:
                values = []  # line will be displayed as 0
            else:
                count = len( primitive.values[line_count])
                line = '%d %s' % (count, ' '.join(values).rstrip()) if count else '0'
                output.append(line)

        return ' '.join(output) if minimal else '\n'.join(output)

    def to_radiance(self, minimal=False, include_modifier=True,
                    include_dependencies=True):
        """Return full radiance definition.
        
        Args:
            minimal: Boolean to note wehther the radiance string should be written
                in a minimal format (with spaces instead of line breaks). Default: False.
            include_modifier: Boolean to note whether the modifier of this primitive
                should be included in the string. Default: True.
            include_dependencies: Boolean to note whether the dependencies of this
                primitive should be included in the string. Default: True.
        """
        output = []

        if include_dependencies:
            for dep in self.dependencies:
                output.append(self._to_radiance(dep, minimal))

        if include_modifier and self.modifier.name != 'void':
            output.append(self._to_radiance(self.modifier, minimal))
        output.append(self._to_radiance(self, minimal))

        return '\n'.join(output)

    def to_dict(self):
        """Translate this object to a dictionary."""
        return {
            "modifier": self.modifier.to_dict(),
            "type": self.type,
            "name": self.name,
            "values": self.values,
            "dependencies": [dep.to_dict() for dep in self._dependencies]
        }

    def duplicate(self):
        """Get a copy of this object."""
        return self.__copy__()

    @staticmethod
    def filter_dict_input(input_dict):
        """Filter a dictionary of a Primitive to get modifier and dependency modules."""
        try:  # ensure the putil module is imported, which imports all primitive modules
            putil
        except NameError:
            import honeybee_radiance.putil as putil

        # try to get modifier
        if input_dict['modifier'] == 'void':
            modifier = 'void'
        else:
            modifier = putil.dict_to_primitive(input_dict['modifier'])

        if 'dependencies' not in input_dict: 
            dependencies = []
        else:
            dependencies = [
                putil.dict_to_primitive(dep) for dep in input_dict['dependencies']
            ]

        return modifier, dependencies

    def __key(self):
        """A tuple based on the object properties, useful for hashing."""
        return (hash(self.modifier), self.type, self.name) + \
            tuple(hash(tuple(vals)) for vals in self.values) + \
            tuple(hash(dep) for dep in self._dependencies)

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        return isinstance(other, self.__class__) and \
            self.__key() == other.__key()

    def __ne__(self, other):
        return not self.__eq__(other)

    def __copy__(self):
        mod, depend = self._dup_mod_and_depend()
        values_copy = [copy(line) for line in self._values]
        return self.__class__(self.name, mod, values_copy, self._is_opaque, depend)
    
    def _dup_mod_and_depend(self):
        """Duplicate this object's modifer and its dependencies."""
        mod = None if isinstance(self._modifier, Void) else self._modifier.duplicate()
        dependencies = [dep.duplicate() for dep in self._dependencies]
        return mod, dependencies

    def ToString(self):
        """Overwrite .NET ToString."""
        return self.__repr__()

    def __repr__(self):
        """Return primitive definition."""
        return self.to_radiance()
