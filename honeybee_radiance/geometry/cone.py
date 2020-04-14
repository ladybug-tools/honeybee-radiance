"""Radiance Cone.

http://radsite.lbl.gov/radiance/refer/ray.html#Cone
"""
from .geometrybase import Geometry
import honeybee.typing as typing


class Cone(Geometry):
    """Radiance Cone.

    A cone is a megaphone-shaped object. It is truncated by two planes perpendicular to
    its axis, and one of its ends may come to a point. It is given as two axis endpoints,
    and the starting and ending radii:

    .. code-block:: shell

        mod cone id
        0
        0
        8
                x0      y0      z0
                x1      y1      z1
                r0      r1

    Args:
        identifier: Text string for a unique Geometry ID. Must not contain spaces
            or special characters. This will be used to identify the object across
            a model and in the exported Radiance files.
        center_pt_start: Cone start center point as (x, y, z) (Default: (0, 0 ,0)).
        radius_start: Cone start radius as a number (Default: 10).
        center_pt_end: Cone end center point as (x, y, z) (Default: (0, 0 ,10)).
        radius_end: Cone end radius as a number (Default: 0).
        modifier: Geometry modifier (Default: None).
        dependencies: A list of primitives that this primitive depends on. This
            argument is only useful for defining advanced primitives where the
            primitive is defined based on other primitives. (Default: [])

    Properties:
        * identifier
        * display_name
        * center_pt_start
        * radius_start
        * center_pt_end
        * radius_end
        * values
        * modifier
        * dependencies

    """
    __slots__ = ('_center_pt_start', '_radius_start', '_center_pt_end', '_radius_end')

    def __init__(self, identifier, center_pt_start=None, radius_start=10,
                 center_pt_end=None, radius_end=0, modifier=None, dependencies=None):
        """Radiance Cone."""
        Geometry.__init__(self, identifier, modifier=modifier, dependencies=dependencies)
        self.center_pt_start = center_pt_start or (0, 0, 0)
        self.radius_start = radius_start if radius_start is not None else 10
        self.center_pt_end = center_pt_end or (0, 0, 10)
        self.radius_end = radius_end if radius_end is not None else 0
        self._update_values()

    def _update_values(self):
        """update value dictionaries."""
        self._values[2] = \
            [self.center_pt_start[0], self.center_pt_start[1], self.center_pt_start[2],
             self.center_pt_end[0], self.center_pt_end[1], self.center_pt_end[2],
             self.radius_start, self.radius_end]

    @property
    def center_pt_start(self):
        """Cone start center point as (x, y, z). Default is (0, 0 ,0)."""
        return self._center_pt_start

    @center_pt_start.setter
    def center_pt_start(self, value):
        self._center_pt_start = tuple(float(v) for v in value)
        assert len(self._center_pt_start) == 3, \
            'Radiance Cone center point must have 3 values for (x, y, z).'

    @property
    def radius_start(self):
        """Cone start radius as a number. Default is 10."""
        return self._radius_start

    @radius_start.setter
    def radius_start(self, value):
        self._radius_start = typing.float_positive(value)

    @property
    def center_pt_end(self):
        """Cone end center point as (x, y, z). Default is (0, 0 ,10)."""
        return self._center_pt_end

    @center_pt_end.setter
    def center_pt_end(self, value):
        self._center_pt_end = tuple(float(v) for v in value)
        assert len(self._center_pt_end) == 3, \
            'Radiance Cone center point must have 3 values for (x, y, z).'

    @property
    def radius_end(self):
        """ Cone end radius as a number. Default is 0."""
        return self._radius_end

    @radius_end.setter
    def radius_end(self, value):
        self._radius_end = typing.float_positive(value)

    @classmethod
    def from_primitive_dict(cls, primitive_dict):
        """Initialize a Cone from a primitive dict.

        Args:
            data: A dictionary in the format below.

        .. code-block:: python

            {
            "modifier": {},  # primitive modifier (Default: None)
            "type": "cone",  # primitive type
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
            center_pt_start=values[0:3],
            radius_start=values[6],
            center_pt_end=values[3:6],
            radius_end=values[7],
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
        """Initialize a Cone from a dictionary.

        Args:
            data: A dictionary in the format below.

        .. code-block:: python

            {
            "type": "cone",  # Geometry type
            "modifier": {} ,
            "identifier": "",  # Geometry identifer
            "display_name": "",  # Geometry display name
            "center_pt_start": (0, 0, 0),
            "radius_start": float,
            "center_pt_end": (0, 0, 10),
            "radius_end": float,
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
                      center_pt_start=(data["center_pt_start"]),
                      radius_start=data["radius_start"],
                      center_pt_end=( data["center_pt_end"]),
                      radius_end=data["radius_end"],
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
            "radius_start": self.radius_start,
            "center_pt_start": self.center_pt_start,
            "radius_end": self.radius_end,
            "center_pt_end": self.center_pt_end,
            'dependencies': [dp.to_dict() for dp in self.dependencies]
        }
        if self._display_name is not None:
            base['display_name'] = self.display_name
        return base

    def __copy__(self):
        mod, depend = self._dup_mod_and_depend()
        new_obj = self.__class__(
            self.identifier, self.center_pt_start, self.radius_start, self.center_pt_end,
            self.radius_end, mod, depend)
        new_obj._display_name = self._display_name
        return new_obj
