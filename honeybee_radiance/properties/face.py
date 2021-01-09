# coding=utf-8
"""Face Radiance Properties."""
from ._base import _RadianceProperties
from ..modifier import Modifier
from ..lib.modifiersets import generic_modifier_set_visible


class FaceRadianceProperties(_RadianceProperties):
    """Radiance Properties for Honeybee Face.

    Args:
        host: A honeybee_core Face object that hosts these properties.
        modifier: A Honeybee Radiance Modifier object for the face. If None,
            it will be set by the parent Room ModifierSet or the Honeybee
            default generic ModifierSet.
        modifier_blk: A Honeybee Radiance Modifier object to be used for this
            face in direct solar simulations and in isolation studies (assessing
            the contribution of individual Apertures). If None, this will be
            a completely black material if the Face's modifier is opaque and
            will be equal to the modifier if the Face's modifier is non-opaque.

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
        """Initialize Face radiance properties."""
        _RadianceProperties.__init__(self, host, modifier, modifier_blk)

    @property
    def modifier(self):
        """Get or set the Face modifier.

        If the modifier is not set on the face-level, then it will be assigned
        based on the ModifierSet assigned to the parent Room.  If there is no
        parent Room or the parent Room's ModifierSet has no modifier for
        the Face type and boundary_condition, it will be assigned using the
        honeybee default generic ModifierSet.
        """
        if self._modifier:  # set by user
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
        if value is not None:
            assert isinstance(value, Modifier), \
                'Expected Radiance Modifier for face. Got {}'.format(type(value))
            value.lock()  # lock editing in case modifier has multiple references
        self._modifier = value

    @classmethod
    def from_dict(cls, data, host):
        """Create FaceRadianceProperties from a dictionary.

        Note that the dictionary must be a non-abridged version for this
        classmethod to work.

        Args:
            data: A dictionary representation of FaceRadianceProperties with the
                format below.
            host: A Face object that hosts these properties.

        .. code-block:: python

            {
            'type': 'FaceRadianceProperties',
            'modifier': {},  # A Honeybee Radiance Modifier dictionary
            'modifier_blk': {}  # A Honeybee Radiance Modifier dictionary
            }
        """
        assert data['type'] == 'FaceRadianceProperties', \
            'Expected FaceRadianceProperties. Got {}.'.format(data['type'])
        new_prop = cls(host)
        return cls._restore_modifiers_from_dict(new_prop, data)

    def apply_properties_from_dict(self, abridged_data, modifiers):
        """Apply properties from a FaceRadiancePropertiesAbridged dictionary.

        Args:
            abridged_data: A FaceRadiancePropertiesAbridged dictionary (typically
                coming from a Model) with the format below.
            modifiers: A dictionary of modifiers with modifier identifiers as keys,
                which will be used to re-assign modifiers.

        .. code-block:: python

            {
            'type': 'FaceRadiancePropertiesAbridged',
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
        base['radiance']['type'] = 'FaceRadianceProperties' if not \
            abridged else 'FaceRadiancePropertiesAbridged'
        return self._add_modifiers_to_dict(base, abridged)

    def __repr__(self):
        return 'Face Radiance Properties: [host: {}]'.format(self.host.display_name)
