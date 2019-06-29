"""Radiance Cylinder.

http://radsite.lbl.gov/radiance/refer/ray.html#Cylinder
"""
from .geometrybase import Geometry
import honeybee.typing as typing
import ladybug_geometry.geometry3d.pointvector as pv


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

    def __init__(self, name, center_pt_start=None, center_pt_end=None, radius=10,
                 modifier=None, dependencies=None):
        """Radiance Cylinder.

        Args:
            name: Geometry name as a string. Do not use white space or special
                character.
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
        self._center_pt_start = pv.Point3D(*(float(v) for v in value))

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
        self._center_pt_end = pv.Point3D(*(float(v) for v in value))

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
            center_pt_end=values[3:6],
            radius=values[6],
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
            "center_pt_end": {"x": float, "y": float, "z": float},
            "radius": float,
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
                   center_pt_end=(end_c["x"], end_c["y"], end_c["z"]),
                   radius=input_dict["radius"],
                   modifier=modifier,
                   dependencies=dependencies)

    def to_dict(self):
        """Translate radiance material to dict
        {
            "type": "cone", // Geometry type
            "modifier": {} or "void",
            "name": "", // Geometry Name
            "center_pt_start": {"x": float, "y": float, "z": float},
            "center_pt_end": {"x": float, "y": float, "z": float},
            "radius": float,
            "dependencies": []
        }
        """
        return {
            "modifier": self.modifier.to_dict(),
            "type": self.__class__.__name__.lower(),
            "name": self.name,
            "center_pt_start": self.center_pt_start.to_dict(),
            "radius": self.radius,
            "center_pt_end": self.center_pt_end.to_dict(),
            'dependencies': [dp.to_dict() for dp in self.dependencies]
        }
