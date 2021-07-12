# coding=utf-8
"""Object representing a group of sub-faces or shades that change states in unison."""
from __future__ import division

from .state import RadianceShadeState, RadianceSubFaceState
from ..geometry import Polygon
from ..modifier.material import BSDF
from ..lib.modifiers import white_glow

from honeybee.typing import valid_rad_string
from honeybee.shade import Shade
from honeybee.aperture import Aperture
from honeybee.door import Door
from honeybee.boundarycondition import Surface

import os


class DynamicShadeGroup(object):
    """Object representing a group of dynamic shades that change states in unison.

    Note that this object is not intended to set any Model properties. It is only
    used by the Model to collect objects with the same dynamic_group_identifier
    and export a common set of radiance files from them.

    Args:
        identifier: Text string for a unique Group ID. Must not contain spaces
            or special characters. This will be used to identify the object across
            a model and in the exported Radiance files.
        dynamic_objects: An array of Shades that are contained within the group.

    Properties:
        * identifier
        * dynamic_objects
        * state_count
        * is_opaque
        * is_indoor
        * states_json_list
    """

    __slots__ = ('_identifier', '_dynamic_objects', '_state_count')

    def __init__(self, identifier, dynamic_objects):
        """Initialize DynamicShadeGroup."""
        # set identifier
        self._identifier = valid_rad_string(identifier)

        # set the dynamic_objects
        if not isinstance(dynamic_objects, tuple):
            dynamic_objects = tuple(dynamic_objects)
        self._check_dynamic_objects(dynamic_objects)
        self._dynamic_objects = dynamic_objects

        # compute the state_count
        count = 1
        for obj in self.dynamic_objects:
            s_cnt = len(obj.properties.radiance._states)
            if s_cnt > count:
                count = s_cnt
        self._state_count = count

    @property
    def identifier(self):
        """Get a text string for the unique group identifier."""
        return self._identifier

    @property
    def dynamic_objects(self):
        """Get a tuple of objects contained within the group."""
        return self._dynamic_objects

    @property
    def state_count(self):
        """Gat an integer for the total number of states of the dynamic group.

        This is equal to the number of states in the dynamic_object with the
        highest number of states. After a dynamic_object with fewer states than that
        of it's dynamic group has hit its highest state, it just remains in that
        state as the other dynamic_objects continue to change.
        """
        return self._state_count

    @property
    def is_opaque(self):
        """Get a boolean for whether all states of all shades in the group are opaque.
        """
        for obj in self._dynamic_objects:
            for state in obj.properties.radiance._states:
                if not state.modifier.is_opaque:
                    return False
        return True

    @property
    def is_indoor(self):
        """Get a boolean for whether all shades in the group are indoor."""
        for obj in self._dynamic_objects:
            if not obj.is_indoor:
                return False
        return True

    @property
    def states_json_list(self):
        """A list for the states.json file that notes the files for each state.

        The files will follow a standard naming convention as follows.
        <dynamic group identifier>..<field name>..<state count>.rad.
        For instance skylight..direct..000.rad
        """
        ident = self.identifier
        states_list = []
        for st_i in range(self.state_count):
            states_list.append({
                'identifier': '{}_{}'.format(st_i, ident),
                'default': './{}..default..{}.rad'.format(ident, str(st_i)),
                'direct': './{}..direct..{}.rad'.format(ident, str(st_i))
                })
        return states_list

    def states_by_index(self, state_index):
        """Get an array of state objects representing a single state for this group.

        The resulting array will parallel the dynamic_objects of this group, with
        one state object per dynamic object.

        Args:
            state_index: An interger from 0 up to the state_count - 1 , which notes
                the state of the group for which a rad string will be produced.
        """
        # make sure that the state_index is valid
        assert 0 <= state_index < self.state_count, '"{}" is not a valid state index ' \
            'for dynamic group "{}".'.format(state_index, self.identifier)

        # gather the state objects that correspond to the state_index
        states = []
        for obj in self._dynamic_objects:
            try:  # try to get the state at the correct index
                states.append(obj.properties.radiance._states[state_index])
            except IndexError:  # use the last state that is available
                try:
                    states.append(obj.properties.radiance._states[-1])
                except IndexError:  # no states assigned; create default a dummy state
                    st = RadianceShadeState()
                    st._parent  = obj
                    states.append(st)
        return states

    def to_radiance(self, state_index, direct=False, minimal=False):
        """Generate a RAD string representation of a state for this group.

        The resulting string includes everything going into a single .rad file
        to simulate the state, including all geometry and modifiers.

        Args:
            state_index: An interger from 0 up to the state_count - 1 , which notes
                the state of the group for which a rad string will be produced.
            direct: Boolean to note whether to write the "direct" version of the
                state. (Default: False)
            minimal: Boolean to note whether the radiance string should be written
                in a minimal format (with spaces instead of line breaks). Default: False.
        """
        states = self.states_by_index(state_index)

        # gather all unique modifiers across the geometry of the state
        modifiers = []
        if not direct:
            for state in states:
                mod = state.modifier
                if not self._instance_in_array(mod, modifiers):
                    modifiers.append(mod)
                for shd in state._shades:
                    mod = shd.modifier
                    if not self._instance_in_array(mod, modifiers):
                        modifiers.append(mod)
        else:  # use modifier_direct
            for state in states:
                mod = state.modifier_direct
                if not self._instance_in_array(mod, modifiers):
                    modifiers.append(mod)
                for shd in state._shades:
                    mod = shd.modifier_direct
                    if not self._instance_in_array(mod, modifiers):
                        modifiers.append(mod)
        modifiers = list(set(modifiers))

        # get rad strings for all modifier and geometry.
        state_str = ['# STATE {} for "{}"'.format(state_index, self.identifier)]
        for mod in modifiers:
            if isinstance(mod, BSDF):
                self._process_bsdf_modifier(mod, state_str, minimal)
            else:
                state_str.append(mod.to_radiance(minimal))
        for state in states:
            state_str.append(state.to_radiance(direct, minimal))
        return '\n\n'.join(state_str)

    @staticmethod
    def _check_dynamic_objects(dynamic_objects):
        for obj in dynamic_objects:
            assert isinstance(obj, Shade), \
                'Expected Shade for DynamicShadeGroup. Got {}.'.format(type(obj))

    @staticmethod
    def _process_bsdf_modifier(modifier, mod_strs, minimal):
        """Process a BSDF modifier for a radiance model folder."""
        bsdf_name = os.path.split(modifier.bsdf_file)[-1]
        mod_dup = modifier.duplicate()  # duplicate to avoid editing the original
        # the hidden _bsdf_file property is edited since the file has not yet been copied
        mod_dup._bsdf_file = os.path.join('model', 'bsdf', bsdf_name)
        mod_strs.insert(1, mod_dup.to_radiance(minimal))

    @staticmethod
    def _instance_in_array(object_instance, object_array):
        """Check if a specific object instance is already in an array.

        This can be much faster than  `if object_instance in object_array`
        when you expect to be testing a lot of the same instance of an object for
        inclusion in an array since the builtin method uses an == operator to
        test inclusion.
        """
        for val in object_array:
            if val is object_instance:
                return True
        return False

    def __repr__(self):
        return 'Dynamic Shade Group: {}'.format(self.identifier)


