"""Radiance Cone.

http://radsite.lbl.gov/radiance/refer/ray.html#Cone
"""
from .geometrybase import Geometry
import honeybee.typing as typing
import ladybug_geometry.geometry3d.pointvector as pv


class Cone(Geometry):
    """Radiance Cone.

    A cone is a megaphone-shaped object. It is truncated by two planes perpendicular to
    its axis, and one of its ends may come to a point. It is given as two axis endpoints,
    and the starting and ending radii:

        mod cone id
        0
        0
        8
                x0      y0      z0
                x1      y1      z1
                r0      r1

    """

    def __init__(self, name, center_pt_start=None, radius_start=10,
                 center_pt_end=None, radius_end=0, modifier=None, dependencies=None):
        """Radiance Cone.

        Attributes:
            name: Geometry name as a string. Do not use white space or special
                character.
            center_pt_start: Cone start center point as (x, y, z) (Default: (0, 0 ,0)).
            radius_start: Cone start radius as a number (Default: 10).
            center_pt_end: Cone end center point as (x, y, z) (Default: (0, 0 ,10)).
            radius_end: Cone end radius as a number (Default: 0).
            modifier: Geometry modifier (Default: "void").
            dependencies: A list of primitives that this primitive depends on. This
                argument is only useful for defining advanced primitives where the
                primitive is defined based on other primitives. (Default: [])
        """
        Geometry.__init__(self, name, modifier=modifier, dependencies=dependencies)
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
        """Cone start center point as (x, y, z) (Default: (0, 0 ,0))."""
        return self._center_pt_start
    
    @center_pt_start.setter
    def center_pt_start(self, value):
        self._center_pt_start = pv.Point3D(*(float(v) for v in value))

    @property
    def radius_start(self):
        """Cone start radius as a number (Default: 10)."""
        return self._radius_start
    
    @radius_start.setter
    def radius_start(self, value):
        self._radius_start = typing.float_positive(value)

    @property
    def center_pt_end(self):
        """Cone end center point as (x, y, z) (Default: (0, 0 ,10))."""
        return self._center_pt_end
    
    @center_pt_end.setter
    def center_pt_end(self, value):
        self._center_pt_end = pv.Point3D(*(float(v) for v in value))

    @property
    def radius_end(self):
        """ Cone end radius as a number (Default: 0)."""
        return self._radius_end
    
    @radius_end.setter
    def radius_end(self, value):
        self._radius_end = typing.float_positive(value)

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
            center_pt_start=values[0:3],
            radius_start=values[6],
            center_pt_end=values[3:6],
            radius_end=values[7],
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
            "type": "cone", // Geometry type
            "modifier": {} or "void",
            "name": "", // Geometry Name
            "center_pt_start": {"x": float, "y": float, "z": float},
            "radius_start": float,
            "center_pt_end": {"x": float, "y": float, "z": float},
            "radius_end": float,
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
        
        st_c = input_dict["center_pt_start"]
        end_c = input_dict["center_pt_end"]
        return cls(name=input_dict["name"],
                   center_pt_start=(st_c["x"], st_c["y"], st_c["z"]),
                   radius_start=input_dict["radius_start"],
                   center_pt_end=(end_c["x"], end_c["y"], end_c["z"]),
                   radius_end=input_dict["radius_end"],
                   modifier=modifier,
                   dependencies=dependencies)

    def to_dict(self):
        """Translate radiance material to dict
        {
            "type": "cone", // Geometry type
            "modifier": {} or "void",
            "name": "", // Geometry Name
            "center_pt_start": {"x": float, "y": float, "z": float},
            "radius_start": float,
            "center_pt_end": {"x": float, "y": float, "z": float},
            "radius_end": float
        }
        """
        return {
            "modifier": self.modifier.to_dict(),
            "type": self.__class__.__name__.lower(),
            "name": self.name,
            "radius_start": self.radius_start,
            "center_pt_start": self.center_pt_start.to_dict(),
            "radius_end": self.radius_end,
            "center_pt_end": self.center_pt_end.to_dict(),
            'dependencies': [dp.to_dict() for dp in self.dependencies]
        }
