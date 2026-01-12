"""Luminaire."""
import os
import io
import math

from ladybug_geometry.geometry3d import Vector3D, Point3D
from honeybee_radiance_command.ies2rad import Ies2rad, Ies2radOptions
from honeybee_radiance.config import folders


class Luminaire(object):
    """A luminaire defined by an IES photometric file.

    The Luminaire object stores the photometric data of a light fixture and
    provides methods to:

    - Parse IES LM-63 photometric data
    - Generate Radiance geometry via ies2rad
    - Generate pure-Python photometric web geometry
    - Place and orient luminaires in space via a LuminaireZone

    Args:
        ies_path: Path to an IES LM-63 photometric file. The file will be read and
            stored internally as text to ensure the Luminaire can be serialized
            and recreated even if the original file is no longer available.
        identifier: Optional text string for a unique Luminaire ID. This identifier
            is used to name Radiance output files and geometry. If None, the
            identifier will be derived from the IES file name.
        luminaire_zone: Optional LuminaireZone object defining the spatial placement,
            orientation, and repetition of the luminaire in the scene. This is
            required to generate positioned Radiance geometry (xform output).
        light_loss_factor: A scalar multiplier applied to account for lamp lumen
            depreciation, dirt depreciation, or other system losses. Must be
            greater than 0. Default: 1.
        candela_multiplier: Additional scalar multiplier applied to candela values
            after parsing the IES file. Must be greater than 0. Default: 1.

    Properties:
        * ies_path
        * ies_content
        * identifier
        * luminaire_zone
        * light_loss_factor
        * candela_multiplier
        * vertical_angles
        * horizontal_angles
        * candela_values
        * unit_type
        * width
        * length
        * height
        * max_candela
        * unit_scale
    """
    __slots__ = ('_ies_path', '_ies_content', '_identifier', '_luminaire_zone',
                 '_light_loss_factor', '_candela_multiplier', '_vertical_angles',
                 '_horizontal_angles', '_candela_values', '_unit_type', '_width',
                 '_length', '_height', '_max_candela', '_unit_scale')
    def __init__(self, ies_path, identifier=None, luminaire_zone=None, light_loss_factor=1,
                 candela_multiplier=1):
        self.ies_path = ies_path
        self.identifier = identifier
        self.luminaire_zone = luminaire_zone
        self.light_loss_factor = light_loss_factor
        self.candela_multiplier = candela_multiplier
        self._unit_type = None
        self._unit_scale = None
        self._vertical_angles = None
        self._horizontal_angles = None
        self._candela_values = None
        self._width = None
        self._length = None
        self._height = None
        self._max_candela = None

    @classmethod
    def from_dict(cls, data):
        """Create a Luminaire from a dictionary.

        Args:
            data: A python dictionary of a Luminaire.
        """
        assert data['type'] == 'Luminaire', \
            'Expected Luminaire dictionary. Got {}'.format(data['type'])

        new_obj = cls(
            data['ies_path'],
            identifier=data.get('identifier', None),
            light_loss_factor=data.get('light_loss_factor', 1),
            candela_multiplier=data.get('candela_multiplier', 1)
        )

        new_obj.ies_content = data['ies_content']

        if data.get('luminaire_zone') is not None:
            new_obj.luminaire_zone = LuminaireZone.from_dict(
                data['luminaire_zone']
            )

        return new_obj

    @property
    def ies_path(self):
        """Get or set the IES file of the luminaire."""
        return self._ies_path

    @ies_path.setter
    def ies_path(self, file_path):
        if not os.path.isfile(file_path):
            raise IOError('File not found: {}'.format(file_path))
        self._ies_path = file_path

        with io.open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            self._ies_content = f.read()

    @property
    def ies_content(self):
        """Get or set the IES content of the luminaire."""
        return self._ies_content

    @ies_content.setter
    def ies_content(self, content):
        self._ies_content = content

    @property
    def identifier(self):
        """Get or set the identifier of the luminaire."""
        return self._identifier

    @identifier.setter
    def identifier(self, value):
        if value is None:
            value = os.path.splitext(os.path.basename(self.ies_path))[0]
        self._identifier = value

    @property
    def luminaire_zone(self):
        """Get or set the IES file of the luminaire."""
        return self._luminaire_zone

    @luminaire_zone.setter
    def luminaire_zone(self, zone):
        self._luminaire_zone = zone

    @property
    def light_loss_factor(self):
        """Get or set the light loss factor (default = 1)."""
        return self._light_loss_factor

    @light_loss_factor.setter
    def light_loss_factor(self, value):
        if value is None:
            value = 1
        value = float(value)
        if value <= 0:
            raise ValueError('light_loss_factor must be greater than 0.')
        self._light_loss_factor = value

    @property
    def candela_multiplier(self):
        """Get or set the candela multiplier (default = 1)."""
        return self._candela_multiplier


    @candela_multiplier.setter
    def candela_multiplier(self, value):
        if value is None:
            value = 1
        value = float(value)
        if value <= 0:
            raise ValueError('candela_multiplier must be greater than 0.')
        self._candela_multiplier = value

    @property
    def unit_type(self):
        """IES unit type: 1=feet, 2=meters"""
        return self._unit_type

    @property
    def unit_scale(self):
        """Scale factor to convert IES units to meters"""
        return self._unit_scale

    @property
    def candela_values(self):
        """Raw candela values from IES"""
        return self._candela_values

    @property
    def normalized_candela_values(self):
        """Candela values normalized by max candela"""
        if self._max_candela == 0:
            return self._candela_values

        return [
            [v / self._max_candela for v in row]
            for row in self._candela_values
        ]

    @property
    def vertical_angles(self):
        """Get the list of vertical angles defined in the IES file."""
        return self._vertical_angles

    @property
    def horizontal_angles(self):
        """Get the list of horizontal angles defined in the IES file."""
        return self._horizontal_angles

    @property
    def max_candela(self):
        """Get the maximum candela value in the photometric distribution."""
        return self._max_candela

    @property
    def width_m(self):
        """Get the luminaire width in meters."""
        return self._width * self._unit_scale

    @property
    def length_m(self):
        """Get the luminaire length in meters."""
        return self._length * self._unit_scale

    @property
    def height_m(self):
        """Get the luminaire height in meters."""
        return self._height * self._unit_scale

    def _ensure_parsed(self):
        if self._vertical_angles is None:
            self.parse_photometric_data()

    def _ensure_ies_file(self, folder=None):
        """Ensure an IES file exists on disk and return its path.
        Writes the file if the original path no longer exists."""
        if self._ies_path and os.path.isfile(self._ies_path):
            return self._ies_path

        if self._ies_content is None:
            raise RuntimeError('IES content is missing.')

        folder = folder or os.getcwd()
        if not os.path.isdir(folder):
            os.makedirs(folder)

        path = os.path.join(folder, '{}.ies'.format(self.identifier))

        with io.open(path, 'w', encoding='utf-8') as f:
            f.write(self._ies_content)

        self._ies_path = path
        return path

    def ies2rad(self, libdir=None, prefdir=None, outname=None):
        """Executes ies2rad.
        
        Args:
            libdir: Set the library directory.
            prefdir: Set the library subdirectory.
            outname: Output file name root.

        Returns:
            Radiance scene description (rad file).
        """
        ies_path = self._ensure_ies_file(folder=prefdir)

        command = Ies2rad(ies=ies_path)
        options = Ies2radOptions()

        outname = outname or self.identifier
        options.o = outname

        multiplier = self.light_loss_factor * self.candela_multiplier
        if multiplier != 1:
            options.m = multiplier

        path_parts = []

        if libdir:
            options.l = libdir
            if not os.path.isabs(libdir) and not libdir.startswith('.'):
                libdir = os.path.join('.', libdir)
            path_parts.append(libdir)

        if prefdir:
            if not os.path.isabs(prefdir) and not prefdir.startswith('.'):
                prefdir = os.path.join('.', prefdir)
            options.p = prefdir
            path_parts.append(prefdir)

        path_parts.append('{}.rad'.format(outname))

        output_path = os.path.join(*path_parts).replace('\\', '/')

        command.options = options

        env = None
        if folders.env != {}:
            env = folders.env
        env = dict(os.environ, **env) if env else None

        command.run(env=env)

        return output_path

    def generate_scene(self, libdir=None, prefdir=None):
        """Create a combined scene description of LuminaireZone and Luminaire.

        This method will create a scene description where there scene from ies2rad
        is added in the correct location via xform.
        
        Args:
            libdir: Set the library directory.
            prefdir: Set the library subdirectory.

        Return:
            Combined Radiance scene description of LuminaireZone and Luminaire.
        """
        assert self.luminaire_zone is not None, 'Luminaire zone is required to generate scene.'

        output_path = self.ies2rad(
            libdir=libdir,
            prefdir=prefdir,
            outname='__{}__'.format(self.identifier)
        )

        path_parts = []
        if libdir:
            path_parts.append(libdir)
        if prefdir:
            path_parts.append(prefdir)

        path_parts.append('{}.rad'.format(self.identifier))
        scene_path = os.path.join(*path_parts).replace('\\', '/')

        with open(scene_path, 'w') as f:
            for luminaire_instance in self.luminaire_zone.instances:
                point = luminaire_instance.point
                spin = luminaire_instance.spin
                tilt = luminaire_instance.tilt
                rotation = luminaire_instance.rotation
                f.write(
                    '!xform -rz {} -ry {} -rz {} -t {} {} {} {}\n'.format(
                        spin, tilt, rotation, point[0], point[1], point[2], output_path
                    )
                )

        return scene_path

    def write_ies(self, folder, filename=None):
        """Write the stored IES content back to disk."""
        filename = filename or '{}.ies'.format(self.identifier)
        path = os.path.join(folder, filename)

        with open(path, 'w', encoding='utf-8') as f:
            f.write(self._ies_content)

        return path

    def parse_photometric_data(self):
        """Parse IES LM-63 photometric data from stored IES content.

        Populates:
            - vertical_angles
            - horizontal_angles
            - candela_values
            - unit_type
            - width, length, height
            - max_candela
        """
        if not self._ies_content:
            raise RuntimeError('No IES content to parse.')

        lines = self._ies_content.splitlines()

        data_started = False
        tokens = []

        for line in lines:
            line = line.strip()
            if not line:
                continue
            if line.upper().startswith('IESNA'):
                continue
            if line.startswith('['):
                continue
            if not data_started:
                parts = line.split()
                try:
                    float(parts[0])
                    data_started = True
                except Exception:
                    continue

            if data_started:
                tokens.extend(line.split())

        if not tokens:
            raise RuntimeError('Failed to parse numeric IES data.')

        idx = 0

        candela_multiplier = float(tokens[idx])
        idx += 1

        num_vert = int(tokens[idx])
        idx += 1
        num_horz = int(tokens[idx])
        idx += 1

        photometric_type = int(tokens[idx])
        idx += 1
        unit_type = int(tokens[idx])
        idx += 1

        width = float(tokens[idx])
        idx += 1
        length = float(tokens[idx])
        idx += 1
        height = float(tokens[idx])
        idx += 1

        idx += 3

        if photometric_type != 1:
            raise ValueError(
                'Only Type C photometry is supported (got {}).'
                .format(photometric_type)
            )

        vertical_angles = [
            float(tokens[idx + i]) for i in range(num_vert)
        ]
        idx += num_vert

        horizontal_angles = [
            float(tokens[idx + i]) for i in range(num_horz)
        ]
        idx += num_horz

        candela_values = []

        for h in range(num_horz):
            row = []
            for v in range(num_vert):
                row.append(float(tokens[idx]))
                idx += 1
            candela_values.append(row)

        if candela_multiplier != 1:
            for h in range(len(candela_values)):
                candela_values[h] = [
                    v * candela_multiplier for v in candela_values[h]
                ]

        max_candela = max(max(row) for row in candela_values if row)

        self._vertical_angles = vertical_angles
        self._horizontal_angles = horizontal_angles
        self._candela_values = candela_values

        self._width = width
        self._length = length
        self._height = height
        self._max_candela = max_candela

        if unit_type == 1:
            unit_scale = 0.3048
        elif unit_type == 2:
            unit_scale = 1.0
        else:
            raise ValueError(
                'Unsupported unit type in IES file: {}'.format(unit_type)
            )

        self._unit_type = unit_type
        self._unit_scale = unit_scale

    def _expand_horizontal_angles(self, horizontal_angles, candela_values):
        """Expand IES horizontal symmetry to full 0-360 coverage.

        Args:
            horizontal_angles: A list of horizontal angles.
            candela_value: A list of candela values.
        
        Returns:
            Tuple with (horizontal angles, candela values).
        """
        horz = list(horizontal_angles)
        candelas = [list(row) for row in candela_values]

        if len(horz) == 1:
            horz = list(range(0, 361, 10))
            candelas = candelas * len(horz)
            return horz, candelas

        counter = 0

        while horz[0] == 0 and horz[-1] < 360:
            counter += 1
            intervals = [
                horz[-1] - horz[-idx - 2]
                for idx in range(len(horz) - 1)
            ]
            new_angles = [
                horz[-1] + intervals[idx - 1]
                for idx in range(1, len(horz))
            ]

            horz.extend(new_angles)
            candelas.extend(list(reversed(candelas))[1:])

            if counter > 4:
                raise ValueError('Horizontal angles are not symmetric or ordered.')

        if horz[0] > 0:
            zerolimit = [
                horz[0] - (horz[idx] - horz[0])
                for idx in range(1, len(horz))
                if horz[0] - (horz[idx] - horz[0]) >= 0
            ][::-1]

            maxlimit = [
                horz[-1] + (horz[-1] - horz[-1 - idx])
                for idx in range(1, len(horz))
                if horz[-1] + (horz[-1] - horz[-1 - idx]) <= 360
            ]

            c0 = candelas[1:len(zerolimit) + 1][::-1]
            c1 = candelas[-len(maxlimit) - 1:-1][::-1]

            horz = zerolimit + horz + maxlimit
            candelas = c0 + candelas + c1

        return horz, candelas

    def generate_photometric_web(self, normalize=True):
        """Generate a photometric web geometry.

        Args:
            normalize: If set to True the geometry is normalized to unit dimensions.

        Returns:
            dict with keys:
                - points: list of Point3D objects.
                - horizontal_angles (rad)
                - vertical_angles (rad)
                - scale
        """
        self._ensure_parsed()

        horz_deg, candela = self._expand_horizontal_angles(
            self.horizontal_angles,
            self.candela_values
        )

        vert_deg = self.vertical_angles

        horz = [math.radians(h) for h in horz_deg]
        vert = [math.radians(v) for v in vert_deg]

        if normalize:
            max_cd = self.max_candela or 1.0
            candela = [
                [v / max_cd for v in row]
                for row in candela
            ]

        scale = max(abs(self.width_m), abs(self.length_m))

        points = []

        for h_idx, h_ang in enumerate(horz):
            row = []
            for v_idx, v_ang in enumerate(vert):
                cd = scale * candela[h_idx][v_idx]

                x = cd * math.sin(v_ang) * math.cos(h_ang)
                y = cd * math.sin(v_ang) * math.sin(h_ang)
                z = -cd * math.cos(v_ang)

                row.append(Point3D(x, y, z))
            points.append(row)

        return {
            'points': points,
            'horizontal_angles': horz,
            'vertical_angles': vert,
            'scale': scale
        }

    def to_dict(self):
        """Return Luminaire as a dictionary."""
        base = {
            'type': 'Luminaire',
            'ies_path': self.ies_path,
            'ies_content': self._ies_content,
            'identifier': self.identifier
        }

        if self.light_loss_factor != 1:
            base['light_loss_factor'] = self.light_loss_factor

        if self.candela_multiplier != 1:
            base['candela_multiplier'] = self.candela_multiplier

        if self.luminaire_zone is not None:
            base['luminaire_zone'] = self.luminaire_zone.to_dict()

        return base

    def ToString(self):
        """Overwrite ToString .NET method."""
        return self.__repr__()

    def __repr__(self):
        """Get the string representation of the the luminaire."""
        n_luminaires = len(self.luminaire_zone.points) if self.luminaire_zone else 0
        return 'Luminaire: {} [LuminaireZone: {}]'.format(self.identifier, n_luminaires)


