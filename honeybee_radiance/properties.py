"""Radiance Properties."""
from honeybee_radiance.lib.modifiersets import generic_modifier_set_visible
from honeybee_radiance.primitive import Primitive


class FaceRadianceProperties(object):
    """Radiance Properties for Honeybee Face."""

    __slots__ = ('_host', '_modifier', '_modifier_dir')

    def __init__(self, host, modifier=None, modifier_direct=None):
        self._host = host
        # this will be set by user
        self._modifier = None
        self._modifier_dir = None

    @property
    def host(self):
        """Get the Face object hosting these properties."""
        return self._host

    @property
    def modifier(self):
        """Set or get Face modifier / material.

        If the modifier is not set on the face-level, then it will be assigned
        based on the ModifierSet assigned to the parent Room.  If there is no
        parent Room or the the parent Room's ModifierSet has no modifier for
        the Face type and boundary_condition, it will be assigned using the honeybee
        default generic material set.
        """
        if self._modifier:
            # set by user
            return self._modifier
        elif self._host.has_parent:  # set by parent room
            modifier_set = self._host.parent.properties.radiance.modifier_set
            return modifier_set.get_face_modifier(
                self._host.type.name, self._host.boundary_condition.name)
        else:
            return generic_modifier_set_visible.get_face_modifier(
                self._host.type.name, self._host.boundary_condition.name)

    @modifier.setter
    def modifier(self, value):
        if isinstance(value, Primitive) and value.is_modifier:
                self._modifier = value
        else:
            raise TypeError(
                '{} is not a valid Radiance modifier.'.format(type(value))
            )

    @property
    def is_modifier_set_by_user(self):
        """Check if modifier is set by user."""
        return self._modifier is not None

    # TODO: Update this based on material-set
    @property
    def modifier_dir(self):
        """Radiance modifier for direct sunlight studies."""
        return self._modifier_dir

    @modifier_dir.setter
    def modifier_dir(self, value):
        if isinstance(value, Primitive) and value.is_modifier:
                self._modifier_dir = value
        else:
            raise TypeError(
                '{} is not a valid Radiance modifier.'.format(type(value))
            )
    
    #TODO: Update based on material-set
    def to_dict(self):
        """Return radiance properties as a dictionary."""
        base = {'radiance': {}}
        base['radiance']['modifier'] = self.modifier.to_dict() if self.modifier else None
        base['radiance']['modifier_dir'] = \
            self.modifier_dir.to_dict() if self.modifier_dir else None
        return base

    def duplicate(self, new_host=None):
        """Get a copy of this object.

        Args:
            new_host: A new Face object that hosts these properties.
                If None, the properties will be duplicated with the same host.
        """
        host = new_host or self._host
        return FaceRadianceProperties(host, self._modifier, self._modifier_dir)

    def ToString(self):
        return self.__repr__()

    def __repr__(self):
        return 'FaceRadianceProperties:\nModifier:{}'.format(self.modifier.name)
