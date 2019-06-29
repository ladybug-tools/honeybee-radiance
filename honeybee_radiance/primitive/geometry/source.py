"""Radiance Source.

http://radsite.lbl.gov/radiance/refer/ray.html#Source
"""
from .geometrybase import Geometry
import honeybee.typing as typing
import ladybug_geometry.geometry3d.pointvector as pv


class Source(Geometry):
    """Radiance Source.

    A source is not really a surface, but a solid angle. It is used for specifying light
    sources that are very distant. The direction to the center of the source and the
    number of degrees subtended by its disk are given as follows:

    mod source id
    0
    0
    4 xdir ydir zdir angle
    """


    def __init__(self, name, direction=None, angle=0.533, modifier=None,
            dependencies=None):
        """Radiance Source.

        Args:
            name: Geometry name as a string. Do not use white space or special
                character.
            direction: A vector to set source direction (x, y, z) (Default: (0, 0 ,-1)).
            angle: Source solid angle (Default: 0.533).
            modifier: Geometry modifier (Default: "void").
            dependencies: A list of primitives that this primitive depends on. This
                argument is only useful for defining advanced primitives where the
                primitive is defined based on other primitives. (Default: [])

        Usage:
            source = Source("test_source", (0, 0, 10), 10)
            print(source)
        """
        Geometry.__init__(self, name, modifier=modifier, dependencies=dependencies)
        self.direction = direction or (0, 0, -1)
        self.angle = angle if angle is not None else 0.533

        self._update_values()

    def _update_values(self):
        """update values dictionary."""
        self._values[2] = \
            [self.direction[0], self.direction[1], self.direction[2], self.angle]

    @property
    def direction(self):
        """A vector to set source direction (x, y, z) (Default: (0, 0 ,-1))."""
        return self._direction
    
    @direction.setter
    def direction(self, value):
        self._direction = pv.Vector3D(*(float(v) for v in value))

    @property
    def angle(self):
        """Source solid angle (Default: 0.533)."""
        return self._angle
    
    @angle.setter
    def angle(self, value):
        self._angle = typing.float_positive(value)

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
            direction=values[0:3],
            angle=values[3],
            modifier=modifier,
            dependencies=dependencies
        )
        # this might look redundant but it is NOT. see glass for explanation.
        cls_.values = values_dict['values']
        return cls_

    @classmethod
    def from_dict(cls, input_dict):
        """Make radiance primitive from dict
        {
            "type": "source", // Geometry type
            "modifier": {} or "void",
            "name": "", // Geometry Name
            "direction": {"x": float, "y": float, "z": float},
            "angle": float,
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
        
        st_c = input_dict["direction"]
        return cls(name=input_dict["name"],
                   direction=(st_c["x"], st_c["y"], st_c["z"]),
                   angle=input_dict["angle"],
                   modifier=modifier,
                   dependencies=dependencies)

    def to_dict(self):
        """Translate radiance geometry to dict
        {
            "type": "source", // Geometry type
            "modifier": {} or "void",
            "name": "", // Geometry Name
            "direction": {"x": float, "y": float, "z": float},
            "angle": float,
            "dependencies": []
        }
        """
        return {
            "modifier": self.modifier.to_dict(),
            "type": self.__class__.__name__.lower(),
            "name": self.name,
            "direction": self.direction.to_dict(),
            "angle": self.angle,
            'dependencies': [dp.to_dict() for dp in self.dependencies]
        }
