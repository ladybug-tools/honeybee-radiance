"""Radiance Ring.

http://radsite.lbl.gov/radiance/refer/ray.html#Ring
"""
from .geometrybase import Geometry
import ladybug_geometry.geometry3d.pointvector as pv
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

    def __init__(
        self, name, center_pt=None, normal_vector=None, radius_inner=5,
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
        self._center_pt = pv.Point3D(*(float(v) for v in value))

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
        self._normal_vector = pv.Vector3D(*(float(v) for v in value))

    @property
    def radius_outer(self):
        """Ring outer radius as a number (Default: 10)."""
        return self._radius_outer

    @radius_outer.setter
    def radius_outer(self, value):
        self._radius_outer = typing.float_positive(value)

    @classmethod
    def from_values(cls, values_dict):
        """Make a radiance primitive from value dict.

        {
            "modifier": "", // primitive modifier (Default: "void")
            "type": "", // primitive type
            "name": "", // primitive Name
            "values": {} // values,
            "dependencies": []
        }
        """
        assert 'type' in values_dict, 'Input dictionary is missing "type".'
        if values_dict['type'] != cls.__name__.lower():
            raise ValueError(
                'Type must be %s not %s.' % (cls.__name__.lower(), values_dict['type'])
            )

        modifier, dependencies = cls.filter_dict_input(values_dict)
        values = values_dict['values'][2]

        cls_ = cls(
            name=values_dict['name'],
            center_pt=values[0:3],
            normal_vector=values[3:6],
            radius_inner=values[6],
            radius_outer=values[7],
            modifier=modifier,
            dependencies=dependencies
        )
        # this might look redundant but it is NOT. see glass for explanation.
        cls_.values = values_dict['values']
        return cls_

    @classmethod
    def from_dict(cls, input_dict):
        """Make radiance material from dict
        {
            "type": "ring", // Geometry type
            "modifier": {} or "void",
            "name": "", // Geometry Name
            "center_pt": {"x": float, "y": float, "z": float},
            "normal_vector": {"x": float, "y": float, "z": float},
            "radius_inner": float,
            "radius_outer": float,
            "dependencies": []
        }
        """
        assert 'type' in input_dict, 'Input dictionary is missing "type".'
        if input_dict['type'] != cls.__name__.lower():
            raise ValueError(
                'Type must be %s not %s.' % (cls.__name__.lower(),
                                             input_dict['type'])
            )
        modifier, dependencies = cls.filter_dict_input(input_dict)

        st_c = input_dict["center_pt"]
        end_c = input_dict["normal_vector"]
        return cls(name=input_dict["name"],
                   center_pt=(st_c["x"], st_c["y"], st_c["z"]),
                   radius_inner=input_dict["radius_inner"],
                   normal_vector=(end_c["x"], end_c["y"], end_c["z"]),
                   radius_outer=input_dict["radius_outer"],
                   modifier=modifier,
                   dependencies=dependencies)

    def to_dict(self):
        """Translate radiance material to dict
        {
            "type": "ring", // Geometry type
            "modifier": {} or "void",
            "name": "", // Geometry Name
            "center_pt": {"x": float, "y": float, "z": float},
            "radius_inner": float,
            "normal_vector": {"x": float, "y": float, "z": float},
            "radius_outer": float
        }
        """
        return {
            "modifier": self.modifier.to_dict(),
            "type": self.__class__.__name__.lower(),
            "name": self.name,
            "center_pt": self.center_pt.to_dict(),
            "normal_vector": self.normal_vector.to_dict(),
            "radius_inner": self.radius_inner,
            "radius_outer": self.radius_outer,
            'dependencies': [dp.to_dict() for dp in self.dependencies]
        }
