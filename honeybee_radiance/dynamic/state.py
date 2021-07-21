# coding=utf-8
"""Object representing a single state for a dynamic object."""
from __future__ import division

from .stategeo import StateGeometry
from ..geometry import Polygon
from ..modifier import Modifier
from ..mutil import dict_to_modifier
from ..lib.modifiers import white_glow

from ladybug_geometry.geometry3d.face import Face3D

import math


class _RadianceState(object):
    """Object representing a single state for a dynamic object.

    Args:
        modifier: A Honeybee Radiance Modifier object to be applied to this state's
            parent in this state. This is used to swap out the modifier in
            multi-phase studies. If None, it will be the parent's default modifier.
        shades: An optional array of StateGeometry objects to be included
            with this state. The StateGeometry objects cannot already have
            another parent state.

    Properties:
        * modifier
        * shades
        * modifier_direct
        * parent
        * has_parent
    """

    __slots__ = ('_modifier', '_shades', '_modifier_direct', '_parent')

    def __init__(self, modifier=None, shades=None):
        """Initialize RadianceState."""
        self._parent = None  # will be set when the state is assigned
        self.modifier = modifier
        self.shades = shades
        self._modifier_direct = None

    @property
    def modifier(self):
        """Get or set the modifier to be applied to the parent in this state.
        """
        if not self._modifier and self.has_parent:  # use the parent's default
            return self.parent.properties.radiance.modifier
        return self._modifier

    @modifier.setter
    def modifier(self, value):
        if value is not None:
            assert isinstance(value, Modifier), \
                'Expected Modifier for RadianceState. Got {}'.format(type(value))
            value.lock()  # lock editing in case modifier has multiple references
        self._modifier = value

    @property
    def shades(self):
        """Get or set an array of StateGeometry objects to be included with this state.

        The StateGeometry objects cannot already have another parent state.
        """
        return tuple(self._shades)

    @shades.setter
    def shades(self, value):
        if value is not None:
            try:
                self._shades = [self._check_shade(sh) for sh in value]
            except (ValueError, TypeError):
                raise TypeError('RadianceState shades must be an iterable. ' \
                    'Got  {}.'.format(type(value)))
        else:
            self._shades = []

    @property
    def modifier_direct(self):
        """Get or set a modifier for the parent to be used in direct studies.

        If None, it will be the same as the modifier of this state if that modifier
        is nonopaque. Otherwise, it will be the modifier_blk of the parent.
        """
        if not self._modifier_direct:  # use the state's default modifier
            mod = self.modifier
            if mod is None or not mod.is_opaque:
                return mod
            return self._parent.properties.radiance.modifier_blk
        return self._modifier_direct

    @modifier_direct.setter
    def modifier_direct(self, value):
        if value is not None:
            assert isinstance(value, Modifier), \
                'Expected Modifier for RadianceState. Got {}'.format(type(value))
            value.lock()  # lock editing in case modifier has multiple references
        self._modifier_direct = value

    @property
    def parent(self):
        """Get the parent of this State if assigned. None if not assigned."""
        return self._parent

    @property
    def has_parent(self):
        """Get a boolean noting whether this State has a parent."""
        return self._parent is not None

    def remove_shades(self):
        """Remove all shades assigned to this object."""
        for shade in self._shades:
            shade._parent = None
        self._shades = []

    def add_shades(self, shades):
        """Add an array of Shade objects to this state.

        Args:
            shades: An array of Shade objects to add to the this state.
        """
        for shade in shades:
            self._shades.append(self._check_shade(shade))

    def add_shade(self, shade):
        """Add a Shade object to this state.

        Args:
            shade: A Shade object to add to the this state.
        """
        self._shades.append(self._check_shade(shade))

    def move(self, moving_vec):
        """Move all shades assigned to this state along a vector.

        Args:
            moving_vec: A ladybug_geometry Vector3D with the direction and distance
                to move the shades.
        """
        for shd in self._shades:
            shd.move(moving_vec)

    def rotate(self, axis, angle, origin):
        """Rotate all shades assigned to this state.

        Args:
            axis: A ladybug_geometry Vector3D axis representing the axis of rotation.
            angle: An angle for rotation in degrees.
            origin: A ladybug_geometry Point3D for the origin around which the
                object will be rotated.
        """
        for shd in self._shades:
            shd.rotate(axis, angle, origin)

    def rotate_xy(self, angle, origin):
        """Rotate all shades counterclockwise in the world XY plane.

        Args:
            angle: An angle in degrees.
            origin: A ladybug_geometry Point3D for the origin around which the
                object will be rotated.
        """
        for shd in self._shades:
            shd.rotate_xy(angle, origin)

    def reflect(self, plane):
        """Reflect all shades assigned to this state across a plane.

        Args:
            plane: A ladybug_geometry Plane across which the object will
                be reflected.
        """
        for shd in self._shades:
            shd.reflect(plane)

    def scale(self, factor, origin=None):
        """Scale all shades assigned to this state by a factor.

        Args:
            factor: A number representing how much the object should be scaled.
            origin: A ladybug_geometry Point3D representing the origin from which
                to scale. If None, it will be scaled from the World origin (0, 0, 0).
        """
        for shd in self._shades:
            shd.scale(factor, origin)

    def to_radiance(self, direct=False, minimal=False):
        """Generate a RAD string representation of this state.

        Note that the resulting string lacks modifiers but includes both the
        parent geometry and the geometry of any shades.

        Args:
            direct: Boolean to note whether to write the "direct" version of the
                state, which will have the modifier_direct applied to the parent
                of the state and use the modifier_blk assigned to each of the
                shades. (Default: False)
            minimal: Boolean to note whether the radiance string should be written
                in a minimal format (with spaces instead of line breaks). Default: False.
        """
        assert self.has_parent, 'State must have a parent to use to_radiance.'
        modifier = self.modifier_direct if direct else self.modifier
        base_poly = Polygon(self.parent.identifier, self.parent.vertices, modifier)
        rad_strs = [base_poly.to_radiance(minimal, False, False)]
        for shd in self._shades:
            rad_strs.append(shd.to_radiance(direct, minimal))
        return '\n\n'.join(rad_strs)

    def duplicate(self):
        """Get a copy of this object."""
        return self.__copy__()

    def _check_shade(self, shade):
        assert isinstance(shade, StateGeometry), \
            'Expected StateGeometry for RadianceState. Got {}.'.format(type(shade))
        assert shade.parent is None, \
            'StateGeometry for a RadianceState cannot already have a parent object.'
        shade._parent = self
        return shade

    def _duplicate_shades(self, new_state):
        """Add duplicated child shades to a duplicated new_state."""
        new_state._shades = [shd.duplicate() for shd in self._shades]
        for shd in new_state._shades:
            shd._parent = new_state

    def __copy__(self):
        new_obj = _RadianceState(self._modifier)
        self._duplicate_shades(new_obj)
        new_obj._modifier_direct = self._modifier_direct
        return new_obj

    def ToString(self):
        return self.__repr__()

    def __repr__(self):
        return 'State: ({})'.format(self.modifier.display_name)


