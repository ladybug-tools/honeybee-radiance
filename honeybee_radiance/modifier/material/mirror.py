"""Radiance Mirror Material.

http://radsite.lbl.gov/radiance/refer/ray.html#Mirror
"""
from __future__ import division
from .materialbase import Material
import honeybee.typing as typing
from ...primitive import Void


VOID = Void()


class Mirror(Material):
    """Radiance mirror material.

    Mirror is used for planar surfaces that produce virtual source reflections. This
    material should be used sparingly, as it may cause the light source calculation to
    blow up if it is applied to many small surfaces. This material is only supported for
    flat surfaces such as polygons and rings. The arguments are simply the
    RGB reflectance values, which should be between 0 and 1.

    An optional string argument may be used (like the illum type) to specify a different
    material to be used for shading non-source rays. If this alternate material is given
    as "void", then the mirror surface will be invisible. Using "void" is only
    appropriate if the surface hides other (more detailed) geometry with the same
    overall reflectance. 

    Args:
        identifier: Text string for a unique Material ID. Must not contain spaces
            or special characters. This will be used to identify the object across
            a model and in the exported Radiance files.
        r_reflectance: Reflectance for red. The value should be between 0 and 1
            (Default: 1).
        g_reflectance: Reflectance for green. The value should be between 0 and 1
            (Default: 1).
        b_reflectance: Reflectance for blue. The value should be between 0 and 1
            (Default: 1).
        modifier: Material modifier (Default: None).
        alternate_material: An optional material (like the illum type) used to
            specify a different material to be used for shading non-source rays.
            If None, this will keep the alternat_material as mirror. If this alternate
            material is given as "void", then the mirror surface will be invisible.
            Using "void" is only appropriate if the surface hides other (more
            detailed) geometry with the same overall reflectance (Default: None).
        dependencies: A list of primitives that this primitive depends on. This
            argument is only useful for defining advanced primitives where the
            primitive is defined based on other primitives (Default: []).

    Properties:
        * identifier
        * display_name
        * r_reflectance
        * g_reflectance
        * b_reflectance
        * average_reflectance
        * values
        * modifier
        * alternate_material
        * dependencies
        * is_modifier
        * is_material

    Usage:

    .. code-block:: python

        mirror_material = Mirror("mirror_material", 0.95, .95, .95)
        print(mirror_material)
    """

    __slots__ = ('_r_reflectance', '_g_reflectance', '_b_reflectance',
                 '_alternate_material',)

    def __init__(
        self, identifier, r_reflectance=1.0, g_reflectance=1.0, b_reflectance=1.0,
            modifier=None, alternate_material=None, dependencies=None):
        """Create mirror material."""
        # add alternate material as a dependency if provided
        self._alternate_material = None  # placeholder for alternate material
        Material.__init__(self, identifier, modifier=modifier, dependencies=dependencies)
        self.r_reflectance = r_reflectance
        self.g_reflectance = g_reflectance
        self.b_reflectance = b_reflectance
        self.alternate_material = alternate_material
        self._update_values()

    def _update_values(self):
        "update value dictionaries."
        if self.alternate_material is not None:
            self._values[0] = [self.alternate_material.identifier]
        self._values[2] = [
            self.r_reflectance, self.g_reflectance, self.b_reflectance,
        ]

    @property
    def r_reflectance(self):
        """Get or set reflectance for red channel.

        The value should be between 0 and 1 (Default: 0).
        """
        return self._r_reflectance

    @r_reflectance.setter
    def r_reflectance(self, reflectance):
        self._r_reflectance = \
            typing.float_in_range(reflectance, 0, 1, 'red reflectance')

    @property
    def g_reflectance(self):
        """Get or set reflectance for green channel.

        The value should be between 0 and 1 (Default: 0).
        """
        return self._g_reflectance

    @g_reflectance.setter
    def g_reflectance(self, reflectance):
        self._g_reflectance = \
            typing.float_in_range(reflectance, 0, 1, 'green reflectance')

    @property
    def b_reflectance(self):
        """Get or set reflectance for blue channel.

        The value should be between 0 and 1 (Default: 0).
        """
        return self._b_reflectance

    @b_reflectance.setter
    def b_reflectance(self, reflectance):
        self._b_reflectance = \
            typing.float_in_range(reflectance, 0, 1, 'blue reflectance')

    @property
    def alternate_material(self):
        """Get or set an optional material for shading non-source rays.

        If None, this will keep the alternat_material as mirror. If this alternate
        material is given as "void", then the mirror surface will be invisible.
        Using "void" is only appropriate if the surface hides other (more
        detailed) geometry with the same overall reflectance.
        """
        return self._alternate_material

    @alternate_material.setter
    def alternate_material(self, material):
        if material is not None:
            assert isinstance(material, (Material, Void)), \
                'alternate material must be from type Material not {}'.format(
                type(material))

        self._alternate_material = material

    @property
    def dependencies(self):
        """Get list of dependencies for this primitive.

        Additional dependencies can be added with the add_dependent method.
        """
        return self._dependencies if not self.alternate_material \
            else self._dependencies + [self.alternate_material]

    @classmethod
    def from_single_reflectance(
        cls, identifier, rgb_reflectance=0.0, modifier=None, alternate_material=None,
            dependencies=None):
        """Create mirror material with single reflectance value.

        Args:
            identifier: Text string for a unique Material ID. Must not contain spaces
                or special characters. This will be used to identify the object across
                a model and in the exported Radiance files.
            rgb_reflectance: Reflectance for red, green and blue. The value should be
                between 0 and 1 (Default: 0).
            modifier: Material modifier (Default: None).
            alternate_material: An optional material may be used like the illum type to
                specify a different material to be used for shading non-source rays.
                If None, this will keep the alternat_material as mirror. If this alternate
                material is given as "void", then the mirror surface will be invisible.
                Using "void" is only appropriate if the surface hides other (more
                detailed) geometry with the same overall reflectance (Default: None).
            dependencies: A list of primitives that this primitive depends on. This
                argument is only useful for defining advanced primitives where the
                primitive is defined based on other primitives. (Default: [])

        Usage:

        .. code-block:: python

            wall_material = Mirror.by_single_reflect_value("mirror", 1.0)
        """
        return cls(
            identifier, rgb_reflectance, rgb_reflectance, rgb_reflectance,
            modifier, alternate_material, dependencies
        )

    @classmethod
    def from_primitive_dict(cls, primitive_dict):
        """Initialize mirror from a primitive dict.

        Args:
            data: A dictionary in the format below.

        .. code-block:: python

            {
            "modifier": {},  # primitive modifier (Default: None)
            "type": "mirror",  # primitive type
            "identifier": "",  # primitive identifier
            "display_name": "",  # primitive display name
            "values": [],  # values
            "dependencies": []
            }
        """
        cls._dict_type_check(cls.__name__, primitive_dict)
        modifier, dependencies = cls.filter_dict_input(primitive_dict)
        if len(primitive_dict['values'][0]) == 1:
            # find name
            alt_id = primitive_dict['values'][0][0]
            if alt_id == 'void':
                alternate_material = VOID
            elif isinstance(alt_id, dict):
                try:  # see if the mutil module has already been imported
                    mutil
                except NameError:
                    # import the module here to avoid a circular import
                    import honeybee_radiance.mutil as mutil
                alternate_material = mutil.dict_to_modifier(alt_id)
            else:
                alt_mats = [d for d in dependencies if d.identifier == alt_id]

                assert len(alt_mats) == 1, \
                    'Failed to find alternate material for mirror: "{}" in ' \
                    'dependencies.'.format(alt_id)

                # remove it from dependencies
                alternate_material = alt_mats[0]
                dependencies.remove(alternate_material)
        else:
            alternate_material = None

        values = primitive_dict['values'][2]
        cls_ = cls(
            identifier=primitive_dict["identifier"],
            r_reflectance=values[0],
            g_reflectance=values[1],
            b_reflectance=values[2],
            modifier=modifier,
            alternate_material=alternate_material,
            dependencies=dependencies
        )
        if 'display_name' in primitive_dict \
                and primitive_dict['display_name'] is not None:
            cls_.display_name = primitive_dict['display_name']

        # this might look redundant but it is NOT. see glass for explanation.
        cls_.values = primitive_dict['values']
        return cls_

    @classmethod
    def from_dict(cls, data):
        """Initialize Mirror from a dictionary.

        Args:
            data: A dictionary in the format below.

        .. code-block:: python

            {
            "type": "Mirror",  # Material type
            "identifier": "",  # Material identifier
            "display_name": "",  # Material display name
            "r_reflectance": float,  # Reflectance for red
            "g_reflectance": float,  # Reflectance for green
            "b_reflectance": float,  # Reflectance for blue
            "modifier": {},  # Material modifier (Default: None)
            "alternate_material": {},  # optional alternate material
            "dependencies": []
            }
        """
        cls._dict_type_check(cls.__name__, data)
        modifier, dependencies = cls.filter_dict_input(data)
        if 'alternate_material' in data and data['alternate_material']:
            # alternate material
            if data['alternate_material'] == 'void':
                alternate_material = VOID
            else:
                try:  # see if the mutil module has already been imported
                    mutil
                except NameError:
                    # import the module here to avoid a circular import
                    import honeybee_radiance.mutil as mutil
                alternate_material = mutil.dict_to_modifier(data['alternate_material'])
        else:
            alternate_material = None

        new_obj = cls(identifier=data["identifier"],
                      r_reflectance=data["r_reflectance"],
                      g_reflectance=data["g_reflectance"],
                      b_reflectance=data["b_reflectance"],
                      modifier=modifier,
                      alternate_material=alternate_material,
                      dependencies=dependencies)
        if 'display_name' in data and data['display_name'] is not None:
            new_obj.display_name = data['display_name']
        return new_obj

    def to_dict(self):
        """Translate this object to a dictionary."""
        base = {
            'modifier': self.modifier.to_dict(),
            'type': 'Mirror',
            'identifier': self.identifier,
            'r_reflectance': self.r_reflectance,
            'g_reflectance': self.g_reflectance,
            'b_reflectance': self.b_reflectance,
            # dependencies without alternate material
            'dependencies': [dp.to_dict() for dp in self._dependencies]
        }
        if self.alternate_material:
            if isinstance(self.alternate_material, Void):
                base['alternate_material'] = {'type': 'void'}
            else:
                base['alternate_material'] = self.alternate_material.to_dict()
        else:
            base['alternate_material'] = None
        if self._display_name is not None:
            base['display_name'] = self.display_name
        return base

    def __copy__(self):
        mod, depend = self._dup_mod_and_depend()
        alt_mat = None if not self.alternate_material \
            else self.alternate_material.duplicate()
        new_obj = self.__class__(
            self.identifier, self.r_reflectance, self.g_reflectance, self.b_reflectance,
            mod, alt_mat, depend)
        new_obj._display_name = self._display_name
        return new_obj
