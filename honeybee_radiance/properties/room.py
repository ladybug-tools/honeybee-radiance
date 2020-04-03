# coding=utf-8
"""Room Radiance Properties."""
from ..modifierset import ModifierSet
from ..lib.modifiersets import generic_modifier_set_visible


class RoomRadianceProperties(object):
    """Radiance Properties for Honeybee Room.

    Args:
        host: A honeybee_core Room object that hosts these properties.
        modifier_set: A honeybee ModifierSet object to specify all default
            modifiers for the Faces of the Room. If None, the Room will use
            the honeybee default modifier set, which is only representitive
            of typical indoor conditions in the visible spectrum. Default: None.

    Properties:
        * host
        * modifier_set
    """

    __slots__ = ('_host', '_modifier_set')

    def __init__(self, host, modifier_set=None):
        """Initialize Room radiance properties."""
        # set the main properties of the Room
        self._host = host
        self.modifier_set = modifier_set

    @property
    def host(self):
        """Get the Room object hosting these properties."""
        return self._host

    @property
    def modifier_set(self):
        """Get or set the Room ModifierSet object.

        If not set, it will be the Honeybee default generic ModifierSet.
        """
        if self._modifier_set is not None:  # set by the user
            return self._modifier_set
        else:
            return generic_modifier_set_visible

    @modifier_set.setter
    def modifier_set(self, value):
        if value is not None:
            assert isinstance(value, ModifierSet), \
                'Expected ModifierSet. Got {}'.format(type(value))
            value.lock()   # lock in case modifier set has multiple references
        self._modifier_set = value

    @classmethod
    def from_dict(cls, data, host):
        """Create RoomRadianceProperties from a dictionary.

        Note that the dictionary must be a non-abridged version for this
        classmethod to work.

        Args:
            data: A dictionary representation of RoomRadianceProperties with the
                format below.
            host: A Room object that hosts these properties.

        .. code-block:: python

            {
            'type': 'RoomRadianceProperties',
            'modifier_set': {},  # ModifierSet dictionary
            }
        """
        assert data['type'] == 'RoomRadianceProperties', \
            'Expected RoomRadianceProperties. Got {}.'.format(data['type'])

        new_prop = cls(host)
        if 'modifier_set' in data and data['modifier_set'] is not None:
            new_prop.modifier_set = ModifierSet.from_dict(data['modifier_set'])
        return new_prop

    def apply_properties_from_dict(self, abridged_data, modifier_sets):
        """Apply properties from a RoomRadiancePropertiesAbridged dictionary.

        Args:
            abridged_data: A RoomRadiancePropertiesAbridged dictionary (typically
                coming from a Model) with the format below.
            modifier_sets: A dictionary of ModifierSets with identifiers of the sets
                as keys, which will be used to re-assign modifier_sets.

        .. code-block:: python

            {
            'type': 'RoomRadiancePropertiesAbridged',
            'modifier_set': str,  # ModifierSet identifier
            }
        """
        if 'modifier_set' in abridged_data and abridged_data['modifier_set'] is not None:
            self.modifier_set = modifier_sets[abridged_data['modifier_set']]

    def to_dict(self, abridged=False):
        """Return Room radiance properties as a dictionary.

        Args:
            abridged: Boolean for whether the full dictionary of the Room should
                be written (False) or just the identifier of the the individual
                properties (True). Default: False.
        """
        base = {'radiance': {}}
        base['radiance']['type'] = 'RoomRadianceProperties' if not \
            abridged else 'RoomRadiancePropertiesAbridged'

        # write the ModifierSet into the dictionary
        if self._modifier_set is not None:
            base['radiance']['modifier_set'] = \
                self._modifier_set.identifier if abridged else \
                self._modifier_set.to_dict()

        return base

    def duplicate(self, new_host=None):
        """Get a copy of this object.

        Args:
            new_host: A new Room object that hosts these properties.
                If None, the properties will be duplicated with the same host.
        """
        _host = new_host or self._host
        new_room = RoomRadianceProperties(_host, self._modifier_set)
        return new_room

    def ToString(self):
        return self.__repr__()

    def __repr__(self):
        return 'Room Radiance Properties:\n host: {}'.format(self.host.identifier)
