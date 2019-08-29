"""Radiance modifier set."""
from __future__ import division

from honeybee_radiance.primitive import Primitive
from honeybee_radiance.lib.modifiers import (
    generic_exterior_wall, generic_interior_wall,
    generic_roof, generic_ceiling,
    generic_floor, air_wall,
    generic_exterior_glass, generic_interior_glass,
    generic_exterior_glass_door, generic_interior_glass_door, generic_opaque_door,
    generic_exterior_shade, generic_interior_shade
)
from honeybee._lockable import lockable
import honeybee.typing as typing


_default_modifiers = {
    '_BaseSet': {'exterior': None, 'interior': None},
    'WallSet': {
        'exterior': generic_exterior_wall,
        'interior': generic_interior_wall
    },
    'FloorSet': {
        'exterior': generic_floor,
        'interior': generic_floor
    },
    'RoofCeilingSet': {
        'exterior': generic_roof,
        'interior': generic_ceiling
    },
    'ApertureSet': {
        'exterior': generic_exterior_glass,
        'interior': generic_interior_glass,
        'operable': generic_interior_glass,
        'skylight': generic_exterior_glass
    },
    'DoorSet': {
        'exterior': generic_opaque_door,
        'interior': generic_opaque_door,
        'exterior_glass': generic_exterior_glass_door,
        'interior_glass': generic_interior_glass_door,
        'overhead': generic_opaque_door
    },
    'ShadeSet': {
        'exterior': generic_exterior_shade,
        'interior': generic_interior_shade
    }
}


@lockable
class _BaseSet(object):
    """Base class for the sets assigned to Faces (WallSet, FloorSet, RoofCeilingSet)."""

    __slots__ = ('_exterior_modifier', '_interior_modifier', '_locked')

    def __init__(self, exterior_modifier=None, interior_modifier=None):
        """Initialize set.

        Args:
            exterior_modifier: A radiance modifier object for faces with an
                Outdoors boundary condition.
            interior_modifier: A radiance modifier object for faces with a boundary
                condition other than Outdoors.
        """
        self._locked = False  # unlocked by default
        self.exterior_modifier = exterior_modifier
        self.interior_modifier = interior_modifier

    @property
    def exterior_modifier(self):
        """Get or set the modifier for exterior Faces."""
        if self._exterior_modifier is None:
            return _default_modifiers[self.__class__.__name__]['exterior']
        return self._exterior_modifier

    @exterior_modifier.setter
    def exterior_modifier(self, value):
        self._exterior_modifier = self._validate_modifier(value)

    @property
    def interior_modifier(self):
        """Get or set the modifier for interior Faces."""
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

    def _to_dict(self, none_for_defaults=True):
        """Get the ModifierSet as a dictionary.

        Args:
            none_for_defaults: Boolean to note whether default modifiers in the
                set should be included in detail (False) or should be None (True).
                Default: True.
        """
        attributes = self._slots
        if none_for_defaults:
            base = {
                attr[1:]:getattr(self, attr[1:]).name
                if getattr(self, attr) is not None else None
                for attr in attributes
                }
        else:
            base = {
                attr[1:]:getattr(self, attr[1:]).name
                for attr in attributes
            }
        
        base['type'] = self.__class__.__name__ + 'Abridged'
        return base

    def duplicate(self):
        """Get a copy of this set."""
        return self.__copy__()

    def _validate_modifier(self, value):
        """Check an modifier before assigning it."""
        if value is not None:
            assert isinstance(value, Primitive) and value.can_be_modifier , \
                'Expected modifier. Got {}'.format(type(value))
            # TODO: Remove the comment once lockable is implemented
            # value.lock()   # lock editing in case modifier has multiple references
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
        return '{} Modifier Set:\n Exterior: {}\n Interior: {}'.format(
            name, self.exterior_modifier.name, self.interior_modifier.name
        )


@lockable
class WallSet(_BaseSet):
    """Set containing all radiance modifiers needed to for an radiance model's Walls.

    Properties:
        exterior_modifier
        interior_modifier
        modifiers
        modified_modifiers
        is_modified
    """
    __slots__ = ()


