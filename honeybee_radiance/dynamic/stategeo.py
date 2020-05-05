# coding: utf-8
"""Dynamic geometry that can be assigned to individual states."""
from ..modifier import Modifier
from ..geometry import Polygon
from ..mutil import dict_to_modifier  # imports all modifiers classes
from ..lib.modifiers import black, generic_exterior_shade

from honeybee.typing import valid_rad_string
from ladybug_geometry.geometry3d.pointvector import Point3D
from ladybug_geometry.geometry3d.face import Face3D

import math


class StateGeometry(object):
    """A single planar geometry that can be assigned to Radiance states.

    Args:
        identifier: Text string for a unique geometry ID. Must not contain any
            spaces or special characters.
        geometry: A ladybug-geometry Face3D.
        modifier: A Honeybee Radiance Modifier object for the geometry. If None,
            it will be the Generic Exterior Shade modifier in the lib. (Default: None).

    Properties:
        * identifier
        * display_name
        * geometry
        * modifier
        * modifier_direct
        * parent
        * has_parent
        * vertices
        * normal
        * center
        * area
    """
    __slots__ = ('_identifier', '_display_name', '_geometry', '_modifier',
                 '_modifier_direct', '_parent')

    def __init__(self, identifier, geometry, modifier=None):
        """Initialize StateGeometry."""
        # process the identifier
        self._identifier = valid_rad_string(identifier, 'state geometry identifier')
        self._display_name = self._identifier
        # process the geometry
        assert isinstance(geometry, Face3D), \
            'Expected ladybug_geometry Face3D. Got {}'.format(type(geometry))
        self._geometry = geometry
        # process the modifier
        self.modifier = modifier
        self._modifier_direct = None
        self._parent = None  # _parent will be set when the Geo is added to a state

    @classmethod
    def from_dict(cls, data):
        """Initialize a StateGeometry from a dictionary.

        Note that the dictionary must be a non-abridged version for this
        classmethod to work.

        Args:
            data: A dictionary representation of an StateGeometry with the
                format below.

        .. code-block:: python

            {
            'type': 'StateGeometry',
            'identifier': str,  # Text for the unique object identifier
            'display_name': str,  # Optional text for the display name
            'geometry': {},  # A ladybug_geometry Face3D dictionary
            'modifier': {},  # A Honeybee Radiance Modifier dictionary
            'modifier_direct': {}  # A Honeybee Radiance Modifier dictionary
            }
        """
        # check the type of dictionary
        assert data['type'] == 'StateGeometry', 'Expected StateGeometry dictionary. ' \
            'Got {}.'.format(data['type'])
        geo = cls(data['identifier'], Face3D.from_dict(data['geometry']))

        if 'modifier' in data and data['modifier'] is not None:
            geo.modifier = dict_to_modifier(data['modifier'])
        if 'modifier_direct' in data and data['modifier_direct'] is not None:
            geo.modifier_direct = dict_to_modifier(data['modifier_direct'])
        if 'display_name' in data and data['display_name'] is not None:
            geo.display_name = data['display_name']
        return geo

    @classmethod
    def from_dict_abridged(cls, data, modifiers):
        """Create StateGeometry from an abridged dictionary.

        Args:
            data: A dictionary representation of StateGeometryAbridged with
                the format below.
            modifiers: A dictionary of modifiers with modifier identifiers as keys,
                which will be used to re-assign modifiers.

        .. code-block:: python

            {
            'type': 'StateGeometryAbridged',
            'identifier': str,  # Text for the unique object identifier
            'display_name': str,  # Optional text for the display name
            'geometry': {},  # A ladybug_geometry Face3D dictionary
            'modifier': str  # A Honeybee Radiance Modifier identifier
            'modifier_direct': str  # A Honeybee Radiance Modifier identifier
            }
        """
        # check the type of dictionary
        assert data['type'] == 'StateGeometryAbridged', \
            'Expected StateGeometryAbridged dictionary. Got {}.'.format(data['type'])
        geo = cls(data['identifier'], Face3D.from_dict(data['geometry']))

        if 'modifier' in data and data['modifier'] is not None:
            geo.modifier = modifiers[data['modifier']]
        if 'modifier_direct' in data and data['modifier_direct'] is not None:
            geo.modifier_direct = modifiers[data['modifier_direct']]
        if 'display_name' in data and data['display_name'] is not None:
            geo.display_name = data['display_name']
        return geo

    @classmethod
    def from_vertices(cls, identifier, vertices, modifier=None):
        """Create StateGeometry from vertices with each vertex as an iterable of 3 floats.

        Note that this method is not recommended for a geometry with one or more holes
        since the distinction between hole vertices and boundary vertices cannot
        be derived from a single list of vertices.

        Args:
            identifier: Text string for a unique geometry ID. Must not contain any
                spaces or special characters.
            vertices: A flattened list of 3 or more vertices as (x, y, z).
            modifier: A Honeybee Radiance Modifier object for the geometry. If None, it
                will be the Generic Exterior Shade modifier in the lib. (Default: None).
        """
        geometry = Face3D(tuple(Point3D(*v) for v in vertices))
        return cls(identifier, geometry, modifier)

    @property
    def identifier(self):
        """Get a text string for the unique object identifer.
    
        This identifier remains constant as the object is mutated, copied, and
        serialized to different formats (eg. dict, idf, rad). As such, this
        property is used to reference the object across a Model.
        """
        return self._identifier

    @property
    def display_name(self):
        """Get or set a string for the object name without any character restrictions.

        If not set, this will be equal to the identifier.
        """
        return self._display_name

    @display_name.setter
    def display_name(self, value):
        try:
            self._display_name = str(value)
        except UnicodeEncodeError:  # Python 2 machine lacking the character set
            self._display_name = value  # keep it as unicode

    @property
    def geometry(self):
        """Get a ladybug_geometry Face3D object representing the Shade."""
        return self._geometry

    @property
    def modifier(self):
        """Get or set the object modifier."""
        if self._modifier:  # set by user
            return self._modifier
        return generic_exterior_shade

    @modifier.setter
    def modifier(self, value):
        if value is not None:
            assert isinstance(value, Modifier), \
                'Expected Radiance Modifier for shade. Got {}'.format(type(value))
            value.lock()  # lock editing in case modifier has multiple references
        self._modifier = value

    @property
    def modifier_direct(self):
        """Get or set a modifier to be used in direct solar studies.

        If None, this will be a completely black material if the object's modifier is
        opaque and will be equal to the modifier if the object's modifier is non-opaque.
        """
        if self._modifier_direct:  # set by user
            return self._modifier_direct
        mod = self.modifier  # assign a default based on whether the modifier is opaque
        if mod.is_void or mod.is_opaque:
            return black
        else:
            return mod

    @modifier_direct.setter
    def modifier_direct(self, value):
        if value is not None:
            assert isinstance(value, Modifier), \
                'Expected Radiance Modifier. Got {}'.format(type(value))
            value.lock()  # lock editing in case modifier has multiple references
        self._modifier_direct = value

    @property
    def is_opaque(self):
        """Boolean noting whether this geomtry has an opaque modifier."""
        return True if self.modifier.is_void else self.modifier.is_opaque

    @property
    def parent(self):
        """Get the parent State if assigned. None if not assigned."""
        return self._parent

    @property
    def has_parent(self):
        """Get a boolean noting whether this StateGeometry has a parent State."""
        return self._parent is not None

    @property
    def vertices(self):
        """Get a list of vertices for the geometry (in counter-clockwise order)."""
        return self._geometry.vertices

    @property
    def normal(self):
        """Get a ladybug_geometry Vector3D for the direction the geometry is pointing.
        """
        return self._geometry.normal

    @property
    def center(self):
        """Get a ladybug_geometry Point3D for the center of the geometry.

        Note that this is the center of the bounding rectangle around this geometry
        and not the area centroid.
        """
        return self._geometry.center

    @property
    def area(self):
        """Get the area of the geometry."""
        return self._geometry.area

    def move(self, moving_vec):
        """Move this StateGeometry along a vector.

        Args:
            moving_vec: A ladybug_geometry Vector3D with the direction and distance
                to move the face.
        """
        self._geometry = self.geometry.move(moving_vec)

    def rotate(self, axis, angle, origin):
        """Rotate this StateGeometry by a certain angle around an axis and origin.

        Args:
            axis: A ladybug_geometry Vector3D axis representing the axis of rotation.
            angle: An angle for rotation in degrees.
            origin: A ladybug_geometry Point3D for the origin around which the
                object will be rotated.
        """
        self._geometry = self.geometry.rotate(axis, math.radians(angle), origin)

    def rotate_xy(self, angle, origin):
        """Rotate this StateGeometry counterclockwise in the XY plane by a certain angle.

        Args:
            angle: An angle in degrees.
            origin: A ladybug_geometry Point3D for the origin around which the
                object will be rotated.
        """
        self._geometry = self.geometry.rotate_xy(math.radians(angle), origin)

    def reflect(self, plane):
        """Reflect this StateGeometry across a plane.

        Args:
            plane: A ladybug_geometry Plane across which the object will
                be reflected.
        """
        self._geometry = self.geometry.reflect(plane.n, plane.o)

    def scale(self, factor, origin=None):
        """Scale this StateGeometry by a factor from an origin point.

        Args:
            factor: A number representing how much the object should be scaled.
            origin: A ladybug_geometry Point3D representing the origin from which
                to scale. If None, it will be scaled from the World origin (0, 0, 0).
        """
        self._geometry = self.geometry.scale(factor, origin)

    def to_dict(self, abridged=False):
        """Return StateGeometry as a dictionary.

        Args:
            abridged: Boolean to note whether the full dictionary describing the
                object should be returned (False) or just an abridged version (True).
                Default: False.
        """
        # assign required properties
        base = {'type': 'StateGeometryAbridged'} if abridged else \
            {'type': 'StateGeometry'}
        base['identifier'] = self.identifier
        base['display_name'] = self.display_name
        base['geometry'] = self.geometry.to_dict()

        # assign optional properties
        if self._modifier:
            base['modifier'] = self._modifier.identifier if abridged else \
                self._modifier.to_dict()
        if self._modifier_direct is not None:
            base['modifier_direct'] = self._modifier_direct.identifier if abridged \
                else self._modifier.to_dict()
        return base

    def to_radiance(self, direct=False, minimal=False):
        """Generate a RAD string representation of this StateGeometry.

        Note that the resulting string lacks modifiers.

        Args:
            direct: Boolean to note whether to write the "direct" version of the
                state, which will have the modifier_direct applied. (Default: False)
            minimal: Boolean to note whether the radiance string should be written
                in a minimal format (with spaces instead of line breaks). Default: False.
        """
        modifier = self.modifier_direct if direct else self.modifier
        base_poly = Polygon(self.identifier, self.vertices, modifier)
        return base_poly.to_radiance(minimal, False, False)

    def duplicate(self):
        """Get a copy of this object."""
        return self.__copy__()

    def __copy__(self):
        new_geo = StateGeometry(self.identifier, self.geometry, self._modifier)
        new_geo._modifier_direct = self._modifier_direct
        new_geo._display_name = self.display_name
        return new_geo

    def ToString(self):
        return self.__repr__()

    def __repr__(self):
        return 'StateGeometry: %s' % self.display_name