class RadianceShadeState(_RadianceState):
    """Object representing a single state for a dynamic Shade.

    Args:
        modifier: A Honeybee Radiance Modifier object to be applied to this state's
            parent in this state. This can be used to change the transmittance of
            deciduous trees, change the modifier of a ground surface to account
            for snow reflectance, etc. If None, it will be the parent's default
            modifier.
        shades: An optional array of StateGeometry objects to be included
            with this state. The StateGeometry objects cannot already have
            another parent state.

    Properties:
        * modifier
        * shades
        * modifier_direct
        * parent
        * has_parent
    """
    __slots__ = ()

    def __init__(self, modifier=None, shades=None):
        """Initialize RadianceShadeState."""
        _RadianceState.__init__(self, modifier, shades)

    @classmethod
    def from_dict(cls, data):
        """Create RadianceShadeState from a dictionary.

        Note that the dictionary must be a non-abridged version for this
        classmethod to work.

        Args:
            data: A dictionary representation of RadianceShadeState with the
                format below.

        .. code-block:: python

            {
            'type': 'RadianceShadeState',
            'modifier': {},  # A Honeybee Radiance Modifier dictionary
            'shades': [],  # A list of StateGeometry dictionaries
            'modifier_direct': {}  # A Honeybee Radiance Modifier dictionary
            }
        """
        assert data['type'] == 'RadianceShadeState', \
            'Expected RadianceShadeState. Got {}.'.format(data['type'])
        new_state = cls()
        if 'modifier' in data and data['modifier'] is not None:
            new_state.modifier = dict_to_modifier(data['modifier'])
        if 'shades' in data and data['shades'] is not None:
            new_state.shades = [StateGeometry.from_dict(shd) for shd in data['shades']]
        if 'modifier_direct' in data and data['modifier_direct'] is not None:
            new_state.modifier_direct = dict_to_modifier(data['modifier_direct'])
        return new_state

    @classmethod
    def from_dict_abridged(cls, data, modifiers):
        """Create RadianceShadeState from an abridged dictionary.

        Args:
            data: A dictionary representation of RadianceShadeStateAbridged with
                the format below.
            modifiers: A dictionary of modifiers with modifier identifiers as keys,
                which will be used to re-assign modifiers.

        .. code-block:: python

            {
            'type': 'RadianceShadeStateAbridged',
            'modifier': str,  # An identifier of a honeybee-radiance modifier
            'shades': [],  # A list of abridged StateGeometry dictionaries
            'modifier_direct': str  # An identifier of a honeybee-radiance modifier
            }
        """
        assert data['type'] == 'RadianceShadeStateAbridged', \
            'Expected RadianceShadeStateAbridged. Got {}.'.format(data['type'])
        new_state = cls()
        if 'modifier' in data and data['modifier'] is not None:
            new_state.modifier = modifiers[data['modifier']]
        if 'shades' in data and data['shades'] is not None:
            new_state.shades = [StateGeometry.from_dict_abridged(shd, modifiers)
                                for shd in data['shades']]
        if 'modifier_direct' in data and data['modifier_direct'] is not None:
            new_state.modifier_direct = modifiers[data['modifier_direct']]
        return new_state

    def to_dict(self, abridged=False):
        """Convert RadianceShadeState to a dictionary.

        Args:
            abridged: Boolean to note whether the full dictionary describing the
                object should be returned (False) or just an abridged version (True).
                Default: False.
        """
        base = {'type': 'RadianceShadeStateAbridged'} if abridged else \
            {'type': 'RadianceShadeState'}
        if self._modifier:
            base['modifier'] = self._modifier.identifier if abridged else \
                self._modifier.to_dict()
        if len(self._shades) != 0:
            base['shades'] = [shd.to_dict(abridged=abridged) for shd in self.shades]
        if self._modifier_direct is not None:
            base['modifier_direct'] = self._modifier_direct.identifier if abridged \
                else self._modifier.to_dict()
        return base

    def __copy__(self):
        new_obj = RadianceShadeState(self._modifier)
        self._duplicate_shades(new_obj)
        new_obj._modifier_direct = self._modifier_direct
        return new_obj