@lockable
class FloorSet(_BaseSet):
    """Set containing all radiance modifiers needed to for an radiance model's floors.

    Properties:
        exterior_modifier
        interior_modifier
        modifiers
        modified_modifiers
        is_modified
    """
    __slots__ = ()


@lockable
class RoofCeilingSet(_BaseSet):
    """Set containing all radiance modifiers needed to for an radiance model's roofs.

    Properties:
        exterior_modifier
        interior_modifier
        modifiers
        modified_modifiers
        is_modified
    """
    __slots__ = ()


@lockable
class ApertureSet(_BaseSet):
    """Set containing all radiance modifiers needed to for a radiance model's Apertures.

    Properties:
        window_modifier
        interior_modifier
        skylight_modifier
        operable_modifier
        modifiers
        modified_modifiers
        is_modified
    """
    __slots__ = ('_skylight_modifier', '_operable_modifier')

    def __init__(self, window_modifier=None, interior_modifier=None,
                 skylight_modifier=None, operable_modifier=None):
        """Initialize aperture set.

        Args:
            window_modifier: A window modifier object for apertures
                with an Outdoors boundary condition and Wall parent Face.
            interior_modifier: A window modifier object for apertures
                with a Surface boundary condition.
            skylight_modifier: : A window modifier object for apertures with a
                Outdoors boundary condition, and RoofCeiling or Floor face type for
                their parent face.
            operable_modifier: A window modifier object for apertures
                with an Outdoors boundary condition and a True is_operable property.
        """
        _BaseSet.__init__(self, window_modifier, interior_modifier)
        self.skylight_modifier = skylight_modifier
        self.operable_modifier = operable_modifier

    @property
    def window_modifier(self):
        """Get or set the modifier for glass doors."""
        if self._exterior_modifier is None:
            return _default_modifiers[self.__class__.__name__]['exterior']
        return self._exterior_modifier

    @window_modifier.setter
    def window_modifier(self, value):
        self._exterior_modifier = self._validate_modifier(value)

    @property
    def operable_modifier(self):
        """Get or set the modifier for operable window."""
        if self._operable_modifier is None:
            return _default_modifiers[self.__class__.__name__]['operable']
        return self._operable_modifier

    @operable_modifier.setter
    def operable_modifier(self, value):
        self._operable_modifier = self._validate_modifier(value)

    @property
    def skylight_modifier(self):
        """Get or set the modifier for skylights."""
        if self._skylight_modifier is None:
            return _default_modifiers[self.__class__.__name__]['skylight']
        return self._skylight_modifier

    @skylight_modifier.setter
    def skylight_modifier(self, value):
        self._skylight_modifier = self._validate_modifier(value)

    # TODO: make a decision on validating aperture modifiers
    # though technically it should only be a material that light can go through
    # there are cases that one might need to set the aperture to a black wall
    # probably a good approach is to cast the aperture to a wall face before doing
    # that.
    def _validate_modifier(self, value):
        """Check an modifier before assigning it."""
        if value is not None:
            assert isinstance(value, Primitive) and value.can_be_modifier , \
                'Expected modifier. Got {}'.format(type(value))
            # TODO: Remove the comment once lockable is implemented
            # value.lock()   # lock editing in case modifier has multiple references
        return value

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
        name = self.__class__.__name__.split('Set')[0]
        return '{} Modifier Set:\n Exterior: {}\n Interior: {}' \
            '\n Skylight: {}\n GlassDoor: {}'.format(
            name,
            self.exterior_modifier.name,
            self.interior_modifier.name,
            self._skylight_modifier.name,
            self._glass_door_modifier.name
        )


