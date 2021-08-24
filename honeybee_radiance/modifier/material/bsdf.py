"""Radiance BSDF Material.

http://radsite.lbl.gov/radiance/refer/ray.html#Glass
"""
from __future__ import division

import os
from .materialbase import Material
from honeybee.config import folders
import honeybee.typing as typing
import ladybug_geometry.geometry3d.pointvector as pv


class BSDF(Material):
    """Radiance BSDF material.

    .. code-block:: shell

        mod BSDF id
        6+ thick BSDFfile ux uy uz funcfile transform
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
        thickness: Optional number to set the thickness of the BSDF material.
            (default: 0).
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
        * thickness
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
    __slots__ = ('_bsdf_file', '_up_orientation', '_thickness', '_function_file',
                 '_transform', '_angle_basis', '_front_diffuse_reflectance',
                 '_back_diffuse_reflectance', '_diffuse_transmittance')

    # TODO(): compress file content: https://stackoverflow.com/a/15529390/4394669
    def __init__(self, bsdf_file, identifier=None, up_orientation=None, thickness=0,
                 modifier=None, function_file='.', transform=None, angle_basis=None,
                 dependencies=None):
        """Create BSDF material."""
        identifier = identifier or '.'.join(os.path.split(bsdf_file)[-1].split('.')[:-1])

        Material.__init__(self, identifier, modifier=modifier,
                          dependencies=dependencies)

        self.bsdf_file = bsdf_file
        self.angle_basis = angle_basis
        self.up_orientation = up_orientation
        self.thickness = thickness or 0
        self.function_file = function_file
        self.transform = transform
        self._front_diffuse_reflectance = None
        self._back_diffuse_reflectance = None
        self._diffuse_transmittance = None
        self._update_values()

    def _update_values(self):
        "update value dictionaries."
        n_path = os.path.normpath(self.bsdf_file).replace('\\', '/')
        f_path = n_path if os.path.isabs(n_path) else './{}'.format(n_path)
        self._values[0] = [
            float(self.thickness),
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

    @property
    def bsdf_file(self):
        """Path to BSDF file."""
        return self._bsdf_file

    @bsdf_file.setter
    def bsdf_file(self, bsdf_file):
        assert os.path.isfile(
            bsdf_file), 'No such file at: {}'.format(bsdf_file)
        assert bsdf_file.lower().endswith('.xml'), \
            'BSDF file must be an xml file: {}'.format(bsdf_file)
        self._bsdf_file = os.path.normpath(bsdf_file).replace('\\', '/')
        if not hasattr(self, '_angle_basis'):
            # first time that file is assigned
            pass
        else:
            self.find_angle_basis(bsdf_file)

    @property
    def up_orientation(self):
        """Get or set the up normal vector.

        (x, y ,z) vector that sets the hemisphere that the
        BSDF material faces.  For materials that are symmetrical about
        the face plane (like non-angled venetian blinds), this can be
        any vector that is not perfectly normal to the face. For
        asymmetrical materials like angled venetian blinds, this variable
        should be coordinated with the direction the face are facing.
        The default is set to (0.01, 0.01, 1.00), which should hopefully
        not be perpendicular to any typical face.
        """
        return self._up_orientation

    @up_orientation.setter
    def up_orientation(self, vector):
        if vector:
            up_vector = pv.Vector3D(*[float(v) for v in vector])
        else:
            up_vector = pv.Vector3D(0.01, 0.01, 1.00)

        self._up_orientation = up_vector

    @property
    def thickness(self):
        """Get or set a number for the thickness of the BSDF material (default: 0).

        If a view or shadow ray hits a BSDF proxy with non-zero thickness, it will pass
        directly through as if the surface were not there. Similar to the illum type,
        this permits direct viewing and shadow testing of complex geometry. The BSDF is
        used when a scattered (indirect) ray hits the surface, and any transmitted sample
        rays will be offset by the thickness amount to avoid the hidden geometry and
        gather samples from the other side. In this manner, BSDF surfaces can improve the
        results for indirect scattering from complex systems without sacrificing
        appearance or shadow accuracy. If the BSDF has transmission and back-side
        reflection data, a parallel BSDF surface may be placed slightly less than the
        given thickness away from the front surface to enclose the complex geometry on
        both sides. The sign of the thickness is important, as it indicates whether the
        proxied geometry is behind the BSDF surface (when thickness is positive) or in
        front (when thickness is negative)
        """
        return self._thickness

    @thickness.setter
    def thickness(self, value):
        self._thickness = float(value)

    @property
    def function_file(self):
        """Get or set the path to function file."""
        return self._function_file

    @function_file.setter
    def function_file(self, value):
        self._function_file = value or '.'

    @property
    def transform(self):
        """Get or set the transform.

        This is optional and is used to scale the thickness and reorient the
        up vector. (Default: None).
        """
        return self._transform

    @transform.setter
    def transform(self, value):
        self._transform = value

    @property
    def angle_basis(self):
        """Get or set a string for the BSDF file angle basis.

        Valid values are Klems Full, Klems Half, Klems Quarter and TensorTree
        """
        return self._angle_basis

    @angle_basis.setter
    def angle_basis(self, value):
        if value:
            assert value in (
                'Klems Full', 'Klems Half',
                'Klems Quarter', 'TensorTree'), '{} is not a valid angle basis.'
            self._angle_basis = value
        else:
            self._angle_basis = self.find_angle_basis(self.bsdf_file)

    @property
    def front_diffuse_reflectance(self):
        """Get or set the additional front diffuse reflectance."""
        return self._front_diffuse_reflectance

    @front_diffuse_reflectance.setter
    def front_diffuse_reflectance(self, value):
        if value is not None:
            value = typing.tuple_with_length(value, 3)

        self._front_diffuse_reflectance = value

    @property
    def back_diffuse_reflectance(self):
        """Get or set the additional back diffuse reflectance."""
        return self._back_diffuse_reflectance

    @back_diffuse_reflectance.setter
    def back_diffuse_reflectance(self, value):
        if value is not None:
            value = typing.tuple_with_length(value, 3)

        self._back_diffuse_reflectance = value

    @property
    def diffuse_transmittance(self):
        """Get or set the additional diffuse transmittance."""
        return self._diffuse_transmittance

    @diffuse_transmittance.setter
    def diffuse_transmittance(self, value):
        if value is not None:
            value = typing.tuple_with_length(value, 3)

        self._diffuse_transmittance = value

    @classmethod
    def from_primitive_dict(cls, primitive_dict):
        """Initialize a BSDF from a primitive dict.

        Args:
            data: A dictionary in the format below.

        .. code-block:: python

            {
            "modifier": {},  # primitive modifier (Default: None)
            "type": "BSDF",  # primitive type
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
            thickness=values[0],
            bsdf_file=values[1],
            identifier=primitive_dict['identifier'],
            up_orientation=values[2:5],
            modifier=modifier,
            function_file=values[5],
            transform=values[6] if len(values) == 7 else None,
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
        """Initialize a BSDF from a dictionary.

        Args:
            data: A dictionary in the format below.
            folder: Path to a destination folder to save the bsdf file.

        .. code-block:: python

            {
            "modifier": {},  # material modifier (Default: None)
            "type": "BSDF",  # Material type
            "identifier": "",  # Material identifer
            "display_name": ""  # Material display name
            "up_orientation": [number, number, number],
            "thickness": float,  # default: 0
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
            thickness=data['thickness'],
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
        """Convert BSDF material to a dictionary."""
        bsdf_data = self.compress_file(self.bsdf_file)

        bsdf_dict = {
            'modifier': self.modifier.to_dict(),
            'type': 'BSDF',
            'identifier': self.identifier,
            'up_orientation': self.up_orientation.to_array(),
            'thickness': self.thickness,
            'function_file': self.function_file,
            'transform': self.transform,
            'bsdf_data': bsdf_data,
            'dependencies': [dep.to_dict() for dep in self.dependencies]
        }
        if self._display_name is not None:
            bsdf_dict['display_name'] = self.display_name

        if self.front_diffuse_reflectance:
            bsdf_dict['front_diffuse_reflectance'] = self.front_diffuse_reflectance
            if self.back_diffuse_reflectance:
                bsdf_dict['back_diffuse_reflectance'] = self.back_diffuse_reflectance
                if self.diffuse_transmittance:
                    bsdf_dict['diffuse_transmittance'] = self.diffuse_transmittance

        return bsdf_dict

    @staticmethod
    def find_angle_basis(bsdf_file, max_ln_count=2000):
        """Find angle basis in an xml file."""
        # find data structure first
        with open(bsdf_file, 'r') as inf:
            for count, line in enumerate(inf):
                if line.strip().startswith('<IncidentDataStructure>'):
                    # get data structure
                    data_structure = line.replace('<IncidentDataStructure>', '') \
                        .replace('</IncidentDataStructure>', '').strip()
                    break
                assert count < max_ln_count, \
                    'Failed to find IncidentDataStructure in first %d lines. ' \
                    'You can check the file by opening the file in a text editor ' \
                    'and search for <IncidentDataStructure>' % max_ln_count

        # now find the angle basis
        if data_structure.startswith('TensorTree'):
            return 'TensorTree'
        elif data_structure.lower() == 'columns':
            # look for AngleBasisName
            with open(bsdf_file, 'r') as inf:
                for i in range(count):
                    next(inf)
                for count, line in enumerate(inf):
                    if line.strip().startswith('<AngleBasisName>'):
                        angle_basis = line.replace('<AngleBasisName>', '') \
                            .replace('</AngleBasisName>', '').replace('LBNL/', '') \
                            .strip()
                        return angle_basis
                    assert count < max_ln_count, \
                        'Failed to find AngleBasisName in first %d lines. ' \
                        'You can check the file by opening the file in a text editor ' \
                        'and search for <AngleBasisName>' % max_ln_count
        else:
            raise ValueError(
                'Unknown IncidentDataStructure: {}'.format(data_structure))

    @staticmethod
    def compress_file(filepath):
        """Compress bsdf data in an XML file to a string."""
        # TODO: Research better ways to compress the file
        with open(filepath, 'r') as input_file:
            content = input_file.read()
        return content

    @staticmethod
    def decompress_to_file(value, filepath):
        """Write bsdf data string to a file."""
        with open(filepath, 'w') as output_file:
            output_file.write(value)

    def __copy__(self):
        mod, depend = self._dup_mod_and_depend()
        new_bsdf = self.__class__(
            self.bsdf_file, self.identifier, self.up_orientation, self.thickness, mod,
            self.function_file, self.transform, self.angle_basis, depend)
        new_bsdf._front_diffuse_reflectance = self._front_diffuse_reflectance
        new_bsdf._back_diffuse_reflectance = self._back_diffuse_reflectance
        new_bsdf._diffuse_transmittance = self._diffuse_transmittance
        new_bsdf._display_name = self._display_name
        return new_bsdf