class RadianceSubFaceState(_RadianceState):
    """Object representing a single state for a dynamic Aperture or Door.

    Args:
        modifier: A Honeybee Radiance Modifier object to be applied to this state's
            parent in this state. This is used to swap out the modifier in
            multi-phase studies. If None, it will be the parent's default modifier.
        shades: An optional array of StateGeometry objects to be included
            with this state. The StateGeometry objects cannot already have
            another parent state.

    Properties:
        * modifier
        * shades
        * modifier_direct
        * vmtx_geometry
        * dmtx_geometry
        * mtxs_default
        * parent
        * has_parent
    """
    __slots__ = ('_vmtx_geometry', '_dmtx_geometry')

    def __init__(self, modifier=None, shades=None):
        """Initialize RadianceSubFaceState."""
        _RadianceState.__init__(self, modifier, shades)
        self._vmtx_geometry = None
        self._dmtx_geometry = None

    @property
    def modifier_direct(self):
        """Get or set a modifier for the parent to be used in direct studies.

        If None, it will be the same as the modifier of this state. This property
        is only used in 2-phase and 5-phase studies and should usually be left
        as None in 2-phase studies. In 5-phase studies, this will be used for
        the 5th phase.
        """
        if not self._modifier_direct:  # use the state's default modifier
            return self.modifier
        return self._modifier_direct

    @modifier_direct.setter
    def modifier_direct(self, value):
        if value is not None:
            assert isinstance(value, Modifier), \
                'Expected Modifier for RadianceState. Got {}'.format(type(value))
            value.lock()  # lock editing in case modifier has multiple references
        self._modifier_direct = value

    @property
    def vmtx_geometry(self):
        """Get or set a Face3D to be used for the inward-facing vmtx file.

        If None, it will be a flipped (inward-facing) version of this state's parent.
        Note that this property is only used in 3-phase and 5-phase studies and
        its usual purpose is to account for thickness of the tmtx (BSDF) layer.
        Also note that the gen_geo_from_vmtx_offset or gen_geos_from_tmtx_thickness methods can be used to
        automatically generate this geometry without the need to set it here.
        """
        if not self._vmtx_geometry:  # use the inward-version of the parent geometry
            return self.parent.geometry.flip() if self.has_parent else None
        return self._vmtx_geometry

    @vmtx_geometry.setter
    def vmtx_geometry(self, value):
        if value is not None:
            assert isinstance(value, Face3D), \
                'Expected Face3D for RadianceSubFaceState vmtx_geometry. ' \
                    'Got {}'.format(type(value))
        self._vmtx_geometry = value

    @property
    def dmtx_geometry(self):
        """Get or set a Face3D to be used for the outward-facing dmtx file.

        If None, it will be a flipped (inward-facing) version of this state's parent.
        Note that this property is only used in 3-phase and 5-phase studies and
        its usual purpose is to account for thickness of the tmtx (BSDF) layer.
        Also note that the gen_geo_from_dmtx_offset or gen_geos_from_tmtx_thickness methods can be used to
        automatically generate this geometry without the need to set it here.
        """
        if not self._dmtx_geometry:  # use the inward-version of the parent geometry
            return self.parent.geometry.flip() if self.has_parent else None
        return self._dmtx_geometry

    @dmtx_geometry.setter
    def dmtx_geometry(self, value):
        if value is not None:
            assert isinstance(value, Face3D), \
                'Expected Face3D for RadianceSubFaceState dmtx_geometry. ' \
                    'Got {}'.format(type(value))
        self._dmtx_geometry = value

    @property
    def mtxs_default(self):
        """Get a boolean noting whether the vmtx_geometry and dmtx_geometry are None.
        
        This indicates that the vmtx_geometry and dmtx_geometry are both just a
        flipped version of the parent geometry.
        """
        return self._vmtx_geometry is None and self._dmtx_geometry is None

    def gen_geos_from_tmtx_thickness(self, thickness):
        """Auto-generate the vmtx_geometry and dmtx_geometry using a tmtx thickness.

        Args:
            thickness: A number for the thickness of the tmtx layer. The state's
                vmtx_geometry will be set to the the parent geometry moved half
                of this thickness inward. The dmtx_geometry will be set to the
                parent geometry moved half of this thickness outward.
        """
        assert self.has_parent, 'State must have a parent to use gen_geos_from_tmtx_thickness.'
        dist = thickness / 2
        out_vec = self.parent.normal * dist
        in_vec = out_vec.reverse()
        base_geo = self.parent.geometry.flip()
        self.dmtx_geometry = base_geo.move(out_vec)
        self.vmtx_geometry = base_geo.move(in_vec)

    def gen_geo_from_vmtx_offset(self, offset):
        """Auto-generate the vmtx_geometry using an offset from the parent geometry.

        Args:
            offset: A number for the offset of the vmtx layer from the parent geometry.
        """
        assert self.has_parent, 'State must have a parent to use gen_geo_from_vmtx_offset.'
        in_vec = self.parent.normal.reverse() * offset
        base_geo = self.parent.geometry.flip()
        self.vmtx_geometry = base_geo.move(in_vec)

    def gen_geo_from_dmtx_offset(self, offset):
        """Auto-generate the dmtx_geometry using an offset from the parent geometry.

        Args:
            offset: A number for the offset of the dmtx layer from the parent geometry.
        """
        assert self.has_parent, 'State must have a parent to use gen_geo_from_dmtx_offset.'
        out_vec = self.parent.normal * offset
        base_geo = self.parent.geometry.flip()
        self.vmtx_geometry = base_geo.move(out_vec)

    def move(self, moving_vec):
        """Move all shades and mtx geometry assigned to this state along a vector.

        Args:
            moving_vec: A ladybug_geometry Vector3D with the direction and distance
                to move the shades.
        """
        for shd in self._shades:
            shd.move(moving_vec)
        if self._vmtx_geometry:
            self._vmtx_geometry = self._vmtx_geometry.move(moving_vec)
        if self._dmtx_geometry:
            self._dmtx_geometry = self._dmtx_geometry.move(moving_vec)

    def rotate(self, axis, angle, origin):
        """Rotate all shades and mtx geometry assigned to this state.

        Args:
            axis: A ladybug_geometry Vector3D axis representing the axis of rotation.
            angle: An angle for rotation in degrees.
            origin: A ladybug_geometry Point3D for the origin around which the
                object will be rotated.
        """
        for shd in self._shades:
            shd.rotate(axis, angle, origin)
        if self._vmtx_geometry:
            self._vmtx_geometry = self._vmtx_geometry.rotate(
                axis, math.radians(angle), origin)
        if self._dmtx_geometry:
            self._dmtx_geometry = self._dmtx_geometry.rotate(
                axis, math.radians(angle), origin)

    def rotate_xy(self, angle, origin):
        """Rotate all shades and mtx geometry counterclockwise in the world XY plane.

        Args:
            angle: An angle in degrees.
            origin: A ladybug_geometry Point3D for the origin around which the
                object will be rotated.
        """
        for shd in self._shades:
            shd.rotate_xy(angle, origin)
        if self._vmtx_geometry:
            self._vmtx_geometry = self._vmtx_geometry.rotate_xy(
                math.radians(angle), origin)
        if self._dmtx_geometry:
            self._dmtx_geometry = self._dmtx_geometry.rotate_xy(
                math.radians(angle), origin)

    def reflect(self, plane):
        """Reflect all shades and mtx geometry assigned to this state across a plane.

        Args:
            plane: A ladybug_geometry Plane across which the object will
                be reflected.
        """
        for shd in self._shades:
            shd.reflect(plane)
        if self._vmtx_geometry:
            self._vmtx_geometry = self._vmtx_geometry.reflect(plane.n, plane.o)
        if self._dmtx_geometry:
            self._dmtx_geometry = self._dmtx_geometry.reflect(plane.n, plane.o)

    def scale(self, factor, origin=None):
        """Scale all shades and mtx geometry assigned to this state by a factor.

        Args:
            factor: A number representing how much the object should be scaled.
            origin: A ladybug_geometry Point3D representing the origin from which
                to scale. If None, it will be scaled from the World origin (0, 0, 0).
        """
        for shd in self._shades:
            shd.scale(factor, origin)
        if self._vmtx_geometry:
            self._vmtx_geometry = self._vmtx_geometry.scale(factor, origin)
        if self._dmtx_geometry:
            self._dmtx_geometry = self._dmtx_geometry.scale(factor, origin)

    def vmtx_to_radiance(self, modifier=white_glow, minimal=False):
        """Generate a RAD string representation of this state's vmtx.

        The resulting string lacks modifiers and only includes the vmtx_geometry.

        Args:
            modifier: A modifier object assigned to the vmtx_geometry. Default: white_glow.
            minimal: Boolean to note whether the radiance string should be written
                in a minimal format (with spaces instead of line breaks). Default: False.
        """
        assert self.has_parent, 'State must have a parent to use vmtx_to_radiance.'
        vmtx_poly = Polygon(self.parent.identifier,
                            self.vmtx_geometry.vertices, modifier)
        return vmtx_poly.to_radiance(minimal, False, False)

    def dmtx_to_radiance(self, minimal=False):
        """Generate a RAD string representation of this state's dmtx.

        The resulting string lacks modifiers and only includes the dmtx_geometry.

        Args:
            minimal: Boolean to note whether the radiance string should be written
                in a minimal format (with spaces instead of line breaks). Default: False.
        """
        assert self.has_parent, 'State must have a parent to use dmtx_to_radiance.'
        dmtx_poly = Polygon(self.parent.identifier,
                            self.dmtx_geometry.vertices, white_glow)
        return dmtx_poly.to_radiance(minimal, False, False)
    
    @classmethod
    def from_dict(cls, data):
        """Create RadianceSubFaceState from a dictionary.

        Note that the dictionary must be a non-abridged version for this
        classmethod to work.

        Args:
            data: A dictionary representation of RadianceSubFaceState with the
                format below.

        .. code-block:: python

            {
            'type': 'RadianceSubFaceState',
            'modifier': {},  # A Honeybee Radiance Modifier dictionary
            'shades': [],  # A list of abridged StateGeometry dictionaries
            'modifier_direct': {},  # A Honeybee Radiance Modifier dictionary
            'vmtx_geometry': {},  # A Face3D for the view matrix geometry
            'dmtx_geometry': {}  # A Face3D for the daylight matrix geometry
            }
        """
        assert data['type'] == 'RadianceSubFaceState', \
            'Expected RadianceSubFaceState. Got {}.'.format(data['type'])
        new_state = cls()
        if 'modifier' in data and data['modifier'] is not None:
            new_state.modifier = dict_to_modifier(data['modifier'])
        if 'shades' in data and data['shades'] is not None:
            new_state.shades = [StateGeometry.from_dict(shd) for shd in data['shades']]
        if 'modifier_direct' in data and data['modifier_direct'] is not None:
            new_state.modifier_direct = dict_to_modifier(data['modifier_direct'])
        if 'vmtx_geometry' in data and data['vmtx_geometry'] is not None:
            new_state.vmtx_geometry = Face3D.from_dict(data['vmtx_geometry'])
        if 'dmtx_geometry' in data and data['dmtx_geometry'] is not None:
            new_state.dmtx_geometry = Face3D.from_dict(data['dmtx_geometry'])
        return new_state

    @classmethod
    def from_dict_abridged(cls, data, modifiers):
        """Create RadianceSubFaceState from an abridged dictionary.

        Note that the dictionary must be a non-abridged version for this
        classmethod to work.

        Args:
            data: A dictionary representation of RadianceSubFaceStateAbridged
                with the format below.
            modifiers: A dictionary of modifiers with modifier identifiers as keys,
                which will be used to re-assign modifiers.

        .. code-block:: python

            {
            'type': 'RadianceSubFaceStateAbridged',
            'modifier': str,  # An identifier of a honeybee-radiance modifier
            'shades': [],  # A list of abridged StateGeometry dictionaries
            'modifier_direct': str,  # An identifier of a honeybee-radiance modifier
            'vmtx_geometry': {},  # A Face3D for the view matrix geometry
            'dmtx_geometry': {}  # A Face3D for the daylight matrix geometry
            }
        """
        assert data['type'] == 'RadianceSubFaceStateAbridged', \
            'Expected RadianceSubFaceStateAbridged. Got {}.'.format(data['type'])
        new_state = cls()
        if 'modifier' in data and data['modifier'] is not None:
            new_state.modifier = modifiers[data['modifier']]
        if 'shades' in data and data['shades'] is not None:
            new_state.shades = [StateGeometry.from_dict_abridged(shd, modifiers)
                                for shd in data['shades']]
        if 'modifier_direct' in data and data['modifier_direct'] is not None:
            new_state.modifier_direct = modifiers[data['modifier_direct']]
        if 'vmtx_geometry' in data and data['vmtx_geometry'] is not None:
            new_state.vmtx_geometry = Face3D.from_dict(data['vmtx_geometry'])
        if 'dmtx_geometry' in data and data['dmtx_geometry'] is not None:
            new_state.dmtx_geometry = Face3D.from_dict(data['dmtx_geometry'])
        return new_state

    def to_dict(self, abridged=False):
        """Convert RadianceSubFaceState to a dictionary.

        Args:
            abridged: Boolean to note whether the full dictionary describing the
                object should be returned (False) or just an abridged version (True).
                Default: False.
        """
        base = {'type': 'RadianceSubFaceStateAbridged'} if abridged else \
            {'type': 'RadianceSubFaceState'}
        if self._modifier:
            base['modifier'] = self._modifier.identifier if abridged else \
                self._modifier.to_dict()
        if len(self._shades) != 0:
            base['shades'] = [shd.to_dict(abridged=abridged) for shd in self.shades]
        if self._modifier_direct is not None:
            base['modifier_direct'] = self._modifier_direct.identifier if abridged \
                else self._modifier.to_dict()
        if self._vmtx_geometry is not None:
            base['vmtx_geometry'] = self._vmtx_geometry.to_dict()
        if self._dmtx_geometry is not None:
            base['dmtx_geometry'] = self._dmtx_geometry.to_dict()
        return base

    def __copy__(self):
        new_obj = RadianceSubFaceState(self._modifier)
        self._duplicate_shades(new_obj)
        new_obj._modifier_direct = self._modifier_direct
        new_obj._vmtx_geometry = self._vmtx_geometry
        new_obj._dmtx_geometry = self._dmtx_geometry
        return new_obj
