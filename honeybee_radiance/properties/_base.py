# coding=utf-8
"""Base class of Radiance Properties for all planar geometry objects."""
from ..modifier import Modifier
from ..mutil import dict_to_modifier  # imports all modifiers classes
from ..dynamic.state import _RadianceState
from ..lib.modifiers import black

from honeybee.typing import valid_rad_string


class _RadianceProperties(object):
    """Base class of Radiance Properties for all planar geometry objects.

    This includes (Face, Aperture, Door, Shade).

    Args:
        host: A honeybee_core object that hosts these properties.
        modifier: A Honeybee Radiance Modifier for the object. If None,
            it will be set by the parent Room ModifierSet or the Honeybee
            default generic ModifierSet.
        modifier_blk: A Honeybee Radiance Modifier to be used for this object
            in direct solar simulations and in isolation studies (assessing
            the contribution of individual Apertures).

    Properties:
        * host
        * modifier
        * modifier_blk
        * is_opaque
        * is_modifier_set_on_object
        * is_blk_overridden
    """

    __slots__ = ('_host', '_modifier', '_modifier_blk')

    def __init__(self, host, modifier=None, modifier_blk=None):
        """Initialize GeometryRadianceProperties."""
        self._host = host
        self.modifier = modifier
        self.modifier_blk = modifier_blk

    @property
    def host(self):
        """Get the object hosting these properties."""
        return self._host

    @property
    def modifier(self):
        """Get or set the object modifier."""
        return self._modifier

    @modifier.setter
    def modifier(self, value):
        if value is not None:
            assert isinstance(value, Modifier), \
                'Expected Radiance Modifier for shade. Got {}'.format(type(value))
            value.lock()  # lock editing in case modifier has multiple references
        self._modifier = value

    @property
    def modifier_blk(self):
        """Get or set a modifier to be used in direct solar and in isolation studies.

        If None, this will be a completely black material if the object's modifier is
        opaque and will be equal to the modifier if the object's modifier is non-opaque.
        """
        if self._modifier_blk:  # set by user
            return self._modifier_blk
        mod = self.modifier  # assign a default based on whether the modifier is opaque
        if mod.is_void or mod.is_opaque:
            return black
        else:
            return mod

    @modifier_blk.setter
    def modifier_blk(self, value):
        if value is not None:
            assert isinstance(value, Modifier), \
                'Expected Radiance Modifier. Got {}'.format(type(value))
            value.lock()  # lock editing in case modifier has multiple references
        self._modifier_blk = value

    @property
    def is_opaque(self):
        """Boolean noting whether this object has an opaque modifier.

        This has repercussions for how this object is written into the Radiance
        folder structure.
        """
        return True if self.modifier.is_void else self.modifier.is_opaque

    @property
    def is_modifier_set_on_object(self):
        """Boolean noting if modifier is assigned on the level of this object.

        This is opposed to having the modifier assigned by a ModifierSet.
        """
        return self._modifier is not None

    @property
    def is_blk_overridden(self):
        """Boolean noting if modifier_blk has been overridden from default on this object.
        """
        return self._modifier is not None

    def reset_to_default(self):
        """Reset a Modifier assigned at the level of this Shade to the default.

        This means that the Shade's modifier will be assigned by a ModifierSet instead.
        """
        self._modifier = None

    def duplicate(self, new_host=None):
        """Get a copy of this object.

        new_host: A new object that hosts these properties.
            If None, the properties will be duplicated with the same host.
        """
        _host = new_host or self._host
        return self.__class__(_host, self._modifier, self._modifier_blk)

    def _apply_modifiers_from_dict(self, abridged_data, modifiers):
        """Apply modifiers from an Abridged dictionary.

        Args:
            abridged_data: An Abridged dictionary (typically coming from a Model).
            modifiers: A dictionary of modifiers with modifier identifiers as keys,
                which will be used to re-assign modifiers.
        """
        if 'modifier' in abridged_data and abridged_data['modifier'] is not None:
            self.modifier = modifiers[abridged_data['modifier']]
        if 'modifier_blk' in abridged_data and abridged_data['modifier_blk'] is not None:
            self.modifier_blk = modifiers[abridged_data['modifier_blk']]

    def _add_modifiers_to_dict(self, base, abridged=False):
        """Add modifiers to a base dictionary.

        Args:
            base: A base dictionary to which modifiers will be added.
            abridged: Boolean to note whether the full dictionary describing the
                object should be returned (False) or just an abridged version (True).
                Default: False.
        """
        if self._modifier is not None:
            base['radiance']['modifier'] = self._modifier.identifier if \
                abridged else self._modifier.to_dict()
        if self._modifier_blk is not None:
            base['radiance']['modifier_blk'] = self._modifier_blk.identifier if \
                abridged else self._modifier_blk.to_dict()
        return base

    @staticmethod
    def _restore_modifiers_from_dict(new_prop, data):
        """Restore modifiers from a data dictionary to a new properties object."""
        if 'modifier' in data and data['modifier'] is not None:
            new_prop.modifier = dict_to_modifier(data['modifier'])
        if 'modifier_blk' in data and data['modifier_blk'] is not None:
            new_prop.modifier_blk = dict_to_modifier(data['modifier_blk'])
        return new_prop

    def ToString(self):
        return self.__repr__()

    def __repr__(self):
        return 'Base Radiance Properties: [host: {}]'.format(self.host.display_name)


