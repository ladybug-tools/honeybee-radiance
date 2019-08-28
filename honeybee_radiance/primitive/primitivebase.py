"""Base class for Radiance Primitives.

Unless you are a developer you most likely want to use one of the subclasses of
Primitive instead of using this class directly. Look under honeybee.radiance.material
and honeybee.radiance.geometry

http://radsite.lbl.gov/radiance/refer/ray.html
"""
import honeybee.typing as typing
from honeybee_radiance.parser import string_to_dicts


class Void(object):
    """Void modifier."""
    __slots__ = ()

    @property
    def name(self):
        """Void."""
        return 'void'

    @property
    def can_be_modifier(self):
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


class Primitive(object):
    """Base class for Radiance Primitives."""

    # list of Radiance material types
    MATERIALTYPES = \
        set(('plastic', 'glass', 'trans', 'metal', 'mirror', 'illum',
             'mixedfunc', 'dielectric', 'transdata', 'light', 'glow', 'BSDF',
             'void', 'spotlight', 'prism1', 'prism2', 'mist', 'plastic2',
             'metal2', 'trans2', 'ashik2', 'dielectric', 'interface',
             'plasfunc', 'metfunc', 'transfunc', 'BRTDfunc',
             'plasdata', 'metdata', 'transdata', 'antimatter'))

    TEXTURETYPES = set(('texfunc', 'texdata'))

    # list of Radiance geometry types
    GEOMETRYTYPES = set(('source', 'sphere', 'bubble', 'polygon', 'cone', 'cup',
                         'cylinder', 'tube', 'ring', 'instance', 'mesh'))

    PATTERNTYPES = set(('colorfunc', 'brightfunc', 'colordata', 'brightdata',
                        'colorpict', 'colortext', 'brighttext'))

    MIXTURETYPES = set(('mixfunc', 'mixdata', 'mixpict', 'mixtext'))

    TYPES = set().union(MATERIALTYPES, TEXTURETYPES, GEOMETRYTYPES, PATTERNTYPES,
                        MIXTURETYPES)

    # Materials, mixtures, textures or patterns
    MODIFIERTYPES = set().union(MATERIALTYPES, MIXTURETYPES, TEXTURETYPES, PATTERNTYPES)
    # Materials that are not usually opaque. This will be used to set is_opaque property
    # is it's not provided by user and can be overwritten by setting the value for
    # is_opaque
    NONEOPAQUETYPES = set(('glass', 'trans', 'trans2', 'transdata', 'transfunc',
                           'dielectric', 'BSDF', 'mixfunc', 'BRTDfunc', 'mist',
                           'prism1', 'prism2'))

    VOID = Void()

    def __init__(self, name, modifier=None, values=None, is_opaque=None,
                 dependencies=None):
        """Create primitive base.

        args:
            name: Primitive name as a string. Do not use white space or special
                characters.
            type: One of Radiance standard Primitive types (e.g. glass, plastic, etc)
            modifier: Modifier. It can be primitive, mixture, texture or pattern.
                (Default: "void").
            values: A dictionary of primitive data. key is line number and item is the
                list of values {0: [], 1: [], 2: ['0.500', '0.500', '0.500', '0.000',
                '0.050']}
            dependencies: A list of primitives that this primitive depends on. This
                argument is only useful for defining advanced primitives where the
                primitive is defined based on other primitives. (Default: [])

        """
        self.name = name
        self.type = self.__class__.__name__.lower()
        self.modifier = modifier
        self.values = values or {0: [], 1: [], 2: []}
        self._is_opaque = is_opaque
        self._dependencies = []
        dependencies = dependencies or []
        for dep in dependencies:
            self.add_dependent(dep)

    @classmethod
    def from_string(cls, primitive_string):
        """Create a Radiance primitive from a string.

        If the primitive modifier is not void or it has other dependencies the dependency
        must also be part of the input string.
        """
        pr_dict = string_to_dicts(primitive_string)
        assert len(
            pr_dict) == 1, 'Input string includes more than one Radiance objects.'
        return cls.from_values(pr_dict[0])

    @classmethod
    def from_values(cls, values_dict):
        """Make a radiance primitive from value dict.

        This dictionary structure is unique for all radiance primitives while from_dict
        classmethod accepts a different schema based on subclass properties.

        {
            "modifier": "", // primitive modifier (Default: "void")
            "type": "", // primitive type
            "name": "", // primitive Name
            "values": {} // values,
            "dependencies": []
        }
        """
        modifier, dependencies = cls.filter_dict_input(values_dict)

        cls_ = cls(
            name=values_dict['name'],
            modifier=modifier,
            values=values_dict['values'],
            dependencies=dependencies
        )

        if cls_.type == 'primitive':
            cls_.type = values_dict['type']

        return cls_

    @classmethod
    def from_dict(cls, inp_dict):
        """Make radiance primitive from dict
        {
            "modifier": "", // primitive modifier (Default: "void")
            "type": "custom", // primitive type
            "name": "", // primitive Name
            "values": {} // values,
            "dependencies": []
        }
        """
        return cls.from_values(inp_dict)

    @property
    def values(self):
        self._update_values()
        return self._values

    @values.setter
    def values(self, new_values):
        """Modify values for the current primitive.

        Args:
           new_values: New values as a dictionary. The keys should be between 0 and 2.

         Usage:
            # This line will assign 9 values to line 0 of the primitive
            primitive.values = {0: ["0.5", "0.5", "0.5",
                "/usr/local/lib/ray/oakfloor.pic", ".", "frac(U)",
                "frac(V)", "-s", "1.1667"]}
        """
        self._values = {}
        for line_count, value in new_values.items():
            assert 0 <= line_count <= 2, ValueError(
                'Illegal input: {}. Key values must be between 0-2.'.format(
                    line_count)
            )
            self._values[line_count] = value

    @property
    def dependencies(self):
        """Get list of dependencies."""
        return self._dependencies

    @property
    def is_radiance_primitive(self):
        """Indicate that this object is a Radiance primitive."""
        return True

    @property
    def is_radiance_geometry(self):
        """Indicate if this object is a Radiance geometry."""
        return False

    @property
    def is_radiance_texture(self):
        """Indicate if this object is a Radiance geometry."""
        return False

    @property
    def is_radiance_pattern(self):
        """Indicate if this object is a Radiance geometry."""
        return False

    @property
    def is_radiance_mixture(self):
        """Indicate if this object is a Radiance geometry."""
        return False

    @property
    def is_radiance_material(self):
        """Indicate if this object is a Radiance material."""
        return False

    @property
    def can_be_modifier(self):
        """Indicate if this object can be a modifier.

        Materials, mixtures, textures or patterns can be modifiers.
        """
        return self.type in self.MODIFIERTYPES

    @property
    def name(self):
        """Get/set primitive name."""
        return self._name

    @name.setter
    def name(self, name):
        self._name = typing.valid_string(name)

    @property
    def modifier(self):
        """Get/set primitive modifier."""
        return self._modifier

    @modifier.setter
    def modifier(self, modifier):
        if not modifier or modifier == 'void':
            self._modifier = self.VOID
        else:
            try:
                assert modifier.can_be_modifier, \
                    'A {} cannot be a modifier. Modifiers can be Materials, mixtures, ' \
                    'textures or patterns'.format(type(modifier))
            except AttributeError:
                raise TypeError('Invalid modifier: %s' % modifier)
            except AssertionError as e:
                raise AssertionError(e)
            else:
                self._modifier = modifier

    @property
    def type(self):
        """Get/set primitive type."""
        return self._type

    @type.setter
    def type(self, type):
        _mapper = {'bsdf': 'BSDF', 'brtdfunc': 'BRTDfunc'}

        if type != 'primitive':
            if type not in self.TYPES:
                # try base classes for subclasses
                for base in self.__class__.__mro__:
                    if base.__name__.lower() in _mapper:
                        type = _mapper[base.__name__.lower()]
                        break
                    if base.__name__.lower() in self.TYPES:
                        type = base.__name__.lower()
                        break

            assert type in self.TYPES, \
                "%s is not a supported Radiance primitive type." % type + \
                "Try one of these primitives:\n%s" % str(self.TYPES)

        self._type = type

    @property
    def is_opaque(self):
        """Indicate if the primitive is opaque.

        This property is used to separate opaque and non-opaque surfaces.
        """
        if self._is_opaque:
            return self._is_opaque
        elif self.type in self.NONEOPAQUETYPES:
            # none opaque material
            self._is_opaque = False
            return self._is_opaque
        else:
            # check modifier for surfaces
            return self.modifier.is_opaque

    @is_opaque.setter
    def is_opaque(self, is_opaque):
        self._is_opaque = bool(is_opaque)

    def _update_values(self):
        """update value dictionaries.

        _update_values must be implemented in subclasses.
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
                values = []  # line will be printed as 0
            else:
                count = len( primitive.values[line_count])
                line = '%d %s' % (count, ' '.join(values).rstrip()) if count else '0'
                output.append(line)

        return ' '.join(output) if minimal else '\n'.join(output)

    # TODO: add string format for float values
    def to_radiance(self, minimal=False, include_modifier=True,
            include_dependencies=True):
        """Return full radiance definition."""
        output = []

        if include_dependencies:
            for dep in self.dependencies:
                output.append(self._to_radiance(dep, minimal))

        if include_modifier and self.modifier.name != 'void':
            output.append(self._to_radiance(self.modifier, minimal))
        output.append(self._to_radiance(self, minimal))

        return '\n'.join(output)

    # TODO: make it consistent with radiance-energy implementation
    def to_dict(self):
        """Translate radiance primitive to json
        {
            "modifier": "", // primitive modifier (Default: "void")
            "type": "", // primitive type
            "name": "", // primitive Name
            "values": {} // values
        }
        """
        return {
            "modifier": self.modifier.to_dict(),
            "type": self.type,
            "name": self.name,
            "values": self.values,
            "dependencies": [dep.to_dict() for dep in self._dependencies]
        }

    @staticmethod
    def filter_dict_input(input_dict):
        try:
            putil
        except NameError:
            import honeybee_radiance.primitive.putil as putil
        
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

    def ToString(self):
        """Overwrite .NET ToString."""
        return self.__repr__()

    def __repr__(self):
        """Return primitive definition."""
        return self.to_radiance()