class LuminaireZone(object):
    """A collection of luminaire instances defining a lighting layout.

    A LuminaireZone groups one or more LuminaireInstance objects together to
    describe how a Luminaire is distributed, positioned, and oriented within
    a scene.

    The LuminaireZone is attached to a Luminaire object and is required for
    generating positioned Radiance geometry (xform output).

    Typical use cases include:
        - Repeated luminaires in a grid
        - Multiple luminaires sharing the same photometric definition
        - Luminaires with varying orientation and aiming directions

    Args:
        instances:
            A list of LuminaireInstance objects.

    Properties:
        * instances
        * points
        * spins
        * tilts
        * rotations
    """
    __slots__ = ('_instances',)

    def __init__(self, instances):
        self.instances = instances

    @classmethod
    def from_dict(cls, data):
        """Create a LuminaireZone from a dictionary.

        Args:
            data: A python dictionary of a LuminaireZone.
        """
        instances = [LuminaireInstance.from_dict(d) for d in data['instances']]
        return cls(instances)

    @property
    def instances(self):
        """Get a list of LuminaireInstance objects."""
        return self._instances

    @instances.setter
    def instances(self, value):
        if not all(hasattr(v, 'point') for v in value):
            raise TypeError('All items must be LuminaireInstance objects.')
        self._instances = list(value)

    @property
    def points(self):
        """Return a list of points."""
        return [i.point for i in self.instances]

    @property
    def spins(self):
        """Return a list of spin values."""
        return [i.spin for i in self.instances]

    @property
    def tilts(self):
        """Return a list of tilt values."""
        return [i.tilt for i in self.instances]

    @property
    def rotations(self):
        """Return a list of rotation values."""
        return [i.rotation for i in self.instances]

    def __len__(self):
        return len(self._instances)

    def __iter__(self):
        return iter(self._instances)

    def to_dict(self):
        """Return LuminaireZone as a dictionary."""
        return {
            'type': 'LuminaireZone',
            'instances': [i.to_dict() for i in self.instances]
        }

    def ToString(self):
        """Overwrite ToString .NET method."""
        return self.__repr__()

    def __repr__(self):
        """Get the string representation of the luminaire zone."""
        return 'LuminaireZone [Instances: {}] '.format(len(self))