@lockable
class DoorSet(_BaseSet):
    """Set containing all radiance modifiers needed to for an radiance model's Doors.

    Properties:
        exterior_modifier
        interior_modifier
        exterior_glass_modifier
        interior_glass_modifier
        overhead_modifier
        modifiers
        modified_modifiers
        is_modified
    """
    __slots__ = ('_overhead_modifier', '_exterior_glass_modifier',
                 '_interior_glass_modifier')

    def __init__(self, exterior_modifier=None, interior_modifier=None,
                 exterior_glass_modifier=None, interior_glass_modifier=None,
                 overhead_modifier=None):
        """Initialize aperture set.

        Args:
            exterior_modifier: A window modifier object for apertures
                with an Outdoors boundary condition.
            interior_modifier: A window modifier object for apertures
                with a Surface boundary condition.
            exterior_glass_modifier:
            interior_glass_modifier:
            overhead_modifier: : A window modifier object for doors with an
                Outdoors boundary condition and a RoofCeiling or Floor face type for
                their parent face.
        """
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

    def __len__(self):
        return 3

    def __copy__(self):
        return self.__class__(
            self._exterior_modifier,
            self._interior_modifier,
            self._overhead_modifier
        )

    def __repr__(self):
        name = self.__class__.__name__.split('Set')[0]
        return '{} Modifier Set:\n Exterior: {}\n Interior: {}' \
            '\n Overhead: {}'.format(
            name,
            self.exterior_modifier.name,
            self.interior_modifier.name,
            self._overhead_modifier.name
        )


@lockable
class ShadeSet(_BaseSet):
    """Set containing all radiance modifiers needed to for an radiance model's Shade.

    Properties:
        exterior_modifier
        interior_modifier
        modifiers
        modified_modifiers
        is_modified
    """
    __slots__ = ()


