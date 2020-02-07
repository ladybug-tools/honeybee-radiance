# coding=utf-8
"""Model Radiance Properties."""
from honeybee.extensionutil import model_extension_dicts

from ..lib.modifiersets import generic_modifier_set_visible
from ..lib.modifiers import black
from ..modifierset import ModifierSet
from ..modifier.material import BSDF

try:
    from itertools import izip as zip  # python 2
except ImportError:
    pass   # python 3


class ModelRadianceProperties(object):
    """Radiance Properties for Honeybee Model.

    Properties:
        * host
        * modifiers
        * blk_modifiers
        * room_modifiers
        * face_modifiers
        * shade_modifiers
        * bsdf_modifiers
        * modifier_sets
        * global_modifier_set
    """

    def __init__(self, host):
        """Initialize Model radiance properties.

        Args:
            host: A honeybee_core Model object that hosts these properties.
        """
        self._host = host

    @property
    def host(self):
        """Get the Model object hosting these properties."""
        return self._host

    @property
    def modifiers(self):
        """A list of all unique modifiers in the model.

        This includes modifiers across all Faces, Apertures, Doors, Shades,
        Room ModifierSets, and the global_modifier_set.
        
        However, it excludes blk_modifiers and these can be obtained separately
        from the blk_modifiers property.
        """
        all_mods = self.global_modifier_set.modifiers_unique + self.room_modifiers + \
            self.face_modifiers + self.shade_modifiers
        return list(set(all_mods))
    
    @property
    def blk_modifiers(self):
        """A list of all unique modifier_blk assigned to Faces, Apertures and Doors."""
        modifiers = [black]
        for room in self.host.rooms:
            for face in room.faces:  # check all Room Face modifiers
                self._check_and_add_face_modifier_blk(face, modifiers)
        for face in self.host.orphaned_faces:  # check all orphaned Face modifiers
            self._check_and_add_face_modifier_blk(face, modifiers)
        for ap in self.host.orphaned_apertures:  # check all Aperture modifiers
            self._check_and_add_obj_modifier_blk(ap, modifiers)
        for dr in self.host.orphaned_doors:  # check all Door modifiers
            self._check_and_add_obj_modifier_blk(dr, modifiers)
        
        for room in self.host.rooms:
            self._check_and_add_room_modifier_shade_blk(room, modifiers)
        for face in self.host.orphaned_faces:
            self._check_and_add_face_modifier_shade_blk(face, modifiers)
        for ap in self.host.orphaned_apertures:
            self._check_and_add_obj_modifier_shade_blk(ap, modifiers)
        for dr in self.host.orphaned_doors:
            self._check_and_add_obj_modifier_shade_blk(dr, modifiers)
        for shade in self.host.orphaned_shades:
            self._check_and_add_obj_modifier_blk(shade, modifiers)
        return list(set(modifiers))
    
    @property
    def room_modifiers(self):
        """A list of all unique modifiers assigned to Room ModifierSets.
        
        Note that this does not include modifiers in the global_modifier_set.
        For these, you can request global_modifier_set.modifiers_unique.
        """
        room_mods = []
        for cnstr_set in self.modifier_sets:
            room_mods.extend(cnstr_set.modified_modifiers_unique)
        return list(set(room_mods))

    @property
    def face_modifiers(self):
        """A list of all unique modifiers assigned to Faces, Apertures and Doors.
        
        This includes both objects that are a part of Rooms as well as orphaned
        objects. It does not include the modfiers of any shades assigned to these
        objects. Nor does it include any blk modifiers.
        """
        modifiers = []
        for room in self.host.rooms:
            for face in room.faces:  # check all Room Face modifiers
                self._check_and_add_face_modifier(face, modifiers)
        for face in self.host.orphaned_faces:  # check all orphaned Face modifiers
            self._check_and_add_face_modifier(face, modifiers)
        for ap in self.host.orphaned_apertures:  # check all Aperture modifiers
            self._check_and_add_obj_modifier(ap, modifiers)
        for dr in self.host.orphaned_doors:  # check all Door modifiers
            self._check_and_add_obj_modifier(dr, modifiers)
        return list(set(modifiers))

    @property
    def shade_modifiers(self):
        """A list of all unique modifiers assigned to Shades in the model."""
        modifiers = []
        for room in self.host.rooms:
            self._check_and_add_room_modifier_shade(room, modifiers)
        for face in self.host.orphaned_faces:
            self._check_and_add_face_modifier_shade(face, modifiers)
        for ap in self.host.orphaned_apertures:
            self._check_and_add_obj_modifier_shade(ap, modifiers)
        for dr in self.host.orphaned_doors:
            self._check_and_add_obj_modifier_shade(dr, modifiers)
        for shade in self.host.orphaned_shades:
            self._check_and_add_obj_modifier(shade, modifiers)
        return list(set(modifiers))

    @property
    def bsdf_modifiers(self):
        """A list of all unique BSDF modifiers in the model.

        This includes any BSDF modifiers in both the Model.modifiers and the
        Model.blk_modifiers.
        """
        all_mods = self.modifiers + self.blk_modifiers
        return list(set(mod for mod in all_mods if isinstance(mod, BSDF)))

    @property
    def modifier_sets(self):
        """A list of all unique Room-Assigned ModifierSets in the Model."""
        modifier_sets = []
        for room in self.host.rooms:
            if room.properties.radiance._modifier_set is not None:
                if not self._instance_in_array(room.properties.radiance._modifier_set,
                                               modifier_sets):
                    modifier_sets.append(room.properties.radiance._modifier_set)
        return list(set(modifier_sets))  # catch equivalent modifier sets

    @property
    def global_modifier_set(self):
        """A default ModifierSet object for all unassigned objects in the Model.

        This ModifierSet will be written in its entirety to the dictionary
        representation of ModelRadianceProperties as well as the resulting OpenStudio
        model.  This is to ensure that all objects lacking a modifier specification
        always have a default.
        """
        return generic_modifier_set_visible

    def check_duplicate_modifier_names(self, raise_exception=True):
        """Check that there are no duplicate Modifier names in the model."""
        mod_names = set()
        duplicate_names = set()
        for mod in self.modifiers:
            if mod.name not in mod_names:
                mod_names.add(mod.name)
            else:
                duplicate_names.add(mod.name)
        if len(duplicate_names) != 0:
            if raise_exception:
                raise ValueError(
                    'The model has the following duplicated modifier '
                    'names:\n{}'.format('\n'.join(duplicate_names)))
            return False
        return True

    def check_duplicate_modifier_set_names(self, raise_exception=True):
        """Check that there are no duplicate ModifierSet names in the model."""
        mod_set_names = set()
        duplicate_names = set()
        for mod_set in self.modifier_sets + [self.global_modifier_set]:
            if mod_set.name not in mod_set_names:
                mod_set_names.add(mod_set.name)
            else:
                duplicate_names.add(mod_set.name)
        if len(duplicate_names) != 0:
            if raise_exception:
                raise ValueError(
                    'The model has the following duplicated ModifierSet '
                    'names:\n{}'.format('\n'.join(duplicate_names)))
            return False
        return True

    def apply_properties_from_dict(self, data):
        """Apply the radiance properties of a dictionary to the host Model of this object.

        Args:
            data: A dictionary representation of an entire honeybee-core Model.
                Note that this dictionary must have ModelRadianceProperties in order
                for this method to successfully apply the radiance properties.
        """
        assert 'radiance' in data['properties'], \
            'Dictionary possesses no ModelRadianceProperties.'

        modifiers, modifier_sets = self.load_properties_from_dict(data)

        # collect lists of radiance property dictionaries
        room_e_dicts, face_e_dicts, shd_e_dicts, ap_e_dicts, dr_e_dicts = \
            model_extension_dicts(data, 'radiance', [], [], [], [], [])

        # apply radiance properties to objects using the radiance property dictionaries
        for room, r_dict in zip(self.host.rooms, room_e_dicts):
            room.properties.radiance.apply_properties_from_dict(r_dict, modifier_sets)
        for face, f_dict in zip(self.host.faces, face_e_dicts):
            face.properties.radiance.apply_properties_from_dict(f_dict, modifiers)
        for aperture, a_dict in zip(self.host.apertures, ap_e_dicts):
            aperture.properties.radiance.apply_properties_from_dict(a_dict, modifiers)
        for door, d_dict in zip(self.host.doors, dr_e_dicts):
            door.properties.radiance.apply_properties_from_dict(d_dict, modifiers)
        for shade, s_dict in zip(self.host.shades, shd_e_dicts):
            shade.properties.radiance.apply_properties_from_dict(s_dict, modifiers)

    def to_dict(self, include_global_modifier_set=True):
        """Return Model radiance properties as a dictionary.

        include_global_modifier_set: Boolean to note whether the
            global_modifier_set should be included within the dictionary. This
            will ensure that all objects lacking a modifier specification always
            have a default modifier. Default: True.
        """
        base = {'radiance': {'type': 'ModelRadianceProperties'}}

        # add all ModifierSets to the dictionary
        base['radiance']['modifier_sets'] = []
        if include_global_modifier_set:
            base['radiance']['global_modifier_set'] = self.global_modifier_set.name
            base['radiance']['modifier_sets'].append(
                self.global_modifier_set.to_dict(abridged=True, none_for_defaults=False))
        modifier_sets = self.modifier_sets
        for mod_set in modifier_sets:
            base['radiance']['modifier_sets'].append(mod_set.to_dict(abridged=True))

        # add all unique Modifiers to the dictionary
        room_mods = []
        for mod_set in modifier_sets:
            room_mods.extend(mod_set.modified_modifiers_unique)
        all_mods = room_mods + self.face_modifiers + self.shade_modifiers
        if include_global_modifier_set:
            all_mods.extend(self.global_modifier_set.modifiers_unique)
        modifiers = list(set(all_mods))
        base['radiance']['modifiers'] = []
        for mod in modifiers:
            base['radiance']['modifiers'].append(mod.to_dict())

        return base

    def duplicate(self, new_host=None):
        """Get a copy of this object.

        new_host: A new Model object that hosts these properties.
            If None, the properties will be duplicated with the same host.
        """
        _host = new_host or self._host
        return ModelRadianceProperties(_host)

    @staticmethod
    def load_properties_from_dict(data):
        """Load model radiance properties of a dictionary to Python objects.

        Loaded objects include Modifiers and ModifierSets.

        The function is called when re-serializing a Model object from a dictionary
        to load honeybee_radiance objects into their Python object form before
        applying them to the Model geometry.

        Args:
            data: A dictionary representation of an entire honeybee-core Model.
                Note that this dictionary must have ModelRadianceProperties in order
                for this method to successfully load the radiance properties.
        
        Returns:
            modifiers -- A dictionary with names of modifiers as keys and Python
                modifier objects as values.
            modifier_sets -- A dictionary with names of modifier sets as keys
                and Python modifier set objects as values.
        """
        try:  # ensure the putil module is imported, which imports all primitive modules
            putil
        except NameError:
            import honeybee_radiance.putil as putil

        assert 'radiance' in data['properties'], \
            'Dictionary possesses no ModelRadianceProperties.'

        # process all modifiers in the ModelRadianceProperties dictionary
        modifiers = {}
        for mod in data['properties']['radiance']['modifiers']:
            modifiers[mod['name']] = putil.dict_to_modifier(mod)

        # process all modifier sets in the ModelRadianceProperties dictionary
        modifier_sets = {}
        if 'modifier_sets' in data['properties']['radiance'] and \
                data['properties']['radiance']['modifier_sets'] is not None:
            for m_set in data['properties']['radiance']['modifier_sets']:
                modifier_sets[m_set['name']] = \
                    ModifierSet.from_dict_abridged(m_set, modifiers)

        return modifiers, modifier_sets
    
    def _check_and_add_room_modifier_shade(self, room, modifiers):
        """Check if a modifier is assigned to a Room's shades and add it to a list.""" 
        self._check_and_add_obj_modifier_shade(room, modifiers)
        for face in room.faces:  # check all Face modifiers
            self._check_and_add_face_modifier_shade(face, modifiers)

    def _check_and_add_face_modifier_shade(self, face, modifiers):
        """Check if a modifier is assigned to a Face's shades and add it to a list.""" 
        self._check_and_add_obj_modifier_shade(face, modifiers)
        for ap in face.apertures:  # check all Aperture modifiers
            self._check_and_add_obj_modifier_shade(ap, modifiers)
        for dr in face.doors:  # check all Door Shade modifiers
            self._check_and_add_obj_modifier_shade(dr, modifiers)
    
    def _check_and_add_obj_modifier_shade(self, subf, modifiers):
        """Check if a modifier is assigned to an object's shades and add it to a list."""
        for shade in subf.shades:
            self._check_and_add_obj_modifier(shade, modifiers)

    def _check_and_add_room_modifier_shade_blk(self, room, modifiers):
        """Check if a modifier_blk is assigned to a Room's shades and add it to a list.""" 
        self._check_and_add_obj_modifier_shade_blk(room, modifiers)
        for face in room.faces:  # check all Face modifiers
            self._check_and_add_face_modifier_shade_blk(face, modifiers)

    def _check_and_add_face_modifier_shade_blk(self, face, modifiers):
        """Check if a modifier_blk is assigned to a Face's shades and add it to a list.
        """ 
        self._check_and_add_obj_modifier_shade_blk(face, modifiers)
        for ap in face.apertures:  # check all Aperture modifiers
            self._check_and_add_obj_modifier_shade_blk(ap, modifiers)
        for dr in face.doors:  # check all Door Shade modifiers
            self._check_and_add_obj_modifier_shade_blk(dr, modifiers)
    
    def _check_and_add_obj_modifier_shade_blk(self, subf, modifiers):
        """Check if a modifier_blk is assigned to an object's shades and add it to list.
        """
        for shade in subf.shades:
            self._check_and_add_obj_modifier_blk(shade, modifiers)

    def _check_and_add_face_modifier(self, face, modifiers):
        """Check if a modifier is assigned to a face and add it to a list.""" 
        self._check_and_add_obj_modifier(face, modifiers)
        for ap in face.apertures:  # check all Aperture modifiers
            self._check_and_add_obj_modifier(ap, modifiers)
        for dr in face.doors:  # check all Door modifiers
            self._check_and_add_obj_modifier(dr, modifiers)
    
    def _check_and_add_face_modifier_blk(self, face, modifiers):
        """Check if a modifier_blk is assigned to a face and add it to a list.""" 
        self._check_and_add_obj_modifier_blk(face, modifiers)
        for ap in face.apertures:  # check all Aperture modifiers
            self._check_and_add_obj_modifier_blk(ap, modifiers)
        for dr in face.doors:  # check all Door modifiers
            self._check_and_add_obj_modifier_blk(dr, modifiers)

    def _check_and_add_obj_modifier(self, obj, modifiers):
        """Check if a modifier is assigned to an object and add it to a list."""
        constr = obj.properties.radiance._modifier
        if constr is not None:
            if not self._instance_in_array(constr, modifiers):
                modifiers.append(constr)

    def _check_and_add_obj_modifier_blk(self, obj, modifiers):
        """Check if a modifier_blk is assigned to an object and add it to a list."""
        constr = obj.properties.radiance._modifier_blk
        if constr is not None:
            if not self._instance_in_array(constr, modifiers):
                modifiers.append(constr)

    @staticmethod
    def _instance_in_array(object_instance, object_array):
        """Check if a specific object instance is already in an array.

        This can be much faster than  `if object_instance in object_arrary`
        when you expect to be testing a lot of the same instance of an object for
        inclusion in an array since the builtin method uses an == operator to
        test inclusion.
        """
        for val in object_array:
            if val is object_instance:
                return True
        return False

    def ToString(self):
        return self.__repr__()

    def __repr__(self):
        return 'Model Radiance Properties:\n host: {}'.format(self.host.name)
