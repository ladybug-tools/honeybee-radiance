"""Radiance modifier set."""
from __future__ import division

from honeybee_radiance.modifier import Modifier
from honeybee_radiance.mutil import dict_to_modifier  # imports all modifiers classes
from honeybee_radiance.lib.modifiers import generic_floor, generic_wall, \
    generic_ceiling, generic_door, generic_exterior_window, generic_interior_window, \
    generic_exterior_shade, generic_interior_shade, air_boundary

from honeybee._lockable import lockable
from honeybee.typing import valid_rad_string


_default_modifiers = {
    '_BaseSet': {'exterior': None, 'interior': None},
    'WallModifierSet': {
        'exterior': generic_wall,
        'interior': generic_wall
    },
    'FloorModifierSet': {
        'exterior': generic_floor,
        'interior': generic_floor
    },
    'RoofCeilingModifierSet': {
        'exterior': generic_ceiling,
        'interior': generic_ceiling
    },
    'ApertureModifierSet': {
        'exterior': generic_exterior_window,
        'interior': generic_interior_window,
        'operable': generic_exterior_window,
        'skylight': generic_exterior_window
    },
    'DoorModifierSet': {
        'exterior': generic_door,
        'interior': generic_door,
        'exterior_glass': generic_exterior_window,
        'interior_glass': generic_interior_window,
        'overhead': generic_door
    },
    'ShadeModifierSet': {
        'exterior': generic_exterior_shade,
        'interior': generic_interior_shade
    }
}


