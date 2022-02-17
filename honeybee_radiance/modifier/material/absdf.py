"""Radiance aBSDF Material.

https://floyd.lbl.gov/radiance/refer/ray.html#BSDF
"""
from __future__ import division

import os
from .bsdf import BSDF
from honeybee.config import folders


class aBSDF(BSDF):
    """Radiance aBSDF material.

    .. code-block:: shell

        mod aBSDF id
        5+ BSDFfile ux uy uz funcfile transform
        0
        0|3|6|9
            rfdif gfdif bfdif
            rbdif gbdif bbdif
            rtdif gtdif btdif

    The __init__ method sets additional diffuse reflectance for front and back as well
    as additional diffuse transmittance to 0. You can setup these values by using their
    respective property.

    Args:
        bsdf_file: Path to an xml file. Data will NOT be cached in memory.
        identifier: Text string for a unique Material ID. Must not contain spaces
            or special characters. This will be used to identify the object across
            a model and in the exported Radiance files. If None, the identifier
            will be derived from the bsdf_file name. (Default: None)
        up_orientation: (x, y ,z) vector that sets the hemisphere that the
            BSDF material faces.  For materials that are symmetrical about
            the face plane (like non-angled venetian blinds), this can be
            any vector that is not perfectly normal to the face. For
            asymmetrical materials like angled venetian blinds, this variable
            should be coordinated with the direction the face are facing.
            The default is set to (0.01, 0.01, 1.00), which should hopefully
            not be perpendicular to any typical face.
        modifier: Material modifier (Default: None).
        function_file: Optional input for function file (Default: .).
        transform: Optional transform input to to scale the thickness and reorient
            the up vector (default: None).
        angle_basis: BSDF file angle basis. If not provided by user honeybee tries to
            find it by parsing BSDF file itself.
        dependencies: A list of primitives that this primitive depends on. This
            argument is only useful for defining advanced primitives where the
            primitive is defined based on other primitives. (Default: [])


    Properties:
        * identifier
        * display_name
        * bsdf_file
        * up_orientation
        * function_file
        * transform
        * angle_basis
        * front_diffuse_reflectance
        * back_diffuse_reflectance
        * diffuse_transmittance
        * dependencies
        * values
        * modifier
        * dependencies
        * is_modifier
        * is_material
    """

    __slots__ = ()

    # TODO(): compress file content: https://stackoverflow.com/a/15529390/4394669
    def __init__(self, bsdf_file, identifier=None, up_orientation=None, modifier=None, 
                 function_file='.', transform=None, angle_basis=None, dependencies=None):
        """Create aBSDF material."""
        # thickness is ignored in aBSDF class
        thickness = None
        BSDF.__init__(self, bsdf_file, identifier, up_orientation, thickness,
                 modifier, function_file, transform, angle_basis,
                 dependencies)

    def _update_values(self):
        "update value dictionaries."
        n_path = os.path.normpath(self.bsdf_file).replace('\\', '/')
        f_path = n_path if os.path.isabs(n_path) else './{}'.format(n_path)
        self._values[0] = [
            f_path,
            self.up_orientation.x,
            self.up_orientation.y,
            self.up_orientation.z,
            self.function_file
        ]
        if self.transform:
            self.values[0].append(self.transform)

        if self.front_diffuse_reflectance is not None:
            self._values[2] = list(self.front_diffuse_reflectance)

            if self.back_diffuse_reflectance is not None:
                for v in self.back_diffuse_reflectance:
                    self._values[2].append(v)

            if self.diffuse_transmittance is not None:
                for v in self.diffuse_transmittance:
                    self._values[2].append(v)

    @classmethod
    def from_primitive_dict(cls, primitive_dict):
        """Initialize a aBSDF from a primitive dict.

        Args:
            data: A dictionary in the format below.

        .. code-block:: python

            {
            "modifier": {},  # primitive modifier (Default: None)
            "type": "aBSDF",  # primitive type
            "identifier": "",  # primitive identifier
            "display_name": "",  # primitive display name
            "values": []  # values,
            "dependencies": []
            }

        """
        cls._dict_type_check(cls.__name__, primitive_dict)
        modifier, dependencies = cls.filter_dict_input(primitive_dict)
        values = primitive_dict['values'][0]
        extra_values = primitive_dict['values'][2]

        cls_ = cls(
            bsdf_file=values[0],
            identifier=primitive_dict['identifier'],
            up_orientation=values[1:4],
            modifier=modifier,
            function_file=values[4],
            transform=values[5] if len(values) == 6 else None,
            angle_basis=None,
            dependencies=dependencies
        )
        if 'display_name' in primitive_dict and \
                primitive_dict['display_name'] is not None:
            cls_.display_name = primitive_dict['display_name']

        # this might look redundant but it is NOT. see glass for explanation.
        cls_.values = primitive_dict['values']

        if not extra_values:
            return cls_

        values_length = len(extra_values)
        assert values_length in (3, 6, 9), \
            'Length of real values should be 3, 6 or 9 not %d.' % values_length

        if values_length == 3:
            cls_.front_diffuse_reflectance = extra_values
        elif values_length == 6:
            cls_.front_diffuse_reflectance = extra_values[:3]
            cls_.back_diffuse_reflectance = extra_values[3:]
        else:
            cls_.front_diffuse_reflectance = extra_values[:3]
            cls_.back_diffuse_reflectance = extra_values[3:6]
            cls_.diffuse_transmittance = extra_values[6:]

        return cls_

    @classmethod
    def from_dict(cls, data, folder=None):
        """Initialize a aBSDF from a dictionary.

        Args:
            data: A dictionary in the format below.
            folder: Path to a destination folder to save the bsdf file.

        .. code-block:: python

            {
            "modifier": {},  # material modifier (Default: None)
            "type": "aBSDF",  # Material type
            "identifier": "",  # Material identifer
            "display_name": ""  # Material display name
            "up_orientation": [number, number, number],
            "function_file": string,  # default: '.'
            "transform": string,  # default: None
            "bsdf_data": string,  # bsdf file data as string
            "front_diffuse_reflectance": [number, number, number],  # optional
            "back_diffuse_reflectance": [number, number, number],  # optional
            "diffuse_transmittance": [number, number, number]  # optional
            }
        """
        cls._dict_type_check(cls.__name__, data)
        modifier, dependencies = cls.filter_dict_input(data)

        # check folder and create it if it does not exist
        folder = os.path.join(folders.default_simulation_folder, 'BSDF') \
            if folder is None else folder
        if not os.path.isdir(folder):
            os.makedirs(folder)

        fp = os.path.join(folder, '%s.xml' % data['identifier'])
        # write to xml file
        cls.decompress_to_file(data['bsdf_data'], fp)

        cls_ = cls(
            bsdf_file=fp,
            identifier=data['identifier'],
            up_orientation=data['up_orientation'],
            modifier=modifier,
            dependencies=dependencies
        )
        if 'display_name' in data and data['display_name'] is not None:
            cls_.display_name = data['display_name']

        if 'front_diffuse_reflectance' in data:
            cls_.front_diffuse_reflectance = data['front_diffuse_reflectance']
            if 'back_diffuse_reflectance' in data:
                cls_.back_diffuse_reflectance = data['back_diffuse_reflectance']
                if 'diffuse_transmittance' in data:
                    cls_.diffuse_transmittance = data['diffuse_transmittance']

        return cls_

    def to_dict(self):
        """Convert aBSDF material to a dictionary."""
        bsdf_data = self.compress_file(self.bsdf_file)

        absdf_dict = {
            'modifier': self.modifier.to_dict(),
            'type': 'aBSDF',
            'identifier': self.identifier,
            'up_orientation': self.up_orientation.to_array(),
            'function_file': self.function_file,
            'transform': self.transform,
            'bsdf_data': bsdf_data,
            'dependencies': [dep.to_dict() for dep in self.dependencies]
        }
        if self._display_name is not None:
            absdf_dict['display_name'] = self.display_name

        if self.front_diffuse_reflectance:
            absdf_dict['front_diffuse_reflectance'] = self.front_diffuse_reflectance
            if self.back_diffuse_reflectance:
                absdf_dict['back_diffuse_reflectance'] = self.back_diffuse_reflectance
                if self.diffuse_transmittance:
                    absdf_dict['diffuse_transmittance'] = self.diffuse_transmittance

        return absdf_dict

    def __copy__(self):
        mod, depend = self._dup_mod_and_depend()
        new_absdf = self.__class__(
            self.bsdf_file, self.identifier, self.up_orientation, mod,
            self.function_file, self.transform, self.angle_basis, depend)
        new_absdf._front_diffuse_reflectance = self._front_diffuse_reflectance
        new_absdf._back_diffuse_reflectance = self._back_diffuse_reflectance
        new_absdf._diffuse_transmittance = self._diffuse_transmittance
        new_absdf._display_name = self._display_name
        return new_absdf
