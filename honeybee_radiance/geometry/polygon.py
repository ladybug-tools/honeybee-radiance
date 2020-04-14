"""Radiance Polygon.

http://radsite.lbl.gov/radiance/refer/ray.html#Polygon
"""
from .geometrybase import Geometry


class Polygon(Geometry):
    """Radiance Polygon.

    A polygon is given by a list of three-dimensional vertices, which are ordered
    counter-clockwise as viewed from the front side (into the surface normal). The last
    vertex is automatically connected to the first. Holes are represented in polygons as
    interior vertices connected to the outer perimeter by coincident edges (seams).

    .. code-block:: shell

        mod polygon id
        0
        0
        3n
                x1      y1      z1
                x2      y2      z2
                ...
                xn      yn      zn

    Args:
        identifier: Text string for a unique Geometry ID. Must not contain spaces
            or special characters. This will be used to identify the object across
            a model and in the exported Radiance files.
        vertices: Minimum of three arrays, each with 3 (x, y, z) values for
            vertices that make up the polygon. Vertices musct be ordered
            counter-clockwise as viewed from the front side. The last vertex is
            assumed to be connected to the first.
        modifier: Geometry modifier (Default: None).
        dependencies: A list of primitives that this primitive depends on. This
            argument is only useful for defining advanced primitives where the
            primitive is defined based on other primitives. (Default: [])

    Properties:
        * identifier
        * display_name
        * vertices
        * modifier
        * dependencies
        * values

    Usage:

    .. code-block:: python

        polygon = Polygon("test_polygon", [(0, 0, 10), (10, 0, 10), (10, 0, 0)])
        print(polygon)
    """
    __slots__ = ('_vertices',)

    def __init__(self, identifier, vertices, modifier=None, dependencies=None):
        """Radiance Polygon."""
        Geometry.__init__(self, identifier, modifier=modifier, dependencies=dependencies)
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
        self._vertices = tuple(tuple(float(v) for v in pt) for pt in vertices)
        assert len(self._vertices) > 2, 'Number of polygon vertices must be 3 or more.'
        for vert in self._vertices:
            assert len(vert) == 3, 'Polygon vertices must have 3 values for (x, y, z).'

    @classmethod
    def from_primitive_dict(cls, primitive_dict):
        """Initialize a Polygon from a primitive dict.

        Args:
            data: A dictionary in the format below.

        .. code-block:: python

            {
            "modifier": {},  # primitive modifier (Default: None)
            "type": "polygon",  # primitive type
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
        vertices_xyz = primitive_dict['values'][2]
        assert len(vertices_xyz) % 3 == 0, \
            'Number of coordinates must be divisible by 3.' \
            ' Invalid length: [%d].' % len(vertices_xyz)

        cls_ = cls(
            identifier=primitive_dict['identifier'],
            vertices=(vertices_xyz[i:i + 3] for i in range(0, len(vertices_xyz), 3)),
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
        """Initialize a Polygon from a dictionary.

        Args:
            data: A dictionary in the format below.

        .. code-block:: python

            {
            "type": "polygon",  # Geometry type
            "modifier": {} ,
            "identifier": "",  # Geometry identifer
            "display_name": "",  # Geometry display name
            "vertices": [(0, 0, 10), (10, 0, 10), (10, 0, 0)],
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

        vertices = data["vertices"]
        new_obj = cls(
            identifier=data["identifier"],
            vertices=data["vertices"],
            modifier=modifier,
            dependencies=dependencies
        )
        if 'display_name' in data and data['display_name'] is not None:
            new_obj.display_name = data['display_name']
        return new_obj

    def to_dict(self):
        """Translate this object to a dictionary."""
        base = {
            "modifier": self.modifier.to_dict(),
            "type": self.__class__.__name__.lower(),
            "identifier": self.identifier,
            "vertices": self.vertices,
            'dependencies': [dp.to_dict() for dp in self.dependencies]
        }
        if self._display_name is not None:
            base['display_name'] = self.display_name
        return base

    def __copy__(self):
        mod, depend = self._dup_mod_and_depend()
        new_obj = self.__class__(self.identifier, self.vertices, mod, depend)
        new_obj._display_name = self._display_name
        return new_obj