@lockable
class ModifierSet(object):
    """Set containting all radiance modifiers needed to create a radiance model.

    ModifierSets can be used to establish templates that are applied broadly
    across a Model, like a color scheme used consistently throughout a building.

    Args:
        identifier: Text string for a unique ModifierSet ID. Must not contain
            spaces or special characters. This will be used to identify the
            object across a model and in the exported Radiance files.
        wall_set: An optional WallModifierSet object for this ModifierSet.
            If None, it will be the honeybee generic default WallModifierSet.
        floor_set: An optional FloorModifierSet object for this ModifierSet.
            If None, it will be the honeybee generic default FloorModifierSet.
        roof_ceiling_set: An optional RoofCeilingModifierSet object for this ModifierSet.
            If None, it will be the honeybee generic default RoofCeilingModifierSet.
        aperture_set: An optional ApertureModifierSet object for this ModifierSet.
            If None, it will be the honeybee generic default ApertureModifierSet.
        door_set: An optional DoorModifierSet object for this ModifierSet.
            If None, it will be the honeybee generic default DoorModifierSet.
        shade_set: An optional ShadeModifierSet object for this ModifierSet.
            If None, it will be the honeybee generic default ShadeModifierSet.
        air_boundary_modifier: An optional Modifier to be used for all Faces with
            an AirBoundary face type. If None, it will be the honeybee generic
            air wall modifier.

    Properties:
        * identifier
        * display_name
        * wall_set
        * floor_set
        * roof_ceiling_set
        * aperture_set
        * door_set
        * shade_set
        * air_boundary_modifier
        * modifiers
        * modified_modifiers
        * modifiers_unique
        * modified_modifiers_unique
    """

    __slots__ = ('_identifier', '_display_name', '_wall_set', '_floor_set',
                 '_roof_ceiling_set', '_aperture_set', '_door_set', '_shade_set',
                 '_air_boundary_modifier', '_locked')

    def __init__(self, identifier, wall_set=None, floor_set=None, roof_ceiling_set=None,
                 aperture_set=None, door_set=None, shade_set=None,
                 air_boundary_modifier=None):
        """Initialize radiance modifier set."""
        self._locked = False  # unlocked by default
        self.identifier = identifier
        self._display_name = None
        self.wall_set = wall_set
        self.floor_set = floor_set
        self.roof_ceiling_set = roof_ceiling_set
        self.aperture_set = aperture_set
        self.door_set = door_set
        self.shade_set = shade_set
        self.air_boundary_modifier = air_boundary_modifier

    @property
    def identifier(self):
        """Get or set a text string for the unique modifier set identifier."""
        return self._identifier

    @identifier.setter
    def identifier(self, identifier):
        self._identifier = valid_rad_string(identifier, 'ModifierSet identifier')

    @property
    def display_name(self):
        """Get or set a string for the object name without any character restrictions.

        If not set, this will be equal to the identifier.
        """
        if self._display_name is None:
            return self._identifier
        return self._display_name

    @display_name.setter
    def display_name(self, value):
        try:
            self._display_name = str(value)
        except UnicodeEncodeError:  # Python 2 machine lacking the character set
            self._display_name = value  # keep it as unicode

    @property
    def wall_set(self):
        """Get or set the WallModifierSet assigned to this ModifierSet."""
        return self._wall_set

    @wall_set.setter
    def wall_set(self, value):
        if value is not None:
            assert isinstance(value, WallModifierSet), \
                'Expected WallModifierSet. Got {}'.format(type(value))
            self._wall_set = value
        else:
            self._wall_set = WallModifierSet()

    @property
    def floor_set(self):
        """Get or set the FloorModifierSet assigned to this ModifierSet."""
        return self._floor_set

    @floor_set.setter
    def floor_set(self, value):
        if value is not None:
            assert isinstance(value, FloorModifierSet), \
                'Expected FloorModifierSet. Got {}'.format(type(value))
            self._floor_set = value
        else:
            self._floor_set = FloorModifierSet()

    @property
    def roof_ceiling_set(self):
        """Get or set the RoofCeilingModifierSet assigned to this ModifierSet."""
        return self._roof_ceiling_set

    @roof_ceiling_set.setter
    def roof_ceiling_set(self, value):
        if value is not None:
            assert isinstance(value, RoofCeilingModifierSet), \
                'Expected RoofCeilingModifierSet. Got {}'.format(type(value))
            self._roof_ceiling_set = value
        else:
            self._roof_ceiling_set = RoofCeilingModifierSet()

    @property
    def aperture_set(self):
        """Get or set the ApertureModifierSet assigned to this ModifierSet."""
        return self._aperture_set

    @aperture_set.setter
    def aperture_set(self, value):
        if value is not None:
            assert isinstance(value, ApertureModifierSet), \
                'Expected ApertureModifierSet. Got {}'.format(type(value))
            self._aperture_set = value
        else:
            self._aperture_set = ApertureModifierSet()

    @property
    def door_set(self):
        """Get or set the DoorModifierSet assigned to this ModifierSet."""
        return self._door_set

    @door_set.setter
    def door_set(self, value):
        if value is not None:
            assert isinstance(value, DoorModifierSet), \
                'Expected DoorModifierSet. Got {}'.format(type(value))
            self._door_set = value
        else:
            self._door_set = DoorModifierSet()

    @property
    def shade_set(self):
        """Get or set the ShadeModifierSet assigned to this ModifierSet."""
        return self._shade_set

    @shade_set.setter
    def shade_set(self, value):
        if value is not None:
            assert isinstance(value, ShadeModifierSet), \
                'Expected ShadeModifierSet. Got {}'.format(type(value))
            self._shade_set = value
        else:
            self._shade_set = ShadeModifierSet()

    @property
    def air_boundary_modifier(self):
        """Get or set a Modifier to be used for all Faces with an AirBoundary face type.
        """
        if self._air_boundary_modifier is None:
            return air_boundary
        return self._air_boundary_modifier

    @air_boundary_modifier.setter
    def air_boundary_modifier(self, value):
        if value is not None:
            assert isinstance(value, Modifier), \
                'Expected Modifier. Got {}'.format(type(value))
            value.lock()   # lock editing in case modifier has multiple references
        self._air_boundary_modifier = value

    @property
    def modifiers(self):
        """List of all modifiers contained within the set."""
        return self.wall_set.modifiers + \
            self.floor_set.modifiers + \
            self.roof_ceiling_set.modifiers + \
            self.aperture_set.modifiers + \
            self.door_set.modifiers + \
            self.shade_set.modifiers + \
            [self.air_boundary_modifier]

    @property
    def modified_modifiers(self):
        """List of all modifiers that are not defaulted within the set."""
        modified_modifiers = self.wall_set.modified_modifiers + \
            self.floor_set.modified_modifiers + \
            self.roof_ceiling_set.modified_modifiers + \
            self.aperture_set.modified_modifiers + \
            self.door_set.modified_modifiers + \
            self.shade_set.modified_modifiers
        if self._air_boundary_modifier is not None:
            modified_modifiers.append(self._air_boundary_modifier)
        return modified_modifiers

    @property
    def modifiers_unique(self):
        """List of all unique modifiers contained within the set."""
        return list(set(self.modifiers))

    @property
    def modified_modifiers_unique(self):
        """List of all unique modifiers that are not defaulted within the set."""
        return list(set(self.modified_modifiers))

    def get_face_modifier(self, face_type, boundary_condition):
        """Get a modifier object that will be assigned to a given type of face.

        Args:
            face_type: Text string for the type of face (eg. 'Wall', 'Floor',
                'Roof', 'AirBoundary').
            boundary_condition: Text string for the boundary condition
                (eg. 'Outdoors', 'Surface', 'Ground')
        """
        if face_type == 'Wall':
            return self._get_modifier_from_set(self.wall_set, boundary_condition)
        elif face_type == 'Floor':
            return self._get_modifier_from_set(self.floor_set, boundary_condition)
        elif face_type == 'RoofCeiling':
            return self._get_modifier_from_set(self.roof_ceiling_set, boundary_condition)
        elif face_type == 'AirBoundary':
            return self.air_boundary_modifier
        else:
            raise NotImplementedError(
                'Face type {} is not recognized for ModifierSet'.format(face_type))

    def get_aperture_modifier(self, boundary_condition, is_operable, parent_face_type):
        """Get a modifier object that will be assigned to a given type of aperture.

        Args:
            boundary_condition: Text string for the boundary condition
                (eg. 'Outdoors', 'Surface')
            is_operable: Boolean to note whether the aperture is operable.
            parent_face_type: Text string for the type of face to which the aperture
                is a child (eg. 'Wall', 'Floor', 'Roof').
        """
        if boundary_condition == 'Outdoors':
            if not is_operable:
                if parent_face_type == 'Wall':
                    return self.aperture_set.window_modifier
                else:
                    return self.aperture_set.skylight_modifier
            else:
                return self.aperture_set.operable_modifier
        elif boundary_condition == 'Surface':
            return self.aperture_set.interior_modifier
        else:
            raise NotImplementedError(
                'Boundary condition {} is not recognized for apertures in '
                'ModifierSet'.format(boundary_condition))

    def get_door_modifier(self, boundary_condition, is_glass, parent_face_type):
        """Get a modifier object that will be assigned to a given type of door.

        Args:
            boundary_condition: Text string for the boundary condition
                (eg. 'Outdoors', 'Surface').
            is_glass: Boolean to note whether the door is glass (instead of opaque).
            parent_face_type: Text string for the type of face to which the door
                is a child (eg. 'Wall', 'Floor', 'Roof').
        """
        if boundary_condition == 'Outdoors':
            if not is_glass:
                if parent_face_type == 'Wall':
                    return self.door_set.exterior_modifier
                else:
                    return self.door_set.overhead_modifier
            else:
                return self.door_set.exterior_glass_modifier
        elif boundary_condition == 'Surface':
            if not is_glass:
                return self.door_set.interior_modifier
            else:
                return self.door_set.interior_glass_modifier
        else:
            raise NotImplementedError(
                'Boundary condition {} is not recognized for doors in '
                'ModifierSet'.format(boundary_condition)
                )

    def get_shade_modifier(self, is_indoor=False):
        """Get a modifier object that will be assigned to a shade.

        Args:
            is_indoor: A boolean to indicate if the shade is on the indoors or
                the outdoors of its parent. Default: False.
        """
        if is_indoor:
            return self.shade_set.interior_modifier
        else:
            return self.shade_set.exterior_modifier

    @classmethod
    def from_dict(cls, data):
        """Create a ModifierSet from a dictionary.

        Note that the dictionary must be a non-abridged version for this
        classmethod to work.

        Args:
            data: Dictionary describing the ModifierSet in the following format.

        .. code-block:: python

            {
            'type': 'ModifierSet',
            'identifier': str,  # ModifierSet identifier
            "display_name": str,  # ModifierSet display name
            'wall_set': {},  # WallModifierSet dictionary
            'floor_set': {},  # FloorSet dictionary
            'roof_ceiling_set': {},  # RoofCeilingModifierSet dictionary
            'aperture_set': {},  # ApertureModifierSet dictionary
            'door_set': {},  # DoorModifierSet dictionary
            'shade_set': {},  # ShadeModifierSet dictionary
            'air_boundary_modifier': {},  # AirBoundary dictionary
            }
        """
        assert data['type'] == 'ModifierSet', \
            'Expected ModifierSet. Got {}.'.format(data['type'])

        # build each of the sub-construction sets
        wall_set = WallModifierSet.from_dict(data['wall_set']) if 'wall_set' \
            in data and data['wall_set'] is not None else None
        floor_set = FloorModifierSet.from_dict(data['floor_set']) if 'floor_set' \
            in data and data['floor_set'] is not None else None
        roof_ceiling_set = RoofCeilingModifierSet.from_dict(data['roof_ceiling_set']) \
            if 'roof_ceiling_set' in data and \
            data['roof_ceiling_set'] is not None else None
        aperture_set = ApertureModifierSet.from_dict(data['aperture_set']) if \
            'aperture_set' in data and data['aperture_set'] is not None else None
        door_set = DoorModifierSet.from_dict(data['door_set']) if \
            'door_set' in data and data['door_set'] is not None else None
        shade_set = ShadeModifierSet.from_dict(data['shade_set']) if \
            'shade_set' in data and data['shade_set'] is not None else None
        air_mod = dict_to_modifier(data['air_boundary_modifier']) \
            if 'air_boundary_modifier' in data and \
            data['air_boundary_modifier'] is not None else None

        new_obj = cls(data['identifier'], wall_set, floor_set, roof_ceiling_set,
                      aperture_set, door_set, shade_set, air_mod)
        if 'display_name' in data and data['display_name'] is not None:
            new_obj.display_name = data['display_name']
        return new_obj

    @classmethod
    def from_dict_abridged(cls, data, modifier_dict):
        """Create a ModifierSet from an abridged dictionary.

        Args:
            data: A ModifierSetAbridged dictionary with the format below.
            modifier_dict: A dictionary with modifier identifiers as keys and
                honeybee modifier objects as values. These will be used to
                assign the 4 to the ModifierSet object.

        .. code-block:: python

            {
            'type': 'ModifierSetAbridged',
            'identifier': str,  # ModifierSet identifier
            "display_name": str,  # ModifierSet display name
            'wall_set': {},  # WallModifierSetAbridged dictionary
            'floor_set': {},  # FloorSetAbridged dictionary
            'roof_ceiling_set': {},  # RoofCeilingModifierSetAbridged dictionary
            'aperture_set': {},  # ApertureModifierSetAbridged dictionary
            'door_set': {},  # DoorModifierSetAbridged dictionary
            'shade_set': {},  # ShadeModifierSetAbridged dictionary
            'air_boundary_modifier': {},  # AirBoundary dictionary
            }
        """
        assert data['type'] == 'ModifierSetAbridged', \
            'Expected ModifierSetAbridged. Got {}.'.format(data['type'])
        wall_set, floor_set, roof_ceiling_set, aperture_set, door_set, shade_set, \
            air_boundary_mod = cls._get_subsets_from_abridged(data, modifier_dict)
        new_obj = cls(data['identifier'], wall_set, floor_set, roof_ceiling_set,
                      aperture_set, door_set, shade_set, air_boundary_mod)
        if 'display_name' in data and data['display_name'] is not None:
            new_obj.display_name = data['display_name']
        return new_obj

    def to_dict(self, abridged=False, none_for_defaults=True):
        """Get ModifierSet as a dictionary.

        Args:
            abridged: Boolean noting whether detailed modifier objects should be
                written into the ModifierSet (False) or just an abridged
                version (True). Default: False.
            none_for_defaults: Boolean to note whether default modifiers in the
                set should be included in detail (False) or should be None (True).
                Default: True.
        """
        base = {'type': 'ModifierSet'} if not abridged \
            else {'type': 'ModifierSetAbridged'}

        base['identifier'] = self.identifier
        base['wall_set'] = self.wall_set.to_dict(abridged, none_for_defaults)
        base['floor_set'] = self.floor_set.to_dict(abridged, none_for_defaults)
        base['roof_ceiling_set'] = \
            self.roof_ceiling_set.to_dict(abridged, none_for_defaults)
        base['aperture_set'] = self.aperture_set.to_dict(abridged, none_for_defaults)
        base['door_set'] = self.door_set.to_dict(abridged, none_for_defaults)
        base['shade_set'] = self.shade_set.to_dict(abridged, none_for_defaults)
        if none_for_defaults:
            if abridged:
                base['air_boundary_modifier'] = self._air_boundary_modifier.identifier \
                    if self._air_boundary_modifier is not None else None
            else:
                base['air_boundary_modifier'] = self._air_boundary_modifier.to_dict() \
                    if self._air_boundary_modifier is not None else None
        else:
            base['air_boundary_modifier'] = self.air_boundary_modifier.identifier \
                if abridged else self.air_boundary_modifier.to_dict()

        if self._display_name is not None:
            base['display_name'] = self.display_name
        return base

    def duplicate(self):
        """Get a copy of this ModifierSet."""
        return self.__copy__()

    def lock(self):
        """The lock() method to will also lock the WallModifierSet, etc."""
        self._locked = True
        self._wall_set.lock()
        self._floor_set.lock()
        self._roof_ceiling_set.lock()
        self._aperture_set.lock()
        self._door_set.lock()
        self._shade_set.lock()

    def unlock(self):
        """The unlock() method will also unlock the WallModifierSet, etc."""
        self._locked = False
        self._wall_set.unlock()
        self._floor_set.unlock()
        self._roof_ceiling_set.unlock()
        self._aperture_set.unlock()
        self._door_set.unlock()
        self._shade_set.unlock()

    def _get_modifier_from_set(self, face_type_set, boundary_condition):
        """Get a specific modifier from a face_type_set."""
        if boundary_condition == 'Outdoors':
            return face_type_set.exterior_modifier
        else:
            return face_type_set.interior_modifier

    @staticmethod
    def _get_subsets_from_abridged(data, modifiers):
        """Get subset objects from and abridged dictionary."""
        wall_set = ModifierSet._make_modifier_subset(
            data, WallModifierSet(), 'wall_set', modifiers)
        floor_set = ModifierSet._make_modifier_subset(
            data, FloorModifierSet(), 'floor_set', modifiers)
        roof_ceiling_set = ModifierSet._make_modifier_subset(
            data, RoofCeilingModifierSet(), 'roof_ceiling_set', modifiers)
        shade_set = ModifierSet._make_modifier_subset(
            data, ShadeModifierSet(), 'shade_set', modifiers)
        aperture_set = ModifierSet._make_aperture_subset(
            data, ApertureModifierSet(), modifiers)
        door_set = ModifierSet._make_door_subset(data, DoorModifierSet(), modifiers)
        if 'air_boundary_modifier' in data and data['air_boundary_modifier'] is not None:
            air_boundary_mod = modifiers[data['air_boundary_modifier']]
        else:
            air_boundary_mod = None

        return wall_set, floor_set, roof_ceiling_set, aperture_set, door_set, \
            shade_set, air_boundary_mod

    @staticmethod
    def _make_modifier_subset(data, sub_set, sub_set_name, modifiers):
        """Make a wall set, floor set, roof ceiling set, or shade set from dictionary."""
        if sub_set_name in data:
            if 'exterior_modifier' in data[sub_set_name] and \
                    data[sub_set_name]['exterior_modifier'] is not None:
                sub_set.exterior_modifier = \
                    modifiers[data[sub_set_name]['exterior_modifier']]
            if 'interior_modifier' in data[sub_set_name] and \
                    data[sub_set_name]['interior_modifier'] is not None:
                sub_set.interior_modifier = \
                    modifiers[data[sub_set_name]['interior_modifier']]
        return sub_set

    @staticmethod
    def _make_aperture_subset(data, sub_set, modifiers):
        """Make an ApertureModifierSet from a dictionary."""
        if 'aperture_set' in data:
            if 'window_modifier' in data['aperture_set'] and \
                    data['aperture_set']['window_modifier'] is not None:
                sub_set.window_modifier = \
                    modifiers[data['aperture_set']['window_modifier']]
            if 'interior_modifier' in data['aperture_set'] and \
                    data['aperture_set']['interior_modifier'] is not None:
                sub_set.interior_modifier = \
                    modifiers[data['aperture_set']['interior_modifier']]
            if 'skylight_modifier' in data['aperture_set'] and \
                    data['aperture_set']['skylight_modifier'] is not None:
                sub_set.skylight_modifier = \
                    modifiers[data['aperture_set']['skylight_modifier']]
            if 'operable_modifier' in data['aperture_set'] and \
                    data['aperture_set']['operable_modifier'] is not None:
                sub_set.operable_modifier = \
                    modifiers[data['aperture_set']['operable_modifier']]
        return sub_set

    @staticmethod
    def _make_door_subset(data, sub_set, modifiers):
        """Make a DoorModifierSet from dictionary."""
        if 'door_set' in data:
            if 'exterior_modifier' in data['door_set'] and \
                    data['door_set']['exterior_modifier'] is not None:
                sub_set.exterior_modifier = \
                    modifiers[data['door_set']['exterior_modifier']]
            if 'interior_modifier' in data['door_set'] and \
                    data['door_set']['interior_modifier'] is not None:
                sub_set.interior_modifier = \
                    modifiers[data['door_set']['interior_modifier']]
            if 'exterior_glass_modifier' in data['door_set'] and \
                    data['door_set']['exterior_glass_modifier'] is not None:
                sub_set.exterior_glass_modifier = \
                    modifiers[data['door_set']['exterior_glass_modifier']]
            if 'interior_glass_modifier' in data['door_set'] and \
                    data['door_set']['interior_glass_modifier'] is not None:
                sub_set.interior_glass_modifier = \
                    modifiers[data['door_set']['interior_glass_modifier']]
            if 'overhead_modifier' in data['door_set'] and \
                    data['door_set']['overhead_modifier'] is not None:
                sub_set.overhead_modifier = \
                    modifiers[data['door_set']['overhead_modifier']]
        return sub_set

    def ToString(self):
        """Overwrite .NET ToString."""
        return self.__repr__()

    def __copy__(self):
        new_obj = ModifierSet(
            self.identifier,
            self.wall_set.duplicate(),
            self.floor_set.duplicate(),
            self.roof_ceiling_set.duplicate(),
            self.aperture_set.duplicate(),
            self.door_set.duplicate(),
            self.shade_set.duplicate(),
            self._air_boundary_modifier
        )
        new_obj._display_name = self._display_name
        return new_obj

    def __key(self):
        """A tuple based on the object properties, useful for hashing."""
        return (self.identifier,) + tuple(hash(mod) for mod in self.modifiers)

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        return isinstance(other, ModifierSet) and self.__key() == other.__key()

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return 'Radiance Modifier Set: {}'.format(self.display_name)


