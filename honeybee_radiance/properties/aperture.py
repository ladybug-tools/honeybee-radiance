# coding=utf-8
"""Aperture Radiance Properties."""
from ._base import _GeometryRadianceProperties
from ..modifier import Modifier
from ..lib.modifiers import black
from ..lib.modifiersets import generic_modifier_set_visible


class ApertureRadianceProperties(_GeometryRadianceProperties):
    """Radiance Properties for Honeybee Aperture.

    Args:
        host: A honeybee_core Aperture object that hosts these properties.
        modifier: A Honeybee Radiance Modifier object for the aperture. If None,
            it will be set by the parent Room ModifierSet or the Honeybee
            default generic ModifierSet.
        modifier_blk: A Honeybee Radiance Modifier object to be used for this
            aperture in direct solar simulations and in isolation studies (assessing
            the contribution of individual Apertures). If None, this will be
            a completely black material.

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
        """Initialize Aperture radiance properties."""
        _GeometryRadianceProperties.__init__(self, host, modifier, modifier_blk)

    @property
    def modifier(self):
        """Get or set the Aperture modifier.

        If the modifier is not set on the aperture-level, then it will be assigned
        based on the ModifierSet assigned to the parent Room.  If there is no
        parent Room or the parent Room's ModifierSet has no modifier for
        the Aperture type and boundary_condition, it will be assigned using the
        honeybee default generic ModifierSet.
        """
        if self._modifier:  # set by user
            return self._modifier
        elif self._host.has_parent and self._host.parent.has_parent:  # set by room
            constr_set = self._host.parent.parent.properties.radiance.modifier_set
            return constr_set.get_aperture_modifier(
                self._host.boundary_condition.name, self._host.is_operable,
                self._host.parent.type.name)
        elif self._host.has_parent:  # generic but influenced by parent aperture
            return generic_modifier_set_visible.get_aperture_modifier(
                self._host.boundary_condition.name, self._host.is_operable,
                self._host.parent.type.name)
        else:
            return generic_modifier_set_visible.get_aperture_modifier(
                self._host.boundary_condition.name, self._host.is_operable, 'Wall')

    @modifier.setter
    def modifier(self, value):
        if value is not None:
            assert isinstance(value, Modifier), \
                'Expected Radiance Modifier for aperture. Got {}'.format(type(value))
            value.lock()  # lock editing in case modifier has multiple references
        self._modifier = value

    @property
    def modifier_blk(self):
        """Get or set a modifier to be used in direct solar and in isolation studies.

        If None, this will be a completely black material if the Aperture's modifier
        is opaque and will be equal to the modifier if the Aperture's modifier is non-opaque.
        """
        if self._modifier_blk:  # set by user
            return self._modifier_blk
        return black

    @modifier_blk.setter
    def modifier_blk(self, value):
        if value is not None:
            assert isinstance(value, Modifier), \
                'Expected Radiance Modifier for aperture. Got {}'.format(type(value))
            value.lock()  # lock editing in case modifier has multiple references
        self._modifier_blk = value

    @classmethod
    def from_dict(cls, data, host):
        """Create ApertureRadianceProperties from a dictionary.

        Note that the dictionary must be a non-abridged version for this
        classmethod to work.

        Args:
            data: A dictionary representation of ApertureRadianceProperties with the
                format below.
            host: A Aperture object that hosts these properties.

        .. code-block:: python

            {
            'type': 'ApertureRadianceProperties',
            'modifier': {},  # A Honeybee Radiance Modifier dictionary
            'modifier_blk': {}  # A Honeybee Radiance Modifier dictionary
            }
        """
        assert data['type'] == 'ApertureRadianceProperties', \
            'Expected ApertureRadianceProperties. Got {}.'.format(data['type'])
        new_prop = cls(host)
        return cls._restore_modifiers_from_dict(new_prop, data)

    def apply_properties_from_dict(self, abridged_data, modifiers):
        """Apply properties from a ApertureRadiancePropertiesAbridged dictionary.

        Args:
            abridged_data: A ApertureRadiancePropertiesAbridged dictionary (typically
                coming from a Model) with the format below.
            modifiers: A dictionary of modifiers with modifier identifiers as keys,
                which will be used to re-assign modifiers.

        .. code-block:: python

            {
            'type': 'ApertureRadiancePropertiesAbridged',
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
        base['radiance']['type'] = 'ApertureRadianceProperties' if not \
            abridged else 'ApertureRadiancePropertiesAbridged'
        return self._add_modifiers_to_dict(base, abridged)

    def __repr__(self):
        return 'Aperture Radiance Properties:\n host: {}'.format(self.host.identifier)
