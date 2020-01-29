"""Radiance Ring.

http://radsite.lbl.gov/radiance/refer/ray.html#Ring
"""
from .geometrybase import Geometry
import honeybee.typing as typing


class Ring(Geometry):
    """Radiance Ring.

    A ring is a circular disk given by its center, surface normal, and inner and outer
    radii:

        mod ring id
        0
        0
        8
                xcent   ycent   zcent
                xdir    ydir    zdir
                r0      r1

    """
    __slots__ = ('_center_pt', '_normal_vector', '_radius_inner', '_radius_outer')

    def __init__(self, name, center_pt=None, normal_vector=None, radius_inner=5,
                 radius_outer=10, modifier=None, dependencies=None):
        """Radiance Ring.

        Args:
            name: Geometry name as a string. Do not use white space or special
                character.
            center_pt: Ring start center point as (x, y, z) (Default: (0, 0 ,0)).
            normal_vector: Surface normal as (x, y, z) (Default: (0, 0 ,1)).
            radius_inner: Ring inner radius as a number (Default: 5).
            radius_outer: Ring outer radius as a number (Default: 10).
            modifier: Geometry modifier (Default: "void").
            dependencies: A list of primitives that this primitive depends on. This
                argument is only useful for defining advanced primitives where the
                primitive is defined based on other primitives. (Default: [])
        """
        Geometry.__init__(self, name, modifier=modifier)
        self.center_pt = center_pt or (0, 0, 0)
        self.normal_vector = normal_vector or (0, 0, 1)
        self.radius_inner = radius_inner if radius_inner is not None else 5
        self.radius_outer = radius_outer if radius_outer is not None else 10

        self._update_values()

    def _update_values(self):
        """update value dictionaries."""
        self._values[2] = \
            [self.center_pt[0], self.center_pt[1], self.center_pt[2],
             self.normal_vector[0], self.normal_vector[1], self.normal_vector[2],
             self.radius_inner, self.radius_outer]

    @property
    def center_pt(self):
        """Ring start center point as (x, y, z) (Default: (0, 0 ,0))."""
        return self._center_pt

    @center_pt.setter
    def center_pt(self, value):
        self._center_pt = tuple(float(v) for v in value)
        assert len(self._center_pt) == 3, \
            'Radiance Ring center point must have 3 values for (x, y, z).'

    @property
    def radius_inner(self):
        """Ring inner radius as a number (Default: 5)."""
        return self._radius_inner

    @radius_inner.setter
    def radius_inner(self, value):
        self._radius_inner = typing.float_positive(value)

    @property
    def normal_vector(self):
        """Surface normal as (x, y, z) (Default: (0, 0 ,1))."""
        return self._normal_vector

    @normal_vector.setter
    def normal_vector(self, value):
        self._normal_vector = tuple(float(v) for v in value)
        assert len(self._center_pt) == 3, \
            'Radiance Ring normal venctor must have 3 values for (x, y, z).'

    @property
    def radius_outer(self):
        """Ring outer radius as a number (Default: 10)."""
        return self._radius_outer

    @radius_outer.setter
    def radius_outer(self, value):
        self._radius_outer = typing.float_positive(value)

    @classmethod
    def from_primitive_dict(cls, primitive_dict):
        """Initialize a Ring from a primitive dict.

        Args:
            data: A dictionary in the format below.

            .. code-block:: python

            {
                "modifier": "", // primitive modifier (Default: "void")
                "type": "ring", // primitive type
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
            center_pt=values[0:3],
            normal_vector=values[3:6],
            radius_inner=values[6],
            radius_outer=values[7],
            modifier=modifier,
            dependencies=dependencies
        )
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
                "type": "ring", // Geometry type
                "modifier": {} or "void",
                "name": "", // Geometry Name
                "center_pt": (0, 0, 0),
                "normal_vector": (0, 0, 1),
                "radius_inner": float,
                "radius_outer": float,
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
                   center_pt=(data["center_pt"]),
                   radius_inner=data["radius_inner"],
                   normal_vector=(data["normal_vector"]),
                   radius_outer=data["radius_outer"],
                   modifier=modifier,
                   dependencies=dependencies)

    def to_dict(self):
        """Translate this object to a dictionary."""
        return {
            "modifier": self.modifier.to_dict(),
            "type": self.__class__.__name__.lower(),
            "name": self.name,
            "center_pt": self.center_pt,
            "normal_vector": self.normal_vector,
            "radius_inner": self.radius_inner,
            "radius_outer": self.radius_outer,
            'dependencies': [dp.to_dict() for dp in self.dependencies]
        }

    def __copy__(self):
        mod, depend = self._dup_mod_and_depend()
        return self.__class__(
            self.name, self.center_pt, self.normal_vector, self.radius_inner,
            self.radius_outer, mod, depend)