@lockable
class _BaseSet(object):
    """Base class for the sets assigned to Faces.

    This includes WallModifierSet, FloorModifierSet, RoofCeilingModifierSet and
    ShadeModifierSet.

    Args:
        exterior_modifier: A radiance modifier object for faces with an
            Outdoors boundary condition.
        interior_modifier: A radiance modifier object for faces with a boundary
            condition other than Outdoors.
    """

    __slots__ = ('_exterior_modifier', '_interior_modifier', '_locked')

    def __init__(self, exterior_modifier=None, interior_modifier=None):
        """Initialize set."""
        self._locked = False  # unlocked by default
        self.exterior_modifier = exterior_modifier
        self.interior_modifier = interior_modifier

    @property
    def exterior_modifier(self):
        """Get or set the modifier for exterior objects."""
        if self._exterior_modifier is None:
            return _default_modifiers[self.__class__.__name__]['exterior']
        return self._exterior_modifier

    @exterior_modifier.setter
    def exterior_modifier(self, value):
        self._exterior_modifier = self._validate_modifier(value)

    @property
    def interior_modifier(self):
        """Get or set the modifier for interior objects."""
        if self._interior_modifier is None:
            return _default_modifiers[self.__class__.__name__]['interior']
        return self._interior_modifier

    @interior_modifier.setter
    def interior_modifier(self, value):
        self._interior_modifier = self._validate_modifier(value)

    @property
    def modifiers(self):
        """List of all modifiers contained within the set."""
        return [getattr(self, attr[1:]) for attr in self._slots]

    @property
    def modified_modifiers(self):
        """List of all modifiers that are not defaulted within the set."""
        _modifiers = [getattr(self, attr) for attr in self._slots]
        modifiers = [
            modifier for modifier in _modifiers
            if modifier is not None
        ]
        return modifiers

    @property
    def is_modified(self):
        """Boolean noting whether any modifiers are modified from the default."""
        return len(self.modified_modifiers) != 0

    @classmethod
    def from_dict(cls, data):
        """Create a SubSet from a dictionary.

        Note that the dictionary must be a non-abridged version for this
        classmethod to work.

        Args:
            data: Dictionary describing the Set of the object.
        """
        assert data['type'] == cls.__name__, \
            'Expected {}. Got {}.'.format(cls.__name__, data['type'])
        extc = dict_to_modifier(data['exterior_modifier']) \
            if 'exterior_modifier' in data and data['exterior_modifier'] \
            is not None else None
        intc = dict_to_modifier(data['interior_modifier']) \
            if 'interior_modifier' in data and data['interior_modifier'] \
            is not None else None
        return cls(extc, intc)

    def to_dict(self, abridged=False, none_for_defaults=True):
        """Get the ModifierSet as a dictionary.

        Args:
            abridged: Boolean noting whether detailed modifiers objects should
                be written into the ModifierSet (False) or just an abridged
                version (True). Default: False.
            none_for_defaults: Boolean to note whether default modifiers in the
                set should be included in detail (False) or should be None (True).
                Default: True.
        """
        attributes = self._slots
        if none_for_defaults:
            if abridged:
                base = {attr[1:]: getattr(self, attr[1:]).identifier
                        if getattr(self, attr) is not None else None
                        for attr in attributes}
            else:
                base = {attr[1:]: getattr(self, attr[1:]).to_dict()
                        if getattr(self, attr) is not None else None
                        for attr in attributes}
        else:
            if abridged:
                base = {attr[1:]: getattr(self, attr[1:]).identifier
                        for attr in attributes}
            else:
                base = {attr[1:]: getattr(self, attr[1:]).to_dict()
                        for attr in attributes}

        base['type'] = self.__class__.__name__ + 'Abridged' if abridged else \
            self.__class__.__name__
        return base

    def duplicate(self):
        """Get a copy of this set."""
        return self.__copy__()

    def _validate_modifier(self, value):
        """Check a modifier before assigning it."""
        if value is not None:
            assert isinstance(value, Modifier), \
                'Expected modifier. Got {}'.format(type(value))
            value.lock()   # lock editing in case modifier has multiple references
        return value

    @property
    def _slots(self):
        """Return slots including the ones from the baseclass if any."""
        slots = set(self.__slots__)
        for cls in self.__class__.__mro__[:-1]:
            for s in getattr(cls, '__slots__', tuple()):
                if s in slots:
                    continue
                slots.add(s)
        slots.remove('_locked')
        return slots

    def ToString(self):
        """Overwrite .NET ToString."""
        return self.__repr__()

    def __len__(self):
        return 2

    def __iter__(self):
        return iter(self.modifiers)

    def __copy__(self):
        return self.__class__(self._exterior_modifier, self._interior_modifier)

    def __repr__(self):
        name = self.__class__.__name__.split('Set')[0]
        return '{} Modifier Set: [Exterior: {}] [Interior: {}]'.format(
            name, self.exterior_modifier.display_name,
            self.interior_modifier.display_name)


