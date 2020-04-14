"""Radiance Source.

http://radsite.lbl.gov/radiance/refer/ray.html#Source
"""
from .geometrybase import Geometry
import honeybee.typing as typing


class Source(Geometry):
    """Radiance Source.

    A source is not really a surface, but a solid angle. It is used for specifying light
    sources that are very distant. The direction to the center of the source and the
    number of degrees subtended by its disk are given as follows:

    .. code-block:: shell

        mod source id
        0
        0
        4 xdir ydir zdir angle

    Args:
        identifier: Text string for a unique Geometry ID. Must not contain spaces
            or special characters. This will be used to identify the object across
            a model and in the exported Radiance files.
        direction: A vector to set source direction (x, y, z) (Default: (0, 0 ,-1)).
        angle: Source solid angle (Default: 0.533).
        modifier: Geometry modifier (Default: None).
        dependencies: A list of primitives that this primitive depends on. This
            argument is only useful for defining advanced primitives where the
            primitive is defined based on other primitives. (Default: [])

    Properties:
        * identifier
        * display_name
        * direction
        * angle
        * modifier
        * dependencies
        * values

    Usage:

    .. code-block:: python

        source = Source("test_source", (0, 0, 10), 10)
        print(source)
    """
    __slots__ = ('_direction', '_angle')

    def __init__(self, identifier, direction=None, angle=0.533, modifier=None,
                 dependencies=None):
        """Radiance Source."""
        Geometry.__init__(self, identifier, modifier=modifier, dependencies=dependencies)
        self.direction = direction or (0, 0, -1)
        self.angle = angle if angle is not None else 0.533

        self._update_values()

    def _update_values(self):
        """update values dictionary."""
        self._values[2] = \
            [self.direction[0], self.direction[1], self.direction[2], self.angle]

    @property
    def direction(self):
        """A vector to set source direction (x, y, z) (Default is (0, 0 ,-1))."""
        return self._direction

    @direction.setter
    def direction(self, value):
        self._direction = tuple(float(v) for v in value)
        assert len(self._direction) == 3, \
            'Radiance Source direction must have 3 values for (x, y, z).'

    @property
    def angle(self):
        """Source solid angle. Default is 0.533."""
        return self._angle

    @angle.setter
    def angle(self, value):
        self._angle = typing.float_positive(value)

    @classmethod
    def from_primitive_dict(cls, primitive_dict):
        """Initialize a Source from a primitive dict.

        Args:
            data: A dictionary in the format below.

        .. code-block:: python

            {
            "modifier": {},  # primitive modifier (Default: None)
            "type": "source",  # primitive type
            "identifier": "",  # primitive identifier
            "display_name": "",  # primitive display name
            "values": [],  # values
            "dependencies": []
            }
        """
        assert 'type' in primitive_dict, 'Input dictionary is missing "type".'
        if primitive_dict['type'] != cls.__name__.lower():
            raise ValueError(
                'Type must be %s not %s.' % (cls.__name__.lower(), primitive_dict['type'])
            )

        modifier, dependencies = cls.filter_dict_input(primitive_dict)
        values = primitive_dict['values'][2]

        cls_ = cls(
            identifier=primitive_dict['identifier'],
            direction=values[0:3],
            angle=values[3],
            modifier=modifier,
            dependencies=dependencies
        )
        if 'display_name' in primitive_dict and primitive_dict['display_name'] is not None:
            cls_.display_name = primitive_dict['display_name']

        # this might look redundant but it is NOT. see glass for explanation.
        cls_.values = primitive_dict['values']
        return cls_

    @classmethod
    def from_dict(cls, data):
        """Initialize a Ring from a dictionary.

        Args:
            data: A dictionary in the format below.

        .. code-block:: python

            {
            "type": "source",  # Geometry type
            "modifier": {} ,
            "identifier": "",  # Geometry identifier
            "display_name": "",  # Geometry display name
            "direction": {"x": float, "y": float, "z": float},
            "angle": float,
            "dependencies": []
            }
        """
        assert 'type' in data, 'Input dictionary is missing "type".'
        if data['type'] != cls.__name__.lower():
            raise ValueError(
                'Type must be %s not %s.' % (cls.__name__.lower(),
                    data['type'])
            )
        modifier, dependencies = cls.filter_dict_input(data)

        new_obj = cls(identifier=data["identifier"],
                      direction=(data["direction"]),
                      angle=data["angle"],
                      modifier=modifier,
                      dependencies=dependencies)
        if 'display_name' in data and data['display_name'] is not None:
            new_obj.display_name = data['display_name']
        return new_obj

    def to_dict(self):
        """Translate this object to a dictionary."""
        base = {
            "modifier": self.modifier.to_dict(),
            "type": self.__class__.__name__.lower(),
            "identifier": self.identifier,
            "direction": self.direction,
            "angle": self.angle,
            'dependencies': [dp.to_dict() for dp in self.dependencies]
        }
        if self._display_name is not None:
            base['display_name'] = self.display_name
        return base

    def __copy__(self):
        mod, depend = self._dup_mod_and_depend()
        new_obj = self.__class__(
            self.identifier, self.direction, self.angle, mod, depend)
        new_obj._display_name = self._display_name
        return new_obj
