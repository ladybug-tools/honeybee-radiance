# coding=utf-8
"""Shade Radiance Properties."""
from ._base import _GeometryRadianceProperties
from ..modifier import Modifier
from ..lib.modifiers import generic_context
from ..lib.modifiersets import generic_modifier_set_visible


class ShadeRadianceProperties(_GeometryRadianceProperties):
    """Radiance Properties for Honeybee Shade.

    Args:
        host: A honeybee_core Shade object that hosts these properties.
        modifier: A Honeybee Radiance Modifier object for the shade. If None,
            it will be set by the parent Room ModifierSet or the Honeybee
            default generic ModifierSet.
        modifier_blk: A Honeybee Radiance Modifier object to be used for this
            shade in direct solar simulations and in isolation studies (assessing
            the contribution of individual Apertures). If None, this will be
            a completely black material if the Shade's modifier is opaque and
            will be equal to the modifier if the Shade's modifier is non-opaque.

    Properties:
        * host
        * modifier
        * modifier_blk
        * is_opaque
        * is_modifier_set_on_object
        * is_blk_overridden
    """

    __slots__ = ()

    def __init__(self, host, modifier=None, modifier_blk=None):
        """Initialize Shade radiance properties."""
        _GeometryRadianceProperties.__init__(self, host, modifier, modifier_blk)

    @property
    def modifier(self):
        """Get or set the Shade modifier.

        If the modifier is not set on the shade-level, then it will be assigned
        based on the ModifierSet assigned to the parent Room.  If the parent Room's
        ModifierSet has no modifier for the Shade type, it will be assigned using the
        honeybee default generic ModifierSet. If there is no parent Room, it will
        be the generic context material.
        """
        if self._modifier:  # set by user
            return self._modifier
        elif not self._host.has_parent:  # orphaned shade
            return generic_context
        else:  # shade with a parent
            m_set = self._parent_modifier_set(self._host.parent)
            if m_set is None:
                m_set = generic_modifier_set_visible
        return m_set.get_shade_modifier(self._host.is_indoor)

    @modifier.setter
    def modifier(self, value):
        if value is not None:
            assert isinstance(value, Modifier), \
                'Expected Radiance Modifier for shade. Got {}'.format(type(value))
            value.lock()  # lock editing in case modifier has multiple references
        self._modifier = value

    @classmethod
    def from_dict(cls, data, host):
        """Create ShadeRadianceProperties from a dictionary.

        Note that the dictionary must be a non-abridged version for this
        classmethod to work.

        Args:
            data: A dictionary representation of ShadeRadianceProperties with the
                format below.
            host: A Shade object that hosts these properties.

        .. code-block:: python

            {
            'type': 'ShadeRadianceProperties',
            'modifier': {},  # A Honeybee Radiance Modifier dictionary
            'modifier_blk': {}  # A Honeybee Radiance Modifier dictionary
            }
        """
        assert data['type'] == 'ShadeRadianceProperties', \
            'Expected ShadeRadianceProperties. Got {}.'.format(data['type'])
        new_prop = cls(host)
        return cls._restore_modifiers_from_dict(new_prop, data)

    def apply_properties_from_dict(self, abridged_data, modifiers):
        """Apply properties from a ShadeRadiancePropertiesAbridged dictionary.

        Args:
            abridged_data: A ShadeRadiancePropertiesAbridged dictionary (typically
                coming from a Model) with the format below.
            modifiers: A dictionary of modifiers with modifier identifiers as keys,
                which will be used to re-assign modifiers.

        .. code-block:: python

            {
            'type': 'ShadeRadiancePropertiesAbridged',
            'modifier': str,  # A Honeybee Radiance Modifier identifier
            'modifier_blk': str  # A Honeybee Radiance Modifier identifier
            }
        """
        self._apply_modifiers_from_dict(abridged_data, modifiers)

    def to_dict(self, abridged=False):
        """Return radiance properties as a dictionary.

        Args:
            abridged: Boolean to note whether the full dictionary describing the
                object should be returned (False) or just an abridged version (True).
                Default: False.
        """
        base = {'radiance': {}}
        base['radiance']['type'] = 'ShadeRadianceProperties' if not \
            abridged else 'ShadeRadiancePropertiesAbridged'
        return self._add_modifiers_to_dict(base, abridged)

    @staticmethod
    def _parent_modifier_set(host_parent):
        """Recursively search through host parents to find a ModifierSet."""
        if hasattr(host_parent.properties.radiance, 'modifier_set'):
            return host_parent.properties.radiance.modifier_set
        elif host_parent.has_parent:
            return ShadeRadianceProperties._parent_modifier_set(host_parent.parent)
        else:
            return None

    def __repr__(self):
        return 'Shade Radiance Properties:\n host: {}'.format(self.host.identifier)