@lockable
class WallModifierSet(_BaseSet):
    """Set containing all radiance modifiers needed to for an radiance model's Walls.

    Properties:
        * exterior_modifier
        * interior_modifier
        * modifiers
        * modified_modifiers
        * is_modified
    """
    __slots__ = ()


@lockable
class FloorModifierSet(_BaseSet):
    """Set containing all radiance modifiers needed to for an radiance model's floors.

    Properties:
        * exterior_modifier
        * interior_modifier
        * modifiers
        * modified_modifiers
        * is_modified
    """
    __slots__ = ()


@lockable
class RoofCeilingModifierSet(_BaseSet):
    """Set containing all radiance modifiers needed to for an radiance model's roofs.

    Properties:
        * exterior_modifier
        * interior_modifier
        * modifiers
        * modified_modifiers
        * is_modified
    """
    __slots__ = ()


@lockable
class ShadeModifierSet(_BaseSet):
    """Set containing all radiance modifiers needed to for an radiance model's Shade.

    Properties:
        * exterior_modifier
        * interior_modifier
        * modifiers
        * modified_modifiers
        * is_modified
    """
    __slots__ = ()


@lockable
class ApertureModifierSet(_BaseSet):
    """Set containing all radiance modifiers needed to for a radiance model's Apertures.

    Args:
        window_modifier: A modifier object for apertures with an Outdoors
            boundary condition, False is_operable property, and Wall parent Face.
        interior_modifier: A modifier object for apertures with a Surface
            boundary condition.
        skylight_modifier: : A modifier object for apertures with an Outdoors
            boundary condition, False is_operable property, and a RoofCeiling
            or Floor face type for their parent face.
        operable_modifier: A modifier object for apertures with an Outdoors
            boundary condition and a True is_operable property.

    Properties:
        * window_modifier
        * interior_modifier
        * skylight_modifier
        * operable_modifier
        * modifiers
        * modified_modifiers
        * is_modified
    """
    __slots__ = ('_skylight_modifier', '_operable_modifier')

    def __init__(self, window_modifier=None, interior_modifier=None,
                 skylight_modifier=None, operable_modifier=None):
        """Initialize aperture set."""
        _BaseSet.__init__(self, window_modifier, interior_modifier)
        self.skylight_modifier = skylight_modifier
        self.operable_modifier = operable_modifier

    @property
    def window_modifier(self):
        """Get or set the modifier for exterior fixed apertures in walls."""
        if self._exterior_modifier is None:
            return _default_modifiers[self.__class__.__name__]['exterior']
        return self._exterior_modifier

    @window_modifier.setter
    def window_modifier(self, value):
        self._exterior_modifier = self._validate_modifier(value)

    @property
    def skylight_modifier(self):
        """Get or set the modifier for apertures in roofs."""
        if self._skylight_modifier is None:
            return _default_modifiers[self.__class__.__name__]['skylight']
        return self._skylight_modifier

    @skylight_modifier.setter
    def skylight_modifier(self, value):
        self._skylight_modifier = self._validate_modifier(value)

    @property
    def operable_modifier(self):
        """Get or set the modifier for operable apertures."""
        if self._operable_modifier is None:
            return _default_modifiers[self.__class__.__name__]['operable']
        return self._operable_modifier

    @operable_modifier.setter
    def operable_modifier(self, value):
        self._operable_modifier = self._validate_modifier(value)

    @classmethod
    def from_dict(cls, data):
        """Create a ApertureModifierSet from a dictionary.

        Note that the dictionary must be a non-abridged version for this
        classmethod to work.

        Args:
            data: Dictionary describing the ApertureModifierSet.
        """
        assert data['type'] == cls.__name__, \
            'Expected {}. Got {}.'.format(cls.__name__, data['type'])
        extc = dict_to_modifier(data['window_modifier']) \
            if 'window_modifier' in data and data['window_modifier'] \
            is not None else None
        intc = dict_to_modifier(data['interior_modifier']) \
            if 'interior_modifier' in data and data['interior_modifier'] \
            is not None else None
        skyc = dict_to_modifier(data['skylight_modifier']) \
            if 'skylight_modifier' in data and data['skylight_modifier'] \
            is not None else None
        opc = dict_to_modifier(data['operable_modifier']) \
            if 'operable_modifier' in data and data['operable_modifier'] \
            is not None else None
        return cls(extc, intc, skyc, opc)

    def to_dict(self, abridged=False, none_for_defaults=True):
        """Get the ModifierSet as a dictionary.

        Args:
            abridged: Boolean noting whether detailed modifier objects should
                be written into the ModifierSet (False) or just an abridged
                version (True). Default: False.
            none_for_defaults: Boolean to note whether default modifiers in the
                set should be included in detail (False) or should be None (True).
                Default: True.
        """
        base = _BaseSet.to_dict(self, abridged, none_for_defaults)
        if 'exterior_modifier' in base:
            base['window_modifier'] = base['exterior_modifier']
            del base['exterior_modifier']
        return base

    def __len__(self):
        return 4

    def __copy__(self):
        return self.__class__(
            self._exterior_modifier,
            self._interior_modifier,
            self._skylight_modifier,
            self._operable_modifier
        )

    def __repr__(self):
        return 'Aperture Modifier Set: [Exterior: {}] [Interior: {}]' \
            ' [Skylight: {}] [Operable: {}]'.format(
                self.window_modifier.display_name,
                self.interior_modifier.display_name,
                self.skylight_modifier.display_name,
                self.operable_modifier.display_name)