class _DynamicRadianceProperties(_RadianceProperties):
    """Base class of Radiance Properties for all planar geometry objects.

    This includes Apertures and Shades.

    Args:
        host: A honeybee_core object that hosts these properties.
        modifier: A Honeybee Radiance Modifier for the object. If None,
            it will be set by the parent Room ModifierSet or the Honeybee
            default generic ModifierSet.
        modifier_blk: A Honeybee Radiance Modifier to be used for this object
            in direct solar simulations and in isolation studies (assessing
            the contribution of individual Apertures).
        dynamic_group_identifier: An optional string to note the dynamic group
            to which the object is a part of. Objects sharing the same
            dynamic_group_identifier will have their states change in unison.
            If None, the object is assumed to be static.

    Properties:
        * host
        * modifier
        * modifier_blk
        * dynamic_group_identifier
        * states
        * state_count
        * is_opaque
        * is_modifier_set_on_object
        * is_blk_overridden
    """

    __slots__ = ('_dynamic_group_identifier', '_states')

    def __init__(self, host, modifier=None, modifier_blk=None,
                 dynamic_group_identifier=None):
        """Initialize radiance properties."""
        _RadianceProperties.__init__(self, host, modifier, modifier_blk)
        self._states = []
        self.dynamic_group_identifier = dynamic_group_identifier

    @property
    def dynamic_group_identifier(self):
        """Get or set a text string for the dynamic_group_identifier.

        Objects sharing the same dynamic_group_identifier will have their
        states change in unison. If None, the object is assumed to be static.
        """
        return self._dynamic_group_identifier

    @dynamic_group_identifier.setter
    def dynamic_group_identifier(self, identifier):
        if identifier is not None:
            identifier = valid_rad_string(identifier)
        else:
            assert len(self._states) == 0, 'dynamic_group_identifier cannot be ' \
                'None while states are assigned. Use the remove_states method ' \
                'before setting to None.'
        self._dynamic_group_identifier = identifier

    @property
    def states(self):
        """Get or set an array of radiance states assigned to this object.

        These cannot be set unless there is also a dynamic_group_identifier for
        the object.
        """
        return tuple(self._states)

    @states.setter
    def states(self, value):
        if value is not None:
            assert self._dynamic_group_identifier is not None, 'Object must have ' \
                'a dynamic_group_identifier to assign states.'
            try:
                self._states = [self._check_state(st) for st in value]
            except (ValueError, TypeError):
                raise TypeError('Expected iterable for Object states. '
                                'Got  {}.'.format(type(value)))
        else:
            self._states = []

    @property
    def state_count(self):
        """Get an integer for the number of dynamic states assigned to the object."""
        return len(self._states)

    def remove_states(self):
        """Remove all states assigned to this object."""
        for state in self._states:
            state._parent = None
        self._states = []

    def add_state(self, state):
        """Add a Radiance state object to this object.

        Args:
            state: A Radiance state object to add to the this object.
        """
        assert self._dynamic_group_identifier is not None, 'Object must have ' \
            'a dynamic_group_identifier to assign states.'
        self._states.append(self._check_state(state))

    def move(self, moving_vec):
        """Move all state geometry along a vector.

        Args:
            moving_vec: A ladybug_geometry Vector3D with the direction and distance
                to move the shades.
        """
        for state in self._states:
            state.move(moving_vec)

    def rotate(self, axis, angle, origin):
        """Rotate all state geometry.

        Args:
            axis: A ladybug_geometry Vector3D axis representing the axis of rotation.
            angle: An angle for rotation in degrees.
            origin: A ladybug_geometry Point3D for the origin around which the
                object will be rotated.
        """
        for state in self._states:
            state.rotate(axis, angle, origin)

    def rotate_xy(self, angle, origin):
        """Rotate all state geometry counterclockwise in the world XY plane.

        Args:
            angle: An angle in degrees.
            origin: A ladybug_geometry Point3D for the origin around which the
                object will be rotated.
        """
        for state in self._states:
            state.rotate_xy(angle, origin)

    def reflect(self, plane):
        """Reflect all state geometry across a plane.

        Args:
            plane: A ladybug_geometry Plane across which the object will
                be reflected.
        """
        for state in self._states:
            state.reflect(plane)

    def scale(self, factor, origin=None):
        """Scale all state geometry by a factor.

        Args:
            factor: A number representing how much the object should be scaled.
            origin: A ladybug_geometry Point3D representing the origin from which
                to scale. If None, it will be scaled from the World origin (0, 0, 0).
        """
        for state in self._states:
            state.scale(factor, origin)

    def duplicate(self, new_host=None):
        """Get a copy of this object.

        new_host: A new object that hosts these properties.
            If None, the properties will be duplicated with the same host.
        """
        _host = new_host or self._host
        new_prop = self.__class__(
            _host, self._modifier, self._modifier_blk, self._dynamic_group_identifier)
        new_prop._states = []
        for st in self._states:
            new_st = st.duplicate()
            new_st._parent = _host
            new_prop._states.append(new_st)
        return new_prop

    def _check_state(self, obj):
        assert isinstance(obj, _RadianceState), \
            'Expected RadianceState. Got {}.'.format(type(obj))
        assert obj.parent is None, \
            'RadianceState cannot already have a parent object.'
        obj._parent = self.host
        return obj

    def _add_states_to_dict(self, base, abridged=False):
        """Add states to a base dictionary.

        Args:
            base: A base dictionary to which states will be added.
            abridged: Boolean to note whether the full dictionary describing the
                object should be returned (False) or just an abridged version (True).
                Default: False.
        """
        if self._dynamic_group_identifier is not None:
            base['radiance']['dynamic_group_identifier'] = self.dynamic_group_identifier
        if len(self._states) != 0:
            base['radiance']['states'] = [st.to_dict(abridged) for st in self._states]
        return base
