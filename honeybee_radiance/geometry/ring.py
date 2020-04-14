"""Radiance Ring.

http://radsite.lbl.gov/radiance/refer/ray.html#Ring
"""
from .geometrybase import Geometry
import honeybee.typing as typing


class Ring(Geometry):
    """Radiance Ring.

    A ring is a circular disk given by its center, surface normal, and inner and outer
    radii:

    .. code-block:: shell

        mod ring id
        0
        0
        8
                xcent   ycent   zcent
                xdir    ydir    zdir
                r0      r1

    Args:
        identifier: Text string for a unique Geometry ID. Must not contain spaces
            or special characters. This will be used to identify the object across
            a model and in the exported Radiance files.
        center_pt: Ring start center point as (x, y, z) (Default: (0, 0 ,0)).
        normal_vector: Surface normal as (x, y, z) (Default: (0, 0 ,1)).
        radius_inner: Ring inner radius as a number (Default: 5).
        radius_outer: Ring outer radius as a number (Default: 10).
        modifier: Geometry modifier (Default: None).
        dependencies: A list of primitives that this primitive depends on. This
            argument is only useful for defining advanced primitives where the
            primitive is defined based on other primitives. (Default: [])

    Properties:
        * identifier
        * display_name
        * center_pt
        * normal_vector
        * radius_inner
        * radius_outer
        * modifier
        * dependencies
        * values
    """
    __slots__ = ('_center_pt', '_normal_vector', '_radius_inner', '_radius_outer')

    def __init__(self, identifier, center_pt=None, normal_vector=None, radius_inner=5,
                 radius_outer=10, modifier=None, dependencies=None):
        """Radiance Ring."""
        Geometry.__init__(self, identifier, modifier=modifier)
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
        """Ring start center point as (x, y, z). Default is (0, 0 ,0)."""
        return self._center_pt

    @center_pt.setter
    def center_pt(self, value):
        self._center_pt = tuple(float(v) for v in value)
        assert len(self._center_pt) == 3, \
            'Radiance Ring center point must have 3 values for (x, y, z).'

    @property
    def radius_inner(self):
        """Ring inner radius as a number (Default is 5)."""
        return self._radius_inner

    @radius_inner.setter
    def radius_inner(self, value):
        self._radius_inner = typing.float_positive(value)

    @property
    def normal_vector(self):
        """Surface normal as (x, y, z) (Default is (0, 0 ,1))."""
        return self._normal_vector

    @normal_vector.setter
    def normal_vector(self, value):
        self._normal_vector = tuple(float(v) for v in value)
        assert len(self._center_pt) == 3, \
            'Radiance Ring normal venctor must have 3 values for (x, y, z).'

    @property
    def radius_outer(self):
        """Ring outer radius as a number (Default is 10)."""
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
            "modifier": {},  # primitive modifier (Default: None)
            "type": "ring",  # primitive type
            "identifier": "",  # primitive identifier
            "display_name": "",  # primitive display name
            "values": []  # values,
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
            center_pt=values[0:3],
            normal_vector=values[3:6],
            radius_inner=values[6],
            radius_outer=values[7],
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
            "type": "ring",  # Geometry type
            "modifier": {} ,
            "identifier": "",  # Geometry identifier
            "display_name": "",  # Geometry display name
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

        new_obj = cls(identifier=data["identifier"],
                      center_pt=(data["center_pt"]),
                      radius_inner=data["radius_inner"],
                      normal_vector=(data["normal_vector"]),
                      radius_outer=data["radius_outer"],
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
            "center_pt": self.center_pt,
            "normal_vector": self.normal_vector,
            "radius_inner": self.radius_inner,
            "radius_outer": self.radius_outer,
            'dependencies': [dp.to_dict() for dp in self.dependencies]
        }
        if self._display_name is not None:
            base['display_name'] = self.display_name
        return base

    def __copy__(self):
        mod, depend = self._dup_mod_and_depend()
        new_obj = self.__class__(
            self.identifier, self.center_pt, self.normal_vector, self.radius_inner,
            self.radius_outer, mod, depend)
        new_obj._display_name = self._display_name
        return new_obj