@lockable
class DoorModifierSet(_BaseSet):
    """Set containing all radiance modifiers needed to for an radiance model's Doors.

    Args:
        exterior_modifier: A modifier object for doors in walls with an Outdoors
            boundary condition.
        interior_modifier: A modifier object for doors with a Surface (or other)
            boundary condition.
        exterior_glass_modifier: A modifier object for all glass doors with an
            Outdoors boundary condition.
        interior_glass_modifier: A modifier object for all glass doors with a
            Surface boundary condition.
        overhead_modifier: : A modifier object for doors with an Outdoors boundary
            condition and a RoofCeiling or Floor face type for their parent face.

    Properties:
        * exterior_modifier
        * interior_modifier
        * exterior_glass_modifier
        * interior_glass_modifier
        * overhead_modifier
        * modifiers
        * modified_modifiers
        * is_modified
    """
    __slots__ = ('_overhead_modifier', '_exterior_glass_modifier',
                 '_interior_glass_modifier')

    def __init__(self, exterior_modifier=None, interior_modifier=None,
                 exterior_glass_modifier=None, interior_glass_modifier=None,
                 overhead_modifier=None):
        """Initialize door set."""
        _BaseSet.__init__(self, exterior_modifier, interior_modifier)
        self.exterior_glass_modifier = exterior_glass_modifier
        self.interior_glass_modifier = interior_glass_modifier
        self.overhead_modifier = overhead_modifier

    @property
    def exterior_glass_modifier(self):
        """Get or set the modifier for exterior glass doors."""
        if self._exterior_glass_modifier is None:
            return _default_modifiers[self.__class__.__name__]['exterior_glass']
        return self._exterior_glass_modifier

    @exterior_glass_modifier.setter
    def exterior_glass_modifier(self, value):
        self._exterior_glass_modifier = self._validate_modifier(value)

    @property
    def interior_glass_modifier(self):
        """Get or set the modifier for interior glass doors."""
        if self._interior_glass_modifier is None:
            return _default_modifiers[self.__class__.__name__]['interior_glass']
        return self._interior_glass_modifier

    @interior_glass_modifier.setter
    def interior_glass_modifier(self, value):
        self._interior_glass_modifier = self._validate_modifier(value)

    @property
    def overhead_modifier(self):
        """Get or set the modifier for skylights."""
        if self._overhead_modifier is None:
            return _default_modifiers[self.__class__.__name__]['overhead']
        return self._overhead_modifier

    @overhead_modifier.setter
    def overhead_modifier(self, value):
        self._overhead_modifier = self._validate_modifier(value)

    @classmethod
    def from_dict(cls, data):
        """Create a ApertureModifierSet from a dictionary.

        Note that the dictionary must be a non-abridged version for this
        classmethod to work.

        Args:
            data: Dictionary describing the ApertureModifierSet.
        """
        assert data['type'] == cls.__name__, \
            'Expected {}. Got {}.'.format(cls.__name__, data['type'])
        extc = dict_to_modifier(data['exterior_modifier']) \
            if 'exterior_modifier' in data and data['exterior_modifier'] \
            is not None else None
        intc = dict_to_modifier(data['interior_modifier']) \
            if 'interior_modifier' in data and data['interior_modifier'] \
            is not None else None
        egc = dict_to_modifier(data['exterior_glass_modifier']) \
            if 'exterior_glass_modifier' in data and data['exterior_glass_modifier'] \
            is not None else None
        igc = dict_to_modifier(data['interior_glass_modifier']) \
            if 'interior_glass_modifier' in data and data['interior_glass_modifier'] \
            is not None else None
        ohc = dict_to_modifier(data['overhead_modifier']) \
            if 'overhead_modifier' in data and data['overhead_modifier'] \
            is not None else None
        return cls(extc, intc, egc, igc, ohc)

    def __len__(self):
        return 3

    def __copy__(self):
        return self.__class__(
            self._exterior_modifier,
            self._interior_modifier,
            self._exterior_glass_modifier,
            self._interior_glass_modifier,
            self._overhead_modifier
        )

    def __repr__(self):
        return 'Door Modifier Set: [Exterior: {}] [Interior: {}]'.format(
                self.exterior_modifier.display_name,
                self.interior_modifier.display_name)
