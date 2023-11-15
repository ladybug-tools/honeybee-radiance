# coding=utf-8
"""ShadeMesh Radiance Properties."""
from ._base import _RadianceProperties
from ..modifier import Modifier
from ..lib.modifiers import generic_context
from ..lib.modifiersets import generic_modifier_set_visible


class ShadeMeshRadianceProperties(_RadianceProperties):
    """Radiance Properties for Honeybee ShadeMesh.

    Args:
        host: A honeybee_core ShadeMesh object that hosts these properties.
        modifier: A Honeybee Radiance Modifier object for the shade mesh. If None,
            it will be set by the default generic ModifierSet.
        modifier_blk: A Honeybee Radiance Modifier object to be used for this
            shade mesh in direct solar simulations and in isolation studies (assessing
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
        """Initialize ShadeMesh radiance properties."""
        _RadianceProperties.__init__(self, host, modifier, modifier_blk)

    @property
    def modifier(self):
        """Get or set the ShadeMesh modifier.

        If the modifier is not set on the shade-level, then it will be the
        generic context material or the generic exterior shade modifier if it
        is not detached.
        """
        if self._modifier:  # set by user
            return self._modifier
        return generic_context if self._host.is_detached else \
            generic_modifier_set_visible.shade_set.exterior_modifier

    @modifier.setter
    def modifier(self, value):
        if value is not None:
            assert isinstance(value, Modifier), \
                'Expected Radiance Modifier for ShadeMesh. Got {}'.format(type(value))
            value.lock()  # lock editing in case modifier has multiple references
        self._modifier = value

    @classmethod
    def from_dict(cls, data, host):
        """Create ShadeMeshRadianceProperties from a dictionary.

        Note that the dictionary must be a non-abridged version for this
        classmethod to work.

        Args:
            data: A dictionary representation of ShadeMeshRadianceProperties with the
                format below.
            host: A ShadeMesh object that hosts these properties.

        .. code-block:: python

            {
            'type': 'ShadeMeshRadianceProperties',
            'modifier': {},  # A Honeybee Radiance Modifier dictionary
            'modifier_blk': {}  # A Honeybee Radiance Modifier dictionary
            }
        """
        assert data['type'] == 'ShadeMeshRadianceProperties', \
            'Expected ShadeMeshRadianceProperties. Got {}.'.format(data['type'])
        new_prop = cls(host)
        return cls._restore_modifiers_from_dict(new_prop, data)

    def apply_properties_from_dict(self, abridged_data, modifiers):
        """Apply properties from a ShadeMeshRadiancePropertiesAbridged dictionary.

        Args:
            abridged_data: A ShadeMeshRadiancePropertiesAbridged dictionary (typically
                coming from a Model) with the format below.
            modifiers: A dictionary of modifiers with modifier identifiers as keys,
                which will be used to re-assign modifiers.

        .. code-block:: python

            {
            'type': 'ShadeMeshRadiancePropertiesAbridged',
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
        base['radiance']['type'] = 'ShadeMeshRadianceProperties' if not \
            abridged else 'ShadeMeshRadiancePropertiesAbridged'
        return self._add_modifiers_to_dict(base, abridged)

    def __repr__(self):
        return 'ShadeMesh Radiance Properties:\n host: {}'.format(self.host.identifier)
