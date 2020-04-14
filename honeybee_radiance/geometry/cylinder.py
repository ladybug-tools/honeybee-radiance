"""Radiance Cylinder.

http://radsite.lbl.gov/radiance/refer/ray.html#Cylinder
"""
from .geometrybase import Geometry
import honeybee.typing as typing


class Cylinder(Geometry):
    """Radiance Cylinder.

    A cylinder is like a cone, but its starting and ending radii are equal.

    .. code-block:: shell

        mod cylinder id
        0
        0
        7
                x0      y0      z0
                x1      y1      z1
                rad

    Args:
        identifier: Text string for a unique Geometry ID. Must not contain spaces
            or special characters. This will be used to identify the object across
            a model and in the exported Radiance files.
        center_pt_start: Cylinder start center point as (x, y, z)
            (Default: (0, 0 ,0)).
        center_pt_end: Cylinder end center point as (x, y, z) (Default: (0, 0 ,10)).
        radius: Cylinder start radius as a number (Default: 10).
        modifier: Geometry modifier (Default: None).
        dependencies: A list of primitives that this primitive depends on. This
            argument is only useful for defining advanced primitives where the
            primitive is defined based on other primitives. (Default: [])

    Properties:
        * identifier
        * display_name
        * center_pt_start
        * center_pt_end
        * radius
        * values
        * modifier
        * dependencies
    """
    __slots__ = ('_center_pt_start', '_center_pt_end', '_radius')

    def __init__(self, identifier, center_pt_start=None, center_pt_end=None, radius=10,
                 modifier=None, dependencies=None):
        """Radiance Cylinder."""
        Geometry.__init__(self, identifier, modifier=modifier, dependencies=dependencies)
        self.center_pt_start = center_pt_start or (0, 0, 0)
        self.center_pt_end = center_pt_end or (0, 0, 10)
        self.radius = radius if radius is not None else 10
        self._update_values()

    def _update_values(self):
        """update value dictionaries."""
        self._values[2] = \
            [self.center_pt_start[0], self.center_pt_start[1], self.center_pt_start[2],
             self.center_pt_end[0], self.center_pt_end[1], self.center_pt_end[2],
             self.radius]

    @property
    def center_pt_start(self):
        """Cone start center point as (x, y, z). Default is (0, 0 ,0)."""
        return self._center_pt_start

    @center_pt_start.setter
    def center_pt_start(self, value):
        self._center_pt_start = tuple(float(v) for v in value)
        assert len(self._center_pt_start) == 3, \
            'Radiance Cylinder center point must have 3 values for (x, y, z).'

    @property
    def radius(self):
        """Cone start radius as a number. Default is 10."""
        return self._radius

    @radius.setter
    def radius(self, value):
        self._radius = typing.float_positive(value)

    @property
    def center_pt_end(self):
        """Cone end center point as (x, y, z), Default is (0, 0 ,10)."""
        return self._center_pt_end

    @center_pt_end.setter
    def center_pt_end(self, value):
        self._center_pt_end = tuple(float(v) for v in value)
        assert len(self._center_pt_end) == 3, \
            'Radiance Cylinder center point must have 3 values for (x, y, z).'

    @classmethod
    def from_primitive_dict(cls, primitive_dict):
        """Initialize a Cylinder from a primitive dict.

        Args:
            data: A dictionary in the format below.

        .. code-block:: python

            {
            "modifier": {},  # primitive modifier (Default: None)
            "type": "cylinder",  # primitive type
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
            center_pt_end=values[3:6],
            radius=values[6],
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
        """Initialize a Cylinder from a dictionary.

        Args:
            data: A dictionary in the format below.

        .. code-block:: python

            {
            "type": "cylinder",  # Geometry type
            "modifier": {} ,
            "identifier": "",  # Geometry identifer
            "display_name": "",  # Geometry display name
            "center_pt_start": (0, 0, 0),
            "center_pt_end": (0, 0, 10),
            "radius": float,
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
                      center_pt_end=(data["center_pt_end"]),
                      radius=data["radius"],
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
            "center_pt_start": self.center_pt_start,
            "radius": self.radius,
            "center_pt_end": self.center_pt_end,
            'dependencies': [dp.to_dict() for dp in self.dependencies]
        }
        if self._display_name is not None:
            base['display_name'] = self.display_name
        return base

    def __copy__(self):
        mod, depend = self._dup_mod_and_depend()
        new_obj = self.__class__(
            self.identifier, self.center_pt_start, self.center_pt_end, self.radius,
            mod, depend)
        new_obj._display_name = self._display_name
        return new_obj
