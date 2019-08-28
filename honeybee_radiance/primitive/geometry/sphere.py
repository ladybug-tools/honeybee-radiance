"""Radiance Sphere.

http://radsite.lbl.gov/radiance/refer/ray.html#Sphere
"""
from .geometrybase import Geometry
import honeybee.typing as typing
import ladybug_geometry.geometry3d.pointvector as pv


class Sphere(Geometry):
    """Radiance Sphere.

    mod sphere id
    0
    0
    4 xcent ycent zcent radius
    """

    def __init__(self, name, center_pt=None, radius=10, modifier=None,
            dependencies=None):
        """Radiance Sphere.

        Attributes:
            name: Geometry name as a string. Do not use white space or special
                character.
            center_pt: Sphere center point as (x, y, z) (Default: (0, 0 ,0)).
            radius: Sphere radius as a number (Default: 10).
            modifier: Geometry modifier (Default: "void").
            dependencies: A list of primitives that this primitive depends on. This
                argument is only useful for defining advanced primitives where the
                primitive is defined based on other primitives. (Default: [])

        Usage:
            sphere = Sphere("test_sphere", (0, 0, 10), 10)
            print(sphere)
        """
        Geometry.__init__(self, name, modifier=modifier, dependencies=dependencies)
        self.center_pt = center_pt or (0, 0, 0)
        self.radius = radius if radius is not None else 10

        self._update_values()

    def _update_values(self):
        """update value dictionaries."""
        self._values[2] = \
            [self.center_pt[0], self.center_pt[1], self.center_pt[2], self.radius]

    @property
    def center_pt(self):
        """Sphere center point as (x, y, z) (Default: (0, 0 ,0))."""
        return self._center_pt
    
    @center_pt.setter
    def center_pt(self, value):
        self._center_pt = pv.Point3D(*(float(v) for v in value))

    @property
    def radius(self):
        """Sphere radius as a number (Default: 10)."""
        return self._radius
    
    @radius.setter
    def radius(self, value):
        self._radius = typing.float_positive(value)

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
            radius=values[3],
            modifier=modifier,
            dependencies=dependencies
        )
        # this might look redundant but it is NOT. see glass for explanation.
        cls_.values = values_dict['values']
        return cls_

    @classmethod
    def from_dict(cls, input_dict):
        """Make radiance sphere from dict
        {
            "type": "cone", // Geometry type
            "modifier": {} or "void",
            "name": "", // Geometry Name
            "center_pt": {"x": float, "y": float, "z": float},
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
        
        st_c = input_dict["center_pt"]
        return cls(name=input_dict["name"],
                   center_pt=(st_c["x"], st_c["y"], st_c["z"]),
                   radius=input_dict["radius"],
                   modifier=modifier,
                   dependencies=dependencies)

    def to_dict(self):
        """Translate a sphere to dict
        {
            "type": "cone", // Geometry type
            "modifier": {} or "void",
            "name": "", // Geometry Name
            "center_pt": {"x": float, "y": float, "z": float},
            "radius": float,
            "dependencies": []
        }
        """
        return {
            "modifier": self.modifier.to_dict(),
            "type": self.__class__.__name__.lower(),
            "name": self.name,
            "center_pt": self.center_pt.to_dict(),
            "radius": self.radius,
            'dependencies': [dp.to_dict() for dp in self.dependencies]
        }