@lockable
class ModifierSet(object):
    """Set containting all radiance modifiers to create a radiance model.

    The ModifierSet has default values for 

    Properties:
        name
        wall_set
        floor_set
        roof_ceiling_set
        aperture_set
        door_set
        shade_set
        modifiers
        modified_modifiers
        unique_modifiers
        unique_modified_modifiers
    """

    __slots__ = ('_name', '_wall_set', '_floor_set', '_roof_ceiling_set',
        '_aperture_set', '_door_set', '_shade_set', '_locked')

    def __init__(self, name, wall_set=None, floor_set=None, roof_ceiling_set=None,
                 aperture_set=None, door_set=None, shade_set=None):
        """Initialize radiance modifier set.

        Args:
            name: Text string for modifier set name.
            wall_set: An optional WallSet object for this ModifierSet.
                If None, it will be the honeybee generic default WallSet.
            floor_set: An optional FloorSet object for this ModifierSet.
                If None, it will be the honeybee generic default FloorSet.
            roof_ceiling_set: An optional RoofCeilingSet object for this ModifierSet.
                If None, it will be the honeybee generic default RoofCeilingSet.
            aperture_set: An optional ApertureSet object for this ModifierSet.
                If None, it will be the honeybee generic default ApertureSet.
            door_set: An optional DoorSet object for this ModifierSet.
                If None, it will be the honeybee generic default DoorSet.
            shade_set: An optional ShadeSet object for this ModifierSet.
                If None, it will be the honeybee generic default ShadeSet.
        """
        self._locked = False  # unlocked by default
        self.name = name
        self.wall_set = wall_set
        self.floor_set = floor_set
        self.roof_ceiling_set = roof_ceiling_set
        self.aperture_set = aperture_set
        self.door_set = door_set
        self.shade_set = shade_set

    @property
    def name(self):
        """Get or set a text string for modifier set name."""
        return self._name

    @name.setter
    def name(self, name):
        self._name = typing.valid_string(name, 'ModifierSet name')

    @property
    def wall_set(self):
        """Get or set the WallSet assigned to this ModifierSet."""
        return self._wall_set

    @wall_set.setter
    def wall_set(self, value):
        if value is not None:
            assert isinstance(value, WallSet), \
                'Expected WallSet. Got {}'.format(type(value))
            self._wall_set = value
        else:
            self._wall_set = WallSet()

    @property
    def floor_set(self):
        """Get or set the FloorSet assigned to this ModifierSet."""
        return self._floor_set

    @floor_set.setter
    def floor_set(self, value):
        if value is not None:
            assert isinstance(value, FloorSet), \
                'Expected FloorSet. Got {}'.format(type(value))
            self._floor_set = value
        else:
            self._floor_set = FloorSet()

    @property
    def roof_ceiling_set(self):
        """Get or set the RoofCeilingSet assigned to this ModifierSet."""
        return self._roof_ceiling_set

    @roof_ceiling_set.setter
    def roof_ceiling_set(self, value):
        if value is not None:
            assert isinstance(value, RoofCeilingSet), \
                'Expected RoofCeilingSet. Got {}'.format(type(value))
            self._roof_ceiling_set = value
        else:
            self._roof_ceiling_set = RoofCeilingSet()

    @property
    def aperture_set(self):
        """Get or set the ApertureSet assigned to this ModifierSet."""
        return self._aperture_set

    @aperture_set.setter
    def aperture_set(self, value):
        if value is not None:
            assert isinstance(value, ApertureSet), \
                'Expected ApertureSet. Got {}'.format(type(value))
            self._aperture_set = value
        else:
            self._aperture_set = ApertureSet()

    @property
    def door_set(self):
        """Get or set the DoorSet assigned to this ModifierSet."""
        return self._door_set

    @door_set.setter
    def door_set(self, value):
        if value is not None:
            assert isinstance(value, DoorSet), \
                'Expected DoorSet. Got {}'.format(type(value))
            self._door_set = value
        else:
            self._door_set = DoorSet()

    @property
    def shade_set(self):
        """Get or set the ShadeSet assigned to this ModifierSet."""
        return self._shade_set

    @shade_set.setter
    def shade_set(self, value):
        if value is not None:
            assert isinstance(value, ShadeSet), \
                'Expected ShadeSet. Got {}'.format(type(value))
            self._shade_set = value
        else:
            self._shade_set = ShadeSet()

    @property
    def modifiers(self):
        """List of all modifiers contained within the set."""
        return self.wall_set.modifiers + \
            self.floor_set.modifiers + \
            self.roof_ceiling_set.modifiers + \
            self.aperture_set.modifiers + \
            self.door_set.modifiers + \
            self.shade_set.modifiers

    @property
    def modified_modifiers(self):
        """List of all modifiers that are not defaulted within the set."""
        return self.wall_set.modified_modifiers + \
            self.floor_set.modified_modifiers + \
            self.roof_ceiling_set.modified_modifiers + \
            self.aperture_set.modified_modifiers + \
            self.door_set.modified_modifiers + \
            self.shade_set.modified_modifiers

    @property
    def unique_modifiers(self):
        """List of all unique modifiers contained within the set."""
        return list(set(self.modifiers))

    @property
    def unique_modified_modifiers(self):
        """List of all unique modifiers that are not defaulted within the set."""
        return list(set(self.modified_modifiers))

    def get_face_modifier(self, face_type, boundary_condition):
        """Get a modifier object that will be assigned to a given type of face.

        Args:
            face_type: Text string for the type of face (eg. 'Wall', 'Floor',
                'Roof', 'AirWall').
            boundary_condition: Text string for the boundary condition
                (eg. 'Outdoors', 'Surface', 'Adiabatic', 'Ground')
        """
        if face_type == 'Wall':
            return self._get_modifier_from_set(self.wall_set, boundary_condition)
        elif face_type == 'Floor':
            return self._get_modifier_from_set(self.floor_set, boundary_condition)
        elif face_type == 'RoofCeiling':
            return self._get_modifier_from_set(self.roof_ceiling_set, boundary_condition)
        elif face_type == 'AirWall':
            return air_wall
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

    def get_door_modifier(self, boundary_condition, parent_face_type):
        """Get a modifier object that will be assigned to a given type of door.

        Args:
            boundary_condition: Text string for the boundary condition
                (eg. 'Outdoors', 'Surface')
            parent_face_type: Text string for the type of face to which the door
                is a child (eg. 'Wall', 'Floor', 'Roof').
        """
        if boundary_condition == 'Outdoors':
            if parent_face_type == 'Wall':
                return self.door_set.exterior_modifier
            else:
                return self.door_set.overhead_modifier
        elif boundary_condition == 'Surface':
            return self.door_set.interior_modifier
        else:
            raise NotImplementedError(
                'Boundary condition {} is not recognized for doors in '
                'ModifierSet'.format(boundary_condition)
                )

    def get_shade_modifier(self, exterior=True):
        """Get a modifier object that will be assigned to a shade.

        Args:
            boundary_condition: A boolean to indicate if the shade is an exterior or and
            interior shade (Default: True).
        """
        if exterior:
            return self.shade_set.exterior_modifier
        else:
            return self.shade_set.interior_modifier

    @classmethod
    def from_dict(cls, data):
        """Create a ModifierSet from a dictionary.

        Note that the dictionary must be a non-abridged version for this
        classmethod to work.

        Args:
            data: Dictionary describing the ModifierSet.
        """
        assert data['type'] == 'ModifierSet', \
            'Expected ModifierSet. Got {}.'.format(data['type'])

        # TODO: build each modifier from JSON
        # TODO: put each set together
        # NOTE: An alternative solution is to implement from_dict to sets
        # and use that to recreate the class.

        raise NotImplementedError('form_dict method is not implemented')

    def to_dict(self, abridged=False, none_for_defaults=True):
        """Get ModifierSet as a dictionary.

        Args:
            abridged: Boolean noting whether detailed materials and modifier
                objects should be written into the ModifierSet (False) or just
                an abridged version (True). Default: False.
            none_for_defaults: Boolean to note whether default modifiers in the
                set should be included in detail (False) or should be None (True).
                Default: True.
        """
        base = {'type': 'ModifierSet'} if not abridged \
            else {'type': 'ModifierSetAbridged'}

        base['name'] = self.name
        base['wall_set'] = self.wall_set._to_dict(none_for_defaults)
        base['floor_set'] = self.floor_set._to_dict(none_for_defaults)
        base['roof_ceiling_set'] = self.roof_ceiling_set._to_dict(none_for_defaults)
        base['aperture_set'] = self.aperture_set._to_dict(none_for_defaults)
        base['door_set'] = self.door_set._to_dict(none_for_defaults)
        base['shade_set'] = self.shade_set._to_dict(none_for_defaults)

        if not abridged:
            modifiers = self.unique_modified_modifiers if none_for_defaults \
                else self.unique_modifiers
            base['modifiers'] = [modifier.to_dict() for modifier in modifiers]

        return base

    def duplicate(self):
        """Get a copy of this ModifierSet."""
        return self.__copy__()

    def lock(self):
        """The lock() method to will also lock the WallSet, FloorSet, etc."""
        self._locked = True
        self._wall_set._locked = True
        self._floor_set._locked = True
        self._roof_ceiling_set._locked = True
        self._aperture_set._locked = True
        self._door_set._locked = True
        self._shade_set._locked = True

    def unlock(self):
        """The unlock() method will also unlock the WallSet, FloorSet, etc."""
        self._locked = False
        self._wall_set._locked = False
        self._floor_set._locked = False
        self._roof_ceiling_set._locked = False
        self._aperture_set._locked = False
        self._door_set._locked = False
        self._shade_set._locked = False

    def _get_modifier_from_set(self, face_type_set, boundary_condition):
        """Get a specific modifier from a face_type_set."""
        if boundary_condition == 'Outdoors':
            return face_type_set.exterior_modifier
        elif boundary_condition in ('Surface', 'Adiabatic', 'Ground'):
            return face_type_set.interior_modifier
        else:
            raise NotImplementedError(
                'Boundary condition {} is not recognized in Face '
                'ModifierSet'.format(boundary_condition)
            )

    def ToString(self):
        """Overwrite .NET ToString."""
        return self.__repr__()

    def __copy__(self):
        return ModifierSet(
            self.name,
            self.wall_set.duplicate(),
            self.floor_set.duplicate(),
            self.roof_ceiling_set.duplicate(),
            self.aperture_set.duplicate(),
            self.door_set.duplicate(),
            self.shade_set.duplicate()
        )

    def __eq__(self, other):
        return isinstance(other, ModifierSet) and self.name == other.name and \
            self.modifiers == other.modifiers

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return 'Radiance Modifier Set: {}'.format(self.name)