class LuminaireInstance(object):
    """A single positioned and oriented instance of a luminaire.

    A LuminaireInstance represents one physical placement of a luminaire in space.
    It defines the luminaire's location and orientation using IES LM-63
    C0-G0 conventions.

    Orientation is defined using three angular values (in degrees):

    A single Luminaire may have many LuminaireInstance objects, typically grouped
    together within a LuminaireZone.

    Args:
        point: Location of the luminaire instance. Can be a Ladybug Geometry Point3D
            or a list/tuple of three numeric values [x, y, z].
        spin: Rotation about the local vertical axis (degrees). Default: 0.
        tilt: Tilt angle away from the negative Z axis (degrees). Default: 0.
        rotation: Rotation in the horizontal plane about the C0 axis (degrees).
            Default: 0.

    Properties:
        * point
        * spin
        * tilt
        * rotation
    """
    __slots__ = ('_point', '_spin', '_tilt', '_rotation')
    def __init__(self, point, spin=0, tilt=0, rotation=0):
        self.point = point
        self.spin = spin
        self.tilt = tilt
        self.rotation = rotation

    @classmethod
    def from_dict(cls, data):
        """Create a LuminaireInstance from a dictionary.

        Args:
            data: A python dictionary of a LuminaireInstance.
        """
        point = Point3D.from_dict(data['point'])
        spin = data.get('spin', 0)
        tilt = data.get('tilt', 0)
        rotation = data.get('rotation', 0)

        return cls(point, spin=spin, tilt=tilt, rotation=rotation)

    @classmethod
    def from_aiming_point(cls, point, aiming_point, spin=0, tilt=0, rotation=0):
        """Create a LuminaireInstance aimed at a target point.

        Args:
            point: Luminaire location. Can be Point3D or list/tuple of three values.
            aiming_point: Target point the luminaire should aim at. Can be Point3D
                or list/tuple of three values.
            spin: User-defined spin offset (degrees).
            tilt: User-defined tilt offset (degrees).
            rotation: User-defined rotation offset (degrees).
        """
        if not isinstance(point, Point3D):
            point = Point3D(*point)
        if not isinstance(aiming_point, Point3D):
            aiming_point = Point3D(*aiming_point)

        pt_vec = aiming_point - point

        if pt_vec.magnitude == 0:
            return cls(point, spin=spin, tilt=tilt, rotation=rotation)

        pt_vec = pt_vec.normalize()

        C0_vec = Vector3D(1, 0, 0)
        G0_vec = Vector3D(0, 0, -1)

        angle_G0 = math.degrees(pt_vec.angle(G0_vec))
        angle_G0 = 360 - angle_G0

        proj = Vector3D(pt_vec.x, pt_vec.y, 0)

        if proj.magnitude == 0:
            angle_C0 = 0
        else:
            proj = proj.normalize()
            angle_C0 = math.degrees(C0_vec.angle(proj))

            if C0_vec.cross(proj).z < 0:
                angle_C0 = 360 - angle_C0

        tilt = angle_G0 + tilt
        rotation = angle_C0 + rotation

        return cls(point, spin=spin, tilt=tilt, rotation=rotation)

    @property
    def point(self):
        """Get the Point3D object of the LuminaireInstance."""
        return self._point

    @point.setter
    def point(self, value):
        if not isinstance(value, Point3D):
            value = Point3D(*value)
        self._point = value

    @property
    def spin(self):
        """Get the spin value of the LuminaireInstance."""
        return self._spin

    @spin.setter
    def spin(self, value):
        self._spin = float(value)

    @property
    def tilt(self):
        """Get the tilt value of the LuminaireInstance."""
        return self._tilt

    @tilt.setter
    def tilt(self, value):
        self._tilt = float(value)

    @property
    def rotation(self):
        """Get the rotation value of the LuminaireInstance."""
        return self._rotation

    @rotation.setter
    def rotation(self, value):
        self._rotation = float(value)

    def to_dict(self):
        """Return LuminaireInstance as a dictionary."""
        return {
            'point': self.point.to_dict(),
            'spin': self.spin,
            'tilt': self.tilt,
            'rotation': self.rotation
        }

    def ToString(self):
        """Overwrite ToString .NET method."""
        return self.__repr__()

    def __repr__(self):
        """Get the string representation of the luminaire instance."""
        return 'LuminaireInstance [Point: {}, Spin: {}, Tilt: {}, Rotation: {}] '.format(
            self.point, round(self.spin, 2), round(self.tilt, 2), round(self.rotation, 2))
