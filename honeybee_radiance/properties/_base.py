# coding=utf-8
"""Base class of Radiance Properties for all planar geometry objects."""
from ..modifier import Modifier
from ..mutil import dict_to_modifier  # imports all modifiers classes
from ..lib.modifiers import black
from ..lib.modifiersets import generic_modifier_set_visible


class _GeometryRadianceProperties(object):
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
        if mod.is_opaque:
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
        return self.modifier.is_opaque

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

        new_host: A new Shade object that hosts these properties.
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
            base['radiance']['modifier_blk'] =  self._modifier_blk.identifier if \
                abridged else self._modifier_blk.to_dict()
        return base

    @staticmethod
    def _restore_modifiers_from_dict(new_prop, data):
        """Restor modifiers from a data dictionary to a new properties object."""
        if 'modifier' in data and data['modifier'] is not None:
            new_prop.modifier = dict_to_modifier(data['modifier'])
        if 'modifier_blk' in data and data['modifier_blk'] is not None:
            new_prop.modifier_blk = dict_to_modifier(data['modifier_blk'])
        return new_prop

    def ToString(self):
        return self.__repr__()

    def __repr__(self):
        return 'Base Radiance Properties:\n host: {}'.format(self.host.identifier)