class DynamicSubFaceGroup(DynamicShadeGroup):
    """A group of dynamic Apertures and Doors that change states in unison.

    Note that this object is not intended to set any Model properties. It is only
    used by the Model to collect objects with the same dynamic_group_identifier
    and export a common set of radiance files from them.

    Args:
        identifier: Text string for a unique Group ID. Must not contain spaces
            or special characters. This will be used to identify the object across
            a model and in the exported Radiance files.
        dynamic_objects: An array of Shades that are contained within the group.

    Properties:
        * identifier
        * dynamic_objects
        * state_count
        * is_opaque
        * is_indoor
        * states_json_list
    """
    __slots__ = ()

    def __init__(self, modifier, dynamic_objects):
        """Initialize DynamicSubFaceGroup."""
        DynamicShadeGroup.__init__(self, modifier, dynamic_objects)

    @property
    def is_opaque(self):
        """Always False for dynamic sub-faces."""
        return False

    @property
    def is_indoor(self):
        """Get a boolean for whether all sub-faces in the group have a Surface BC."""
        for obj in self._dynamic_objects:
            if not isinstance(obj.boundary_condition, Surface):
                return False
        return True

    @property
    def states_json_list(self):
        """A list for the states.json file that notes the files for each state.

        The files will follow a standard naming convention as follows.
        <dynamic group identifier>..<field name>..<state count>.rad.
        For instance skylight..direct..000.rad

        Note that this list does not contain the tmtx, vmtx, or dmtx keys
        and these should be added separately if this states.json is to be used for
        3-phase studies.
        """
        ident = self.identifier
        states_list = []
        for st_i in range(self.state_count):
            states_list.append({
                'identifier': '{}_{}'.format(st_i, ident),
                'default': './{}..default..{}.rad'.format(ident, str(st_i)),
                'direct': './{}..direct..{}.rad'.format(ident, str(st_i)),
                'black': './{}..black.rad'.format(ident)
                })
        return states_list

    def states_by_index(self, state_index):
        """Get an array of state objects representing a single state for this group.

        The resulting array will parallel the dynamic_objects of this group, with
        one state object per dynamic object.

        Args:
            state_index: An interger from 0 up to the state_count - 1 , which notes
                the state of the group for which a rad string will be produced.
        """
        # make sure that the state_index is valid
        assert 0 <= state_index < self.state_count, '"{}" is not a valid state index ' \
            'for dynamic group "{}".'.format(state_index, self.identifier)

        # gather the state objects that correspond to the state_index
        states = []
        for obj in self._dynamic_objects:
            try:  # try to get the state at the correct index
                states.append(obj.properties.radiance._states[state_index])
            except IndexError:  # use the last state that is available
                try:
                    states.append(obj.properties.radiance._states[-1])
                except IndexError:  # no states assigned; create default a dummy state
                    st = RadianceSubFaceState()
                    st._parent  = obj
                    states.append(st)
        return states

    def blk_to_radiance(self, minimal=False):
        """Generate a RAD string for the black representation of this group.

        The resulting string includes everything going into the black .rad file,
        including all geometry and modifiers.

        Args:
            minimal: Boolean to note whether the radiance string should be written
                in a minimal format (with spaces instead of line breaks). Default: False.
        """
        # gather all unique modifier_blk and write geometry rad strings
        blk_str = ['# BLACK representation for "{}"'.format(self.identifier)]
        modifiers = []
        for obj in self._dynamic_objects:
            mod = obj.properties.radiance.modifier_blk
            base_poly = Polygon(obj.identifier, obj.vertices, mod)
            blk_str.append(base_poly.to_radiance(minimal, False, False))
            if not self._instance_in_array(mod, modifiers):
                modifiers.append(mod)
        modifiers = list(set(modifiers))

        # get rad strings for all modifiers.
        for mod in modifiers:
            if isinstance(mod, BSDF):
                self._process_bsdf_modifier(mod, blk_str, minimal)
            else:
                blk_str.insert(1, mod.to_radiance(minimal))
        return '\n\n'.join(blk_str)

    def tmxt_bsdf(self, state_index):
        """A BSDF modifier representing the tranmission matrix of a state if it exists.

        This will be None unless all of the objects in the group have the same
        BSDF modifier for the state. Note that having a single tmxt_bsdf
        is a requirement in order to be compatible with 3-phase and 5-phase
        simulation.

        Args:
            state_index: An interger from 0 up to the state_count - 1 , which notes
                the state of the group for which a rad string will be produced.
        """
        bsdf_mods = []
        for state in self.states_by_index(state_index):
            mod = state.modifier
            if not isinstance(mod, BSDF):
                return None  # not a BSDF; not valid for 3-phase
            elif not self._instance_in_array(mod, bsdf_mods):
                bsdf_mods.append(mod)
        if len(set(bsdf_mods)) != 1:
            return None  # more than one type of BSDF; not valid for 3-phase
        return bsdf_mods[0]  # just one BSDF for the t_mtx; it's valid!

    def vmtx_to_radiance(self, state_index, minimal=False):
        """Generate a vmtx RAD string representation of a state.

        The resulting string has all geometry geometry and the white_glow modifier.

        Args:
            state_index: An interger from 0 up to the state_count - 1 , which notes
                the state of the group for which a rad string will be produced.
            minimal: Boolean to note whether the radiance string should be written
                in a minimal format (with spaces instead of line breaks). Default: False.
        """
        states = self.states_by_index(state_index)
        # get rad strings for the white_glow modifier and geometry.
        state_str = ['# VMTX representation for "{}"'.format(self.identifier),
                     white_glow.to_radiance(minimal)]
        for state in states:
            state_str.append(state.vmtx_to_radiance(minimal))
        return '\n\n'.join(state_str)

    def dmtx_to_radiance(self, state_index, minimal=False):
        """Generate a dmtx RAD string representation of a state.

        The resulting string has all geometry geometry and the white_glow modifier.

        Args:
            state_index: An interger from 0 up to the state_count - 1 , which notes
                the state of the group for which a rad string will be produced.
            minimal: Boolean to note whether the radiance string should be written
                in a minimal format (with spaces instead of line breaks). Default: False.
        """
        states = self.states_by_index(state_index)
        # get rad strings for the white_glow modifier and geometry.
        state_str = ['# DMTX representation for "{}"'.format(self.identifier),
                     white_glow.to_radiance(minimal)]
        for state in states:
            state_str.append(state.dmtx_to_radiance(minimal))
        return '\n\n'.join(state_str)

    @staticmethod
    def _check_dynamic_objects(dynamic_objects):
        for obj in dynamic_objects:
            assert isinstance(obj, (Aperture, Door)), 'Expected Aperture or Door ' \
                'for DynamicSubFaceGroup. Got {}.'.format(type(obj))

    def __repr__(self):
        return 'Dynamic SubFace Group: {}'.format(self.identifier)
