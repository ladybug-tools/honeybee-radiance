"""Radiance Cylinder.

http://radsite.lbl.gov/radiance/refer/ray.html#Cylinder
"""
from .geometrybase import Geometry
import honeybee.typing as typing


class Cylinder(Geometry):
    """Radiance Cylinder.

    A cylinder is like a cone, but its starting and ending radii are equal.

        mod cylinder id
        0
        0
        7
                x0      y0      z0
                x1      y1      z1
                rad
    """
    __slots__ = ('_center_pt_start', '_center_pt_end', '_radius')

    def __init__(self, name, center_pt_start=None, center_pt_end=None, radius=10,
                 modifier=None, dependencies=None):
        """Radiance Cylinder.

        Args:
            name: Geometry name as a string. Do not use white spaces or special
                characters.
            center_pt_start: Cylinder start center point as (x, y, z)
                (Default: (0, 0 ,0)).
            center_pt_end: Cylinder end center point as (x, y, z) (Default: (0, 0 ,10)).
            radius: Cylinder start radius as a number (Default: 10).
            modifier: Geometry modifier (Default: "void").
            dependencies: A list of primitives that this primitive depends on. This
                argument is only useful for defining advanced primitives where the
                primitive is defined based on other primitives. (Default: [])
        """
        Geometry.__init__(self, name, modifier=modifier, dependencies=dependencies)
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
        """Cone start center point as (x, y, z) (Default: (0, 0 ,0))."""
        return self._center_pt_start
    
    @center_pt_start.setter
    def center_pt_start(self, value):
        self._center_pt_start = tuple(float(v) for v in value)
        assert len(self._center_pt_start) == 3, \
            'Radiance Cylinder center point must have 3 values for (x, y, z).'

    @property
    def radius(self):
        """Cone start radius as a number (Default: 10)."""
        return self._radius
    
    @radius.setter
    def radius(self, value):
        self._radius = typing.float_positive(value)

    @property
    def center_pt_end(self):
        """Cone end center point as (x, y, z) (Default: (0, 0 ,10))."""
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
                "modifier": "", // primitive modifier (Default: "void")
                "type": "cylinder", // primitive type
                "name": "", // primitive name
                "values": [] // values,
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
            name=primitive_dict['name'],
            center_pt_start=values[0:3],
            center_pt_end=values[3:6],
            radius=values[6],
            modifier=modifier,
            dependencies=dependencies
        )
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
                "type": "cylinder", // Geometry type
                "modifier": {} or "void",
                "name": "", // Geometry Name
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

        return cls(name=data["name"],
                   center_pt_start=(data["center_pt_start"]),
                   center_pt_end=(data["center_pt_end"]),
                   radius=data["radius"],
                   modifier=modifier,
                   dependencies=dependencies)

    def to_dict(self):
        """Translate this object to a dictionary."""
        return {
            "modifier": self.modifier.to_dict(),
            "type": self.__class__.__name__.lower(),
            "name": self.name,
            "center_pt_start": self.center_pt_start,
            "radius": self.radius,
            "center_pt_end": self.center_pt_end,
            'dependencies': [dp.to_dict() for dp in self.dependencies]
        }

    def __copy__(self):
        mod, depend = self._dup_mod_and_depend()
        return self.__class__(self.name, self.center_pt_start, self.center_pt_end,
                              self.radius, mod, depend)
