"""Radiance Polygon.

http://radsite.lbl.gov/radiance/refer/ray.html#Polygon
"""
from .geometrybase import Geometry
import ladybug_geometry.geometry3d.pointvector as pv


class Polygon(Geometry):
    """Radiance Polygon.

    A polygon is given by a list of three-dimensional vertices, which are ordered
    counter-clockwise as viewed from the front side (into the surface normal). The last
    vertex is automatically connected to the first. Holes are represented in polygons as
    interior vertices connected to the outer perimeter by coincident edges (seams).

    mod polygon id
    0
    0
    3n
            x1      y1      z1
            x2      y2      z2
            ...
            xn      yn      zn
    """

    def __init__(self, name, vertices, modifier=None, dependencies=None):
        """Radiance Polygon.

        Attributes:
            name: Geometry name as a string. Do not use white space or special
                character.
            vertices: Minimum of three (x, y, z) vertices which are are ordered
                counter-clockwise as viewed from the front side. The last vertex is
                automatically connected to the first.
            modifier: Geometry modifier (Default: "void").
            dependencies: A list of primitives that this primitive depends on. This
                argument is only useful for defining advanced primitives where the
                primitive is defined based on other primitives. (Default: [])

        Usage:
            polygon = Polygon("test_polygon", [(0, 0, 10), (10, 0, 10), (10, 0, 0)])
            print(polygon)
        """
        Geometry.__init__(self, name, modifier=modifier, dependencies=dependencies)
        self.vertices = vertices
        self._update_values()

    def _update_values(self):
        """update values dictionary."""
        self._values[2] = [v for pt in self.vertices for v in pt]

    @property
    def vertices(self):
        """List of Polygon vertices."""
        return self._vertices
    
    @vertices.setter
    def vertices(self, vertices):
        self._vertices = tuple(
            pv.Point3D(*(float(v) for v in value))
            for value in vertices
        )
        assert len(self._vertices) > 2, 'Number of vertices must be 3 or more.'

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
        vertices_xyz = values_dict['values'][2]
        assert len(vertices_xyz) % 3 == 0, \
            'Number of coordinates must be divisible by 3.' \
            ' Invalid length: [%d].' % len(vertices_xyz)

        cls_ = cls(
            name=values_dict['name'],
            vertices=[vertices_xyz[i:i + 3] for i in range(0, len(vertices_xyz), 3)],
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
            "type": "polygon", // Geometry type
            "modifier": {} or "void",
            "name": "", // Geometry Name
            "vertices": [{"x": float, "y": float, "z": float}, ...],
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

        vertices = input_dict["vertices"]
        return cls(
            name=input_dict["name"],
            vertices=[(v['x'], v['y'], v['z']) for v in vertices],
            modifier=modifier,
            dependencies=dependencies
        )

    def to_dict(self):
        """Translate radiance material to dict
        {
            "type": "polygon", // Geometry type
            "modifier": {} or "void",
            "name": "", // Geometry Name
            "vertices": [{"x": float, "y": float, "z": float}, ...],
            "dependencies": []
        }
        """
        return {
            "modifier": self.modifier.to_dict(),
            "type": self.__class__.__name__.lower(),
            "name": self.name,
            "vertices": [v.to_dict() for v in self.vertices],
            'dependencies': [dp.to_dict() for dp in self.dependencies]
        }
