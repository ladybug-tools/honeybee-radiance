"""Module for simulating electric lighting."""
import os
import io
import math

from honeybee.typing import clean_rad_string
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
        * display_name
        * full_identifier
        * luminaire_zone
        * custom_lamp
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
    __slots__ = ('_ies_path', '_ies_content', '_identifier', '_display_name',
                 '_luminaire_zone', '_custom_lamp', '_light_loss_factor',
                 '_candela_multiplier', '_vertical_angles', '_horizontal_angles',
                 '_candela_values', '_unit_type', '_width', '_length', '_height',
                 '_max_candela', '_unit_scale')
    def __init__(self, ies_path, identifier=None, luminaire_zone=None, custom_lamp=None,
                 light_loss_factor=1, candela_multiplier=1):
        self.ies_path = ies_path
        self.identifier = identifier
        self._display_name = None
        self.luminaire_zone = luminaire_zone
        self.custom_lamp = custom_lamp
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

        if data['ies_path'] is None:
            ies_path = data['ies_content']
        else:
            ies_path = data['ies_path']

        new_obj = cls(
            ies_path,
            identifier=data.get('identifier', None),
            light_loss_factor=data.get('light_loss_factor', 1),
            candela_multiplier=data.get('candela_multiplier', 1)
        )

        new_obj.ies_content = data['ies_content']

        if data.get('luminaire_zone') is not None:
            new_obj.luminaire_zone = LuminaireZone.from_dict(
                data['luminaire_zone']
            )
        if data.get('custom_lamp') is not None:
            new_obj.custom_lamp = CustomLamp.from_dict(
                data['custom_lamp']
            )

        return new_obj

    @property
    def ies_path(self):
        """Get or set the IES file of the luminaire."""
        return self._ies_path

    @ies_path.setter
    def ies_path(self, ies_input):
        if ies_input is None:
            raise ValueError('ies_path cannot be None or empty.')

        # file path
        if isinstance(ies_input, str) and os.path.isfile(ies_input):
            self._ies_path = ies_input
            with io.open(ies_input, 'r', encoding='utf-8', errors='ignore') as f:
                self._ies_content = f.read()
            return

        # IES content as a string
        if isinstance(ies_input, str):
            text = ies_input.lstrip()
            if text.upper().startswith('IESNA'):
                self._ies_path = ies_input
                self._ies_content = ies_input
                return

        raise IOError(
            'ies_path must be a valid file path or IES file content as a string.'
        )

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
            if self._ies_path and os.path.isfile(self._ies_path):
                value = os.path.splitext(
                    os.path.basename(self._ies_path)
                )[0]
            else:
                value = self._identifier_from_ies_content()

            if not value:
                value = 'luminaire'
        value = clean_rad_string(value)

        self._identifier = value

    @property
    def display_name(self):
        """Get or set the display name of the luminaire."""
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
    def full_identifier(self):
        """Get full identifier of the luminaire.

        This is identical to identifier, but full_identifier makes certain
        honeybee-radiance functions reusable for this object.
        """
        return self.identifier

    @property
    def luminaire_zone(self):
        """Get or set the LuminaireZone of the luminaire."""
        return self._luminaire_zone

    @luminaire_zone.setter
    def luminaire_zone(self, zone):
        if zone is not None:
            assert isinstance(zone, LuminaireZone), \
                'Expected LuminaireZone object or None. Got {}'.format(type(zone))
        self._luminaire_zone = zone

    @property
    def custom_lamp(self):
        """Get or set the custom lamp of the luminaire."""
        return self._custom_lamp

    @custom_lamp.setter
    def custom_lamp(self, lamp):
        if lamp is not None:
            assert isinstance(lamp, CustomLamp), \
                'Expected CustomLamp object or None. Got {}'.format(type(lamp))
        self._custom_lamp = lamp

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
        self._ensure_parsed()
        return self._candela_values

    @property
    def normalized_candela_values(self):
        """Candela values normalized by max candela"""
        self._ensure_parsed()
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
    def width(self):
        """Get the luminaire width."""
        return self._width

    @property
    def length(self):
        """Get the luminaire length."""
        return self._length

    @property
    def height(self):
        """Get the luminaire height."""
        return self._height

    @property
    def max_candela(self):
        """Get the maximum candela value in the photometric distribution."""
        return self._max_candela

    @property
    def width_m(self):
        """Get the luminaire width in meters."""
        self._ensure_parsed()
        return self.width * self.unit_scale

    @property
    def length_m(self):
        """Get the luminaire length in meters."""
        self._ensure_parsed()
        return self.length * self.unit_scale

    @property
    def height_m(self):
        """Get the luminaire height in meters."""
        self._ensure_parsed()
        return self.height * self.unit_scale

    def ies2rad(self, libdir=None, prefdir=None, outname=None, units=None):
        """Executes ies2rad.

        The cwd is set to libdir to ensure that any relative paths are correctly
        resolved.
        
        Args:
            libdir: Set the library directory.
            prefdir: Set the library subdirectory.
            outname: Output file name root.
            units: Units for the output. Choose from:
                * 'm', 'meter', 'meters'
                * 'mm', 'millimeter', 'millimeters'
                * 'cm', 'centimeter', 'centimeters'
                * 'ft', 'foot', 'feet'
                * 'in', 'inch', 'inches'
                If None, meters are used (default in ies2rad).

        Returns:
            Radiance scene description (rad file).
        """
        ies_folder = os.path.join(libdir or '.', prefdir or '').replace('\\', '/')
        ies_path = self._ensure_ies_file(folder=ies_folder)
        command = Ies2rad(ies=ies_path)
        options = Ies2radOptions()

        outname = outname or self.identifier
        options.o = outname

        if units is None:
            units = 'm'
        units = str(units).strip().lower()
        unit_map = {
            'm': 'm',
            'meter': 'm',
            'meters': 'm',
            'mm': 'm/1000',
            'millimeter': 'm/1000',
            'millimeters': 'm/1000',
            'cm': 'm/100',
            'centimeter': 'm/100',
            'centimeters': 'm/100',
            'ft': 'f',
            'foot': 'f',
            'feet': 'f',
            'in': 'i',
            'inch': 'i',
            'inches': 'i'
        }
        if units not in unit_map:
            raise ValueError(
                "Invalid units '{}'. Valid options are: {}"
                .format(units, ', '.join(sorted(unit_map.keys())))
            )

        options.d = unit_map[units]

        multiplier = self.light_loss_factor * self.candela_multiplier

        if self.custom_lamp is not None:
            multiplier *= self.custom_lamp.depreciation_factor

            if self.custom_lamp.is_white:
                tab_dir = prefdir or '.'
                if not os.path.exists(tab_dir):
                    os.makedirs(tab_dir)
                tab_name = os.path.join(tab_dir, '{}.tab'.format(outname)).replace('\\', '/')
                if not os.path.isabs(tab_name) and not tab_name.startswith('.'):
                    tab_name = os.path.join('.', tab_name)
                x, y = self.custom_lamp.white_xy
                with open(tab_name, 'w') as f:
                    f.write('/{}/ {} {} {}\n'.format(self.custom_lamp.name,
                            x, y, self.custom_lamp.depreciation_factor))

                options.t = self.custom_lamp.name
                options.f = tab_name
            elif self.custom_lamp.is_rgb:
                options.t = 'default'
                options.c = self.custom_lamp.rgb
            else:
                raise ValueError('CustomLamp must be either white or RGB.')

        if multiplier != 1:
            options.m = multiplier

        if libdir:
            libdir = os.path.normpath(libdir).replace('\\', '/')
            if not os.path.isabs(libdir) and not libdir.startswith('.'):
                libdir = './' + libdir
            options.l = libdir

        if prefdir:
            prefdir = os.path.normpath(prefdir).replace('\\', '/')

            if libdir and prefdir.startswith('./'):
                prefdir = prefdir[2:]
            elif not libdir and not prefdir.startswith('.'):
                prefdir = './' + prefdir

            if not prefdir.startswith('.'):
                prefdir = './' + prefdir

            options.p = prefdir

        rad_path = os.path.join(prefdir or '.', '{}.rad'.format(outname)).replace('\\', '/')
        if not os.path.isabs(rad_path) and not rad_path.startswith('.'):
            rad_path = './' + rad_path

        command.options = options

        env = dict(os.environ, **folders.env) if folders.env else None
        command.run(env=env, cwd=libdir)

        return rad_path

    def generate_scene(self, libdir=None, prefdir=None, units=None):
        """Create a combined scene description of LuminaireZone and Luminaire.

        This method will create a scene description where there scene from ies2rad
        is added in the correct location via xform.
        
        Args:
            libdir: Set the library directory.
            prefdir: Set the library subdirectory.
            units: Units for the output. Choose from:
                * 'm', 'meter', 'meters'
                * 'mm', 'millimeter', 'millimeters'
                * 'cm', 'centimeter', 'centimeters'
                * 'ft', 'foot', 'feet'
                * 'in', 'inch', 'inches'
                If None, meters are used (default in ies2rad).

        Return:
            Combined Radiance scene description of LuminaireZone and Luminaire.
        """
        assert self.luminaire_zone is not None, 'Luminaire zone is required to generate scene.'
        luminaire_rad_path = self.ies2rad(
            libdir=libdir,
            prefdir=prefdir,
            outname='__{}__'.format(self.identifier),
            units=units
        )

        scene_dir = os.path.join(libdir or '.', prefdir or '').replace('\\', '/')
        scene_path = os.path.join(scene_dir, '{}.rad'.format(self.identifier)).replace('\\', '/')

        with open(scene_path, 'w') as f:
            for inst in self.luminaire_zone.instances:
                px, py, pz = inst.point
                spin, tilt, rotation = inst.spin, inst.tilt, inst.rotation
                f.write('!xform -rz {} -ry {} -rz {} -t {} {} {} {}\n'.format(
                    spin, tilt, rotation, px, py, pz, luminaire_rad_path
                ))

        return scene_path

    def write_ies(self, folder, filename=None):
        """Write the stored IES content back to disk."""
        filename = filename or '{}.ies'.format(self.identifier)
        path = os.path.join(folder, filename).replace('\\', '/')

        with io.open(path, 'w', encoding='utf-8') as f:
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
                line = [float(v) for v in line.split()]
                tokens.extend(line)

        if not tokens:
            raise RuntimeError('Failed to parse numeric IES data.')

        data = {}
        data['number_of_lamps'] = int(tokens[0])
        data['lumens_per_lamp'] = tokens[1]
        data['ies_candela_multiplier'] = tokens[2]
        data['num_vertical_angles'] = int(tokens[3])
        data['num_horizontal_angles'] = int(tokens[4])
        data['photometric_type'] = int(tokens[5])
        data['unit_type'] = int(tokens[6])
        data['width'] = tokens[7]
        data['length'] = tokens[8]
        data['height'] = tokens[9]
        data['ballast_factor'] = tokens[10]
        data['future_use'] = tokens[11]
        data['input_watts'] = tokens[12]

        if data['photometric_type'] != 1:
            raise ValueError(
                'Only Type C photometry is supported (got {}).'
                .format(data['photometric_type'])
            )

        idx = 13
        data['vertical_angles'] = tokens[idx:idx+data['num_vertical_angles']]
        idx += data['num_vertical_angles']
        data['horizontal_angles'] = tokens[idx:idx+data['num_horizontal_angles']]
        idx += data['num_horizontal_angles']

        candela_values = []
        for h in range(data['num_horizontal_angles']):
            row = tokens[idx:idx+data['num_vertical_angles']]
            idx += data['num_vertical_angles']
            candela_values.append(row)

        if data['ies_candela_multiplier'] != 1:
            candela_values = [
                [v * data['ies_candela_multiplier'] for v in row]
                for row in candela_values
            ]

        data['candela_values'] = candela_values

        data['max_candela'] = max(
            (max(row) for row in candela_values if row)
        )

        self._vertical_angles = data['vertical_angles']
        self._horizontal_angles = data['horizontal_angles']
        self._candela_values = data['candela_values']

        self._width = data['width']
        self._length = data['length']
        self._height = data['height']
        self._max_candela = data['max_candela']

        if data['unit_type'] == 1:
            data['unit_scale'] = 0.3048
        elif data['unit_type'] == 2:
            data['unit_scale'] = 1.0
        else:
            raise ValueError(
                'Unsupported unit type in IES file: {}'.format(data['unit_type'])
            )

        self._unit_type = data['unit_type']
        self._unit_scale = data['unit_scale']

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

    def _expand_horizontal_angles(self, horizontal_angles, candela_values):
        """Expand IES horizontal symmetry to full 0-360 coverage.

        Args:
            horizontal_angles: A list of horizontal angles.
            candela_values: A list of candela values.
        
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

    def _ensure_parsed(self):
        if self._vertical_angles is None:
            self.parse_photometric_data()

    def _ensure_ies_file(self, folder=None):
        """Ensure an IES file exists on disk and return its path.
        Writes the file if the original path no longer exists.
        
        Args:
            folder: Optional folder to write IES file to. The file is only written
                if the path stored in the ies_path property cannot be accessed.

        Returns:
            Path of IES file.
        """
        if self._ies_path and os.path.isfile(self._ies_path):
            return self._ies_path

        if self._ies_content is None:
            raise RuntimeError('IES content is missing.')

        folder = folder or os.getcwd()
        if not os.path.isdir(folder):
            os.makedirs(folder)

        path = self.write_ies(folder, filename='{}.ies'.format(self.identifier))

        return path

    def _identifier_from_ies_content(self):
        """Generate name of luminaire from IES content."""
        if not self._ies_content:
            return None

        for line in self._ies_content.splitlines():
            line = line.strip()
            if not line.startswith('['):
                continue

            if line.upper().startswith('[LUMINAIRE]'):
                if line.split(']', 1)[-1].strip():
                    return line.split(']', 1)[-1].strip()

            if line.upper().startswith('[LUMCAT]'):
                if line.split(']', 1)[-1].strip():
                    return line.split(']', 1)[-1].strip()

        return None

    def move(self, moving_vec):
        """Move this luminaire along a vector.

        Please note that this method only moves the positions of luminaire
        instances in the luminaire zone. It does not modify the photometric data
        itself.

        Args:
            moving_vec: A ladybug_geometry Vector3D with the direction and distance
                to move the sensor.
        """
        for instance in self.luminaire_zone.instances:
            instance.point = instance.point.move(moving_vec)

    def rotate(self, axis, angle, origin=None):
        """Rotate this luminaire by a certain angle around an axis and origin.

        Please note that this method only rotates the positions of luminaire
        instances in the luminaire zone. It does not modify the photometric data
        itself.

        Args:
            axis: Rotation axis as a Vector3D.
            angle: An angle for rotation in degrees.
            origin: A ladybug_geometry Point3D for the origin around which the
                object will be rotated. If None, it will be rotated around
                origin (0, 0, 0).
        """
        for instance in self.luminaire_zone.instances:
            instance.rotate(axis, angle, origin)

    def rotate_xy(self, angle, origin=None):
        """Rotate this luminaire counterclockwise in the world XY plane by an angle.

        Please note that this method only rotates the positions of luminaire
        instances in the luminaire zone. It does not modify the photometric data
        itself.

        Args:
            angle: An angle in degrees.
            origin: A ladybug_geometry Point3D for the origin around which the
                object will be rotated. If None, it will be rotated around
                origin (0, 0, 0).
        """
        for instance in self.luminaire_zone.instances:
            instance.rotate_xy(angle, origin)

    def reflect(self, plane):
        """Reflect this luminaire across a plane.

        Please note that this method only reflects the positions of luminaire
        instances in the luminaire zone. It does not modify the photometric data
        itself.

        Args:
            plane: A ladybug_geometry Plane across which the object will
                be reflected.
        """
        for instance in self.luminaire_zone.instances:
            instance.point = instance.point.reflect(plane.n, plane.o)

    def scale(self, factor, origin=None):
        """Scale this luminaire by a factor from an origin point.

        Please note that this method only scales the positions of luminaire
        instances in the luminaire zone. It does not modify the photometric data
        itself.

        Args:
            factor: A number representing how much the object should be scaled.
            origin: A ladybug_geometry Point3D representing the origin from which
                to scale. If None, it will be scaled from origin (0, 0, 0).
        """
        for instance in self.luminaire_zone.instances:
            instance.point = instance.point.scale(factor, origin=origin)

    def duplicate(self):
        """Duplicate the luminaire."""
        new_obj = Luminaire(
            self.ies_path, self.identifier, light_loss_factor=self.light_loss_factor,
            candela_multiplier=self.candela_multiplier)
        if self.luminaire_zone:
            new_obj.luminaire_zone = self.luminaire_zone.duplicate()
        if self.custom_lamp:
            new_obj.custom_lamp = self.custom_lamp.duplicate()

        return new_obj

    def to_dict(self):
        """Return Luminaire as a dictionary."""
        base = {
            'type': 'Luminaire',
            'ies_path': self.ies_path,
            'ies_content': self._ies_content,
            'identifier': self.identifier,
            'light_loss_factor': self.light_loss_factor,
            'candela_multiplier': self.candela_multiplier
        }

        if self.luminaire_zone is not None:
            base['luminaire_zone'] = self.luminaire_zone.to_dict()

        if self.custom_lamp is not None:
            base['custom_lamp'] = self.custom_lamp.to_dict()

        return base

    def __str__(self):
        return self.__repr__()

    def ToString(self):
        """Overwrite ToString .NET method."""
        return self.__repr__()

    def __repr__(self):
        """Get the string representation of the the luminaire."""
        n_luminaires = len(self.luminaire_zone.instances) if self.luminaire_zone else 0
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
        if not all(isinstance(v, LuminaireInstance) for v in value):
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

    def duplicate(self):
        """Duplicate the luminaire zone."""
        instances = [i.duplicate() for i in self.instances]
        new_obj = LuminaireZone(instances)
        return new_obj

    def to_dict(self):
        """Return LuminaireZone as a dictionary."""
        return {
            'type': 'LuminaireZone',
            'instances': [i.to_dict() for i in self.instances]
        }

    def __str__(self):
        return self.__repr__()

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
        tilt: Tilt angle around the Y axis (degrees). Default: 0.
        rotation: Rotation angle around the Z axis (degrees). Default: 0.

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

        c0_vec = Vector3D(1, 0, 0)
        g0_vec = Vector3D(0, 0, -1)

        angle_g0 = math.degrees(pt_vec.angle(g0_vec))
        angle_g0 = 360 - angle_g0

        proj = Vector3D(pt_vec.x, pt_vec.y, 0)

        if proj.magnitude == 0:
            angle_c0 = 0
        else:
            proj = proj.normalize()
            angle_c0 = math.degrees(c0_vec.angle(proj))

            if c0_vec.cross(proj).z < 0:
                angle_c0 = 360 - angle_c0

        tilt = angle_g0 + tilt
        rotation = angle_c0 + rotation

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

    @property
    def c0_axis(self):
        """Get the C0 axis as a world-space Vector3D.

        This is the luminaire "up" direction after applying:
        spin (Z) -> tilt (Y) -> rotation (Z)
        """
        v = Vector3D(1, 0, 0)  # default C0
        v = self._rotate_z(v, self.spin)
        v = self._rotate_y(v, self.tilt)
        v = self._rotate_z(v, self.rotation)
        return v.normalize()

    @property
    def g0_axis(self):
        """Get the G0 axis as a world-space Vector3D.

        This is the luminaire "forward" direction after applying:
        spin (Z) -> tilt (Y) -> rotation (Z)
        """
        v = Vector3D(0, 0, -1)  # default G0
        v = self._rotate_z(v, self.spin)
        v = self._rotate_y(v, self.tilt)
        v = self._rotate_z(v, self.rotation)
        return v.normalize()

    def rotate(self, axis, angle, origin=None):
        """Rotate this luminaire instance by a certain angle around an axis and origin.

        Args:
            axis: Rotation axis as a Vector3D.
            angle: An angle for rotation in degrees.
            origin: A ladybug_geometry Point3D for the origin around which the
                object will be rotated.
        """
        if origin is None:
            origin = Point3D(0, 0, 0)
        self.point = self.point.rotate(axis, math.radians(angle), origin)
        c0_axis = self.c0_axis.rotate(axis, math.radians(angle))
        g0_axis = self.g0_axis.rotate(axis, math.radians(angle))
        self.set_from_axes(c0_axis, g0_axis)

    def rotate_xy(self, angle, origin=None):
        """Rotate the luminaire around the world Z axis (XY plane).

        Args:
            angle: Rotation angle in degrees.
            origin: Optional Point3D to rotate around. Defaults to (0,0,0).
        """
        if origin is None:
            origin = Point3D(0, 0, 0)

        # Rotate position
        self.point = self.point.rotate(Vector3D(0, 0, 1), math.radians(angle), origin)

        # Rotate the axes
        c0_rotated = self._rotate_z(self.c0_axis, angle)
        g0_rotated = self._rotate_z(self.g0_axis, angle)

        # Update spin, tilt, rotation from new axes
        self.set_from_axes(c0_rotated, g0_rotated)

    @staticmethod
    def _rotate_z(v, angle_deg):
        a = math.radians(angle_deg)
        c = math.cos(a)
        s = math.sin(a)
        return Vector3D(
            v.x * c - v.y * s,
            v.x * s + v.y * c,
            v.z
        )

    @staticmethod
    def _rotate_y(v, angle_deg):
        a = math.radians(angle_deg)
        c = math.cos(a)
        s = math.sin(a)
        return Vector3D(
            v.x * c + v.z * s,
            v.y,
            -v.x * s + v.z * c
        )

    def set_from_axes(self, c0_axis, g0_axis):
        """Set spin, tilt, rotation from C0 and G0 axes.
        
        Args:
            c0_axis: A Vector3D representing the C0 axis.
            g0_axis: A Vector3D representing the G0 axis.
        """
        c0 = c0_axis.normalize()
        g0 = g0_axis.normalize()

        # Extract final rotation (about world Z)
        g0_xy = Vector3D(g0.x, g0.y, 0)

        if g0_xy.magnitude == 0:
            rotation = 0.0
        else:
            g0_xy = g0_xy.normalize()
            rotation = math.degrees(math.atan2(g0_xy.y, g0_xy.x))

        # Undo rotation
        c1 = self._rotate_z(c0, -rotation)
        g1 = self._rotate_z(g0, -rotation)

        # Extract signed tilt
        tilt = math.degrees(math.atan2(-g1.x, -g1.z))

        # Undo tilt
        c2 = self._rotate_y(c1, -tilt)

        # Extract spin
        spin = math.degrees(math.atan2(c2.y, c2.x))

        # Set spin, tilt, rotation
        self.spin = spin % 360
        self.tilt = tilt % 360
        self.rotation = rotation % 360

    def duplicate(self):
        """Duplicate the luminaire instance."""
        new_obj = LuminaireInstance(
            point=self.point.duplicate(), spin=self.spin, tilt=self.tilt,
            rotation=self.rotation)
        return new_obj

    def to_dict(self):
        """Return LuminaireInstance as a dictionary."""
        return {
            'point': self.point.to_dict(),
            'spin': self.spin,
            'tilt': self.tilt,
            'rotation': self.rotation
        }

    def __str__(self):
        return self.__repr__()

    def ToString(self):
        """Overwrite ToString .NET method."""
        return self.__repr__()

    def __repr__(self):
        """Get the string representation of the luminaire instance."""
        return 'LuminaireInstance [Point: {}, Spin: {}, Tilt: {}, Rotation: {}] '.format(
            self.point, round(self.spin, 2), round(self.tilt, 2), round(self.rotation, 2))


class CustomLamp(object):
    """Custom lamp definition for a luminaire.

    A CustomLamp overrides or modifies the luminous output of an IES-defined
    luminaire without changing its photometric distribution.

    Args:
        name: Text identifier for the lamp.
        depreciation_factor: Lumen depreciation factor (0-1).
        rgb: Optional RGB tuple (r, g, b), values 0-1.
        white_xy: Optional CIE xy tuple (x, y).
        color_temperature: Optional color temperature in Kelvin.
    """

    __slots__ = (
        '_name',
        '_depreciation_factor',
        '_candela_multiplier',
        '_rgb',
        '_white_xy',
        '_color_temperature',
        '_metadata'
    )

    def __init__(
        self,
        name,
        depreciation_factor=1.0,
        candela_multiplier=1.0,
        rgb=None,
        white_xy=None,
        color_temperature=None
    ):
        if rgb is not None and white_xy is not None:
            raise ValueError('CustomLamp cannot define both rgb and white_xy.')

        if rgb is None and white_xy is None:
            raise ValueError('CustomLamp must define either rgb or white_xy.')

        if not (0.0 <= depreciation_factor <= 1.0):
            raise ValueError('depreciation_factor must be between 0 and 1.')

        if rgb is not None:
            if len(rgb) != 3 or any(c < 0 or c > 1 for c in rgb):
                raise ValueError('RGB values must be between 0 and 1.')

        if white_xy is not None:
            if len(white_xy) != 2 or any(c < 0 or c > 1 for c in white_xy):
                raise ValueError('white_xy values must be between 0 and 1.')

        self._name = str(name)
        self._depreciation_factor = float(depreciation_factor)
        self._candela_multiplier = float(candela_multiplier)
        self._rgb = tuple(rgb) if rgb is not None else None
        self._white_xy = tuple(white_xy) if white_xy is not None else None
        self._color_temperature = color_temperature

    @classmethod
    def from_lamp_name(cls, lamp_name):
        """Create a CustomLamp from a lamp name from a list of predefined lamps.

        Args:
            lamp_name: Name matching a legacy Honeybee lamp type.
            depreciation_factor: Optional lumen depreciation factor.

        Returns:
            CustomLamp
        """
        key = lamp_name.lower().strip()

        if key not in LAMPNAMES:
            raise ValueError(
                'Unknown lamp name "{}". Valid options are:\n{}'.format(
                    lamp_name, ', '.join(sorted(LAMPNAMES.keys()))
                )
            )

        x, y, depreciation_factor = LAMPNAMES[key]

        return cls(
            name=lamp_name,
            white_xy=(x, y),
            depreciation_factor=depreciation_factor
        )

    @classmethod
    def from_color_temperature(cls, name, color_temperature, depreciation_factor=1.0):
        """Create a CustomLamp from a correlated color temperature (CCT).

        Args:
            name: Name of the lamp.
            color_temperature: CCT in Kelvin (1000-25000).
            depreciation_factor: Optional lumen depreciation factor.

        Returns:
            CustomLamp instance with white_xy computed from CCT.
        """
        # validate the CCT range
        if not (1000 <= color_temperature <= 25000):
            raise ValueError("The color temperature value should be between 1000 and 25000.")

        # convert CCT to xy using the legacy function
        wavelengths = {wavelength:wavelength*(10**-9) for wavelength in range(360,831)}
        x, y = calc_xy_1931_from_cct(color_temperature, wavelengths, CMFS)

        # compute color coordinates (u, v) for 1960 and 1976 standards
        cor = color_coordinates(x, y, 1931)
        uv1960 = cor[1960]
        uv1976 = cor[1976]

        # default Duv is 0
        duv = 0.0

        lamp_metadata = {
            'uv1960': uv1960,
            'uv1976': uv1976,
            'CCT': color_temperature,
            'Duv': duv
        }

        lamp = cls(
            name=name,
            white_xy=(x, y),
            color_temperature=color_temperature,
            depreciation_factor=depreciation_factor
        )

        lamp._metadata = lamp_metadata

        return lamp

    @classmethod
    def from_xy_coordinates(cls, name, x, y, depreciation_factor=1.0, color_space=0):
        """Create a CustomLamp from CIE xy coordinates.

        Args:
            name: Name of the lamp.
            x, y: CIE xy coordinates (0-1).
            depreciation_factor: Optional lumen depreciation factor.
            color_space: Optional color space (0=1931, 1=1960, 2=1976).

        Returns:
            CustomLamp instance with metadata.
        """
        if color_space not in (0, 1, 2):
            raise ValueError(
                "The value for color_space should be 0, 1, or 2. "
                "0=1931 CIE, 1=1960 CIE, 2=1976 CIE."
            )

        year = {0: 1931, 1: 1960, 2: 1976}[color_space]
        cor = color_coordinates(x, y, year)

        x1931, y1931 = cor[1931]
        u1960, v1960 = cor[1960]
        u1976, v1976 = cor[1976]

        cct, duv = calc_cct(x1931, y1931, 1931)
        if abs(duv) > 0.02:
            cct, duv = "NA", "NA"

        # prepare metadata
        lamp_metadata = {
            'uv1960': (u1960, v1960),
            'uv1976': (u1976, v1976),
            'CCT': cct,
            'Duv': duv,
            'color_space': year
        }

        # create the lamp
        lamp = cls(name=name, white_xy=(x1931, y1931), depreciation_factor=depreciation_factor)

        lamp._metadata = lamp_metadata

        return lamp

    @classmethod
    def from_rgb_colors(cls, name, rgb_color, depreciation_factor=1.0):
        """Create a CustomLamp from RGB colors.

        Args:
            name: Name of the lamp.
            rgb_color: Tuple/list with values (R, G, B, A) in 0-255.
            depreciation_factor: Optional lumen depreciation factor.

        Returns:
            CustomLamp instance with metadata.
        """
        # extract and normalize RGB values
        if len(rgb_color) == 3:  # set alpha to 1
            rgb_color.append(1)
        r, g, b, a = rgb_color[0], rgb_color[1], rgb_color[2], rgb_color[3]
        r, g, b, a = map(lambda c: round(float(c) / 255.0, 4), (r, g, b, a))

        # adjust depreciation factor with alpha
        effective_depr = depreciation_factor * a

        # prepare metadata
        lamp_metadata = {
            'rgb': (r, g, b),
            'alpha': a,
            'effective_depreciation': effective_depr,
            'lamp_type': 'RGB'
        }

        # Create the lamp
        lamp = cls(name=name, rgb=(r, g, b), depreciation_factor=effective_depr)
        lamp._metadata = lamp_metadata

        return lamp

    @classmethod
    def from_default_white(cls, name, depreciation_factor=1.0):
        """Create a default white CustomLamp with 3200 K CCT.

        Args:
            name: Name of the lamp.
            depreciation_factor: Optional lumen depreciation factor.

        Returns:
            CustomLamp instance with metadata.
        """
        # default CCT
        cct_default = 3200

        # convert to xy using helper
        wavelengths = {wavelength: wavelength * 1e-9 for wavelength in range(360, 831)}
        x, y = calc_xy_1931_from_cct(cct_default, wavelengths, CMFS)
        cor = color_coordinates(x, y, 1931)

        # extract coordinates for different color spaces
        x1931, y1931 = cor[1931]
        u1960, v1960 = cor[1960]
        u1976, v1976 = cor[1976]

        # Duv is 0.0 for default
        duv = 0.0

        # prepare metadata
        lamp_metadata = {
            'uv1960': (u1960, v1960),
            'uv1976': (u1976, v1976),
            'CCT': cct_default,
            'Duv': duv,
            'lamp_type': 'Default White'
        }

        # Create the lamp instance
        lamp = cls(name=name, white_xy=(x1931, y1931), depreciation_factor=depreciation_factor)
        lamp._metadata = lamp_metadata

        return lamp

    @classmethod
    def from_dict(cls, data):
        """Create a CustomLamp from a dictionary."""
        return cls(
            name=data['name'],
            depreciation_factor=data.get('depreciation_factor', 1.0),
            candela_multiplier=data.get('candela_multiplier', 1.0),
            rgb=data.get('rgb'),
            white_xy=data.get('white_xy')
        )

    @property
    def name(self):
        """Return lamp name."""
        return self._name

    @property
    def depreciation_factor(self):
        """Return depreciation factor."""
        return self._depreciation_factor

    @property
    def candela_multiplier(self):
        """Return candela multiplier."""
        return self._candela_multiplier

    @property
    def is_rgb(self):
        """Return boolean to note whether or not lamp is RGB."""
        return self._rgb is not None

    @property
    def is_white(self):
        """Return boolean to note whether or not lamp is White."""
        return self._white_xy is not None

    @property
    def rgb(self):
        """Return RGB values."""
        return self._rgb

    @property
    def white_xy(self):
        """Rwturn x, y chromaticities."""
        return self._white_xy

    @property
    def color_temperature(self):
        """Correlated color temperature in Kelvin, if defined."""
        return self._color_temperature

    @property
    def metadata(self):
        """Return lamp metadata."""
        return getattr(self, "_metadata", None)

    def duplicate(self):
        """Duplicate the custom lamp."""
        new_obj = CustomLamp(name=self.name, depreciation_factor=self.depreciation_factor,
                             candela_multiplier=self.candela_multiplier, rgb=self.rgb,
                             white_xy=self.white_xy, color_temperature=self.color_temperature)
        if hasattr(self, "_metadata"):
            new_obj._metadata = self._metadata.copy()
        return new_obj

    def to_dict(self):
        """Convert CustomLamp to dictionary."""
        return {
            'name': self._name,
            'depreciation_factor': self._depreciation_factor,
            'candela_multiplier': self._candela_multiplier,
            'rgb': self._rgb,
            'white_xy': self._white_xy
        }

    def __str__(self):
        return self.__repr__()

    def ToString(self):
        """Overwrite ToString .NET method."""
        return self.__repr__()

    def __repr__(self):
        mode = 'RGB' if self.is_rgb else 'White'
        return (
            'CustomLamp: {} [Type: {}]'
        ).format(self._name, mode)


def color_coordinates(a, b, year):
    """Convert CIE color coordinates between 1931, 1960, and 1976 systems.

    This function takes a pair of chromaticity coordinates defined in one
    CIE color space and returns the equivalent coordinates in all three
    standard CIE systems.

    Args:
        a: First chromaticity coordinate (x or u or u').
        b: Second chromaticity coordinate (y or v or v').
        year: CIE diagram year. Must be one of
            - 1931 (x, y)
            - 1960 (u, v)
            - 1976 (u', v')

    Returns:
        dict:
            Dictionary with keys {1931, 1960, 1976}, each mapped to a
            (a, b) tuple rounded to 8 decimal places.

            Example:
                {
                    1931: (x, y),
                    1960: (u, v),
                    1976: (u_prime, v_prime)
                }
    """
    if year not in (1931, 1960, 1976):
        raise ValueError('Year must be one of 1931, 1960, or 1976.')

    coords = {}

    if year == 1931:
        x, y = float(a), float(b)

        u = (4 * x) / (-2 * x + 12 * y + 3)
        v = (6 * y) / (-2 * x + 12 * y + 3)

        coords[1931] = (x, y)
        coords[1960] = (u, v)
        coords[1976] = (u, v * 1.5)

    elif year == 1960:
        u, v = float(a), float(b)

        v_prime = v * 1.5

        x = 9 * u / (6 * u - 16 * v_prime + 12)
        y = 4 * v_prime / (6 * u - 16 * v_prime + 12)

        coords[1960] = (u, v)
        coords[1976] = (u, v_prime)
        coords[1931] = (x, y)

    elif year == 1976:
        u_prime, v_prime = float(a), float(b)

        v = v_prime / 1.5

        x = 9 * u_prime / (6 * u_prime - 16 * v_prime + 12)
        y = 4 * v_prime / (6 * u_prime - 16 * v_prime + 12)

        coords[1976] = (u_prime, v_prime)
        coords[1960] = (u_prime, v)
        coords[1931] = (x, y)

    for key, value in coords.items():
        coords[key] = (round(value[0], 8), round(value[1], 8))

    return coords


def calc_xy_1931_from_cct(cct, wavelengths, cmfs):
    """Calculate CIE 1931 x,y chromaticity from correlated color temperature.

    This function computes the chromaticity coordinates of a blackbody
    radiator at the given color temperature using Planck's law and the
    CIE 1931 color matching functions.

    The implementation matches the legacy Honeybee Custom Lamp behavior,
    including normalization at 560 nm.

    Args:
        cct: Correlated color temperature in Kelvin. Valid range is
            approximately 1000-25000 K.
        wavelengths: Mapping of wavelength (nm) > wavelength in meters.
            Expected keys: integers from 360 to 830.
        cmfs: Mapping of wavelength (nm) > (x, y, <) CIE 1931 values.

    Returns:
        tuple:
            (x, y) CIE 1931 chromaticity coordinates, rounded to 8 decimals.

    Raises:
        ValueError: If CCT is outside a reasonable range or data is missing.
    """
    if cct <= 0:
        raise ValueError('Color temperature must be greater than zero.')

    # physical constants (Planck's law)
    c1 = 3.741771e-16
    c2 = 1.4387769e-2

    # normalize spectral power distribution at 560 nm
    wl_560 = wavelengths.get(560)
    if wl_560 is None:
        raise ValueError('Wavelengths must include 560 nm.')

    exp = math.exp

    spd_560 = (
        c1 * (wl_560 ** -5) /
        (exp(c2 / (cct * wl_560)) - 1)
    )

    if spd_560 == 0:
        raise ValueError('Invalid spectral power normalization.')

    # compute normalized spectral power distribution
    spectral_power = {}

    for wl in range(360, 831):
        wl_m = wavelengths.get(wl)
        if wl_m is None:
            raise ValueError('Missing wavelength data at {} nm'.format(wl))

        spectral_power[wl] = (
            c1 * (wl_m ** -5) /
            (exp(c2 / (cct * wl_m)) - 1)
        ) / spd_560

    # tristimulus integration
    tri_x = tri_y = tri_z = 0.0

    for wl in range(360, 831):
        xbar, ybar, zbar = cmfs[wl]
        spd = spectral_power[wl]

        tri_x += 683 * xbar * spd
        tri_y += 683 * ybar * spd
        tri_z += 683 * zbar * spd

    denom = tri_x + tri_y + tri_z
    if denom == 0:
        raise ValueError('Invalid tristimulus calculation.')

    x = tri_x / denom
    y = tri_y / denom

    return round(x, 8), round(y, 8)


def planckian_table(u_src, v_src, min_temp=1000, max_temp=100000, growth=1.01):
    """Build a table of Planckian temperatures along with (u, v) coordinates and distances.

    Args:
        u_src, v_src: Reference u,v coordinates (CIE 1960) to compare against.
        min_temp: Starting temperature (K). Default 1000 K.
        max_temp: Maximum temperature (K). Default 100,000 K.
        growth: Multiplicative growth factor per step. Default 1.01 (~1% step).

    Returns:
        List of tuples: (temperature, u, v, distance_to_ref, counter)
    """
    table = []
    temp = min_temp
    counter = 1

    wavelengths = {wavelength:wavelength*(10**-9) for wavelength in range(360,831)}
    while temp < max_temp:
        temp *= growth
        # compute 1931 xy from temp
        x, y = calc_xy_1931_from_cct(temp, wavelengths, CMFS)
        # convert to 1960 uv
        u, v = color_coordinates(x, y, 1931)[1960]
        # distance to reference point
        dist = math.sqrt((u_src - u) ** 2 + (v_src - v) ** 2)
        table.append((temp, u, v, dist, counter))
        counter += 1

    return table


def calc_cct(a, b, year):
    """Calculate Correlated Color Temperature (CCT) and Duv from CIE coordinates.

    Args:
        a, b: CIE coordinates (x,y or u,v or u',v') depending on `year`.
        year: Year of the coordinates (1931, 1960, 1976)

    Returns:
        Tuple: (CCT in K, Duv)
    """
    # convert input coordinates to CIE 1960 uv
    u, v = color_coordinates(a, b, year)[1960]
    
    # build Planckian table
    table = planckian_table(u, v)

    # distance extraction
    distances = [row[3] for row in table]
    min_dist = min(distances)
    min_idx = distances.index(min_dist)

    # triangular sign helper
    sign = lambda x: -1 if x < 0 else 1

    try:
        pt_minus1 = table[min_idx - 1]
        pt = table[min_idx]
        pt_plus1 = table[min_idx + 1]
    except IndexError:
        # edge case: CCT too high or too low
        return 10000, 0.1

    # extract distances and temperatures
    dm1, dm, dp1 = pt_minus1[3], pt[3], pt_plus1[3]
    tm1, tm, tp1 = pt_minus1[0], pt[0], pt_plus1[0]
    um1, vm1 = pt_minus1[1:3]
    up1, vp1 = pt_plus1[1:3]

    # distance along uv line
    l = math.sqrt((um1 - up1) ** 2 + (vm1 - vp1) ** 2)
    x = (dm1**2 - dp1**2 + l**2) / 2
    vtx = vm1 + (vp1 - vm1) * x / l
    sign_val = sign(v - vtx)

    # triangular interpolation
    tx_tri = tm1 + (tp1 - tm1) * (x / l)
    duv_tri = math.sqrt(dm1**2 - x**2) * sign_val

    # parabolic interpolation
    X = (tp1 - tm) * (tm1 - tp1) * (tm - tm1)
    a_coef = (tm1*(dp1 - dm) + tm*(dm1 - dp1) + tp1*(dm - dm1)) / X
    b_coef = -((tm1**2)*(dp1 - dm) + (tm**2)*(dm1 - dp1) + (tp1**2)*(dm - dm1)) / X
    c_coef = -(dm1*(tp1 - tm)*tm*tp1 + dm*(tm1 - tp1)*tm1*tp1 + dp1*(tm - tm1)*tm1*tm) / X

    tx = -b_coef / (2 * a_coef)
    tx_cor = tx * 0.99991
    duv = sign_val * (a_coef*tx_cor**2 + b_coef*tx_cor + c_coef)

    # return triangular if Duv very small
    if abs(duv) < 0.002:
        return tx_tri, duv_tri
    else:
        return tx, duv


LAMPNAMES = {
    'clear metal halide': (0.396, 0.39, 0.8),
    'cool white deluxe': (0.376, 0.368, 0.85),
    'deluxe cool white': (0.376, 0.368, 0.85),
    'deluxe warm white': (0.440, 0.403, 0.85),
    'fluorescent': (0.376, 0.368, 0.85),
    'incandescent': (0.453,0.405, 0.95),
    'mercury': (0.373, 0.415, 0.8),
    'metal halide': (0.396, 0.390, 0.8),
    'halogen': (0.4234, 0.399, 1),
    'quartz': (0.424, 0.399, 1),
    'sodium':(0.569, 0.421, 0.93),
    'warm white deluxe': (0.440, 0.403, 0.85),
    'xenon': (0.324, 0.324,1),
    'warm white': (0.440, 0.403, 0.85),
    'cool white': (0.376, 0.368, 0.85)
}


CMFS = {
    360: (0.000130, 0.000004, 0.000606), 361: (0.000146, 0.000004, 0.000681), 362: (0.000164, 0.000005, 0.000765),
    363: (0.000184, 0.000006, 0.000860), 364: (0.000207, 0.000006, 0.000967), 365: (0.000232, 0.000007, 0.001086),
    366: (0.000261, 0.000008, 0.001221), 367: (0.000293, 0.000009, 0.001373), 368: (0.000329, 0.000010, 0.001544),
    369: (0.000370, 0.000011, 0.001734), 370: (0.000415, 0.000012, 0.001946), 371: (0.000464, 0.000014, 0.002178),
    372: (0.000519, 0.000016, 0.002436), 373: (0.000582, 0.000017, 0.002732), 374: (0.000655, 0.000020, 0.003078),
    375: (0.000742, 0.000022, 0.003486), 376: (0.000845, 0.000025, 0.003975), 377: (0.000965, 0.000028, 0.004541),
    378: (0.001095, 0.000032, 0.005158), 379: (0.001231, 0.000035, 0.005803), 380: (0.001368, 0.000039, 0.006450),
    381: (0.001502, 0.000043, 0.007083), 382: (0.001642, 0.000047, 0.007745), 383: (0.001802, 0.000052, 0.008501),
    384: (0.001996, 0.000057, 0.009415), 385: (0.002236, 0.000064, 0.010550), 386: (0.002535, 0.000072, 0.011966),
    387: (0.002893, 0.000082, 0.013656), 388: (0.003301, 0.000094, 0.015588), 389: (0.003753, 0.000106, 0.017730),
    390: (0.004243, 0.000120, 0.020050), 391: (0.004762, 0.000135, 0.022511), 392: (0.005330, 0.000151, 0.025203),
    393: (0.005979, 0.000170, 0.028280), 394: (0.006741, 0.000192, 0.031897), 395: (0.007650, 0.000217, 0.036210),
    396: (0.008751, 0.000247, 0.041438), 397: (0.010029, 0.000281, 0.047504), 398: (0.011422, 0.000319, 0.054120),
    399: (0.012869, 0.000357, 0.060998), 400: (0.014310, 0.000396, 0.067850), 401: (0.015704, 0.000434, 0.074486),
    402: (0.017147, 0.000473, 0.081362), 403: (0.018781, 0.000518, 0.089154), 404: (0.020748, 0.000572, 0.098540),
    405: (0.023190, 0.000640, 0.110200), 406: (0.026207, 0.000725, 0.124613), 407: (0.029782, 0.000826, 0.141702),
    408: (0.033881, 0.000941, 0.161304), 409: (0.038468, 0.001070, 0.183257), 410: (0.043510, 0.001210, 0.207400),
    411: (0.048996, 0.001362, 0.233692), 412: (0.055023, 0.001531, 0.262611), 413: (0.061719, 0.001720, 0.294775),
    414: (0.069212, 0.001935, 0.330799), 415: (0.077630, 0.002180, 0.371300), 416: (0.086958, 0.002455, 0.416209),
    417: (0.097177, 0.002764, 0.465464), 418: (0.108406, 0.003118, 0.519695), 419: (0.120767, 0.003526, 0.579530),
    420: (0.134380, 0.004000, 0.645600), 421: (0.149358, 0.004546, 0.718484), 422: (0.165396, 0.005159, 0.796713),
    423: (0.181983, 0.005829, 0.877846), 424: (0.198611, 0.006546, 0.959439), 425: (0.214770, 0.007300, 1.039050),
    426: (0.230187, 0.008087, 1.115367), 427: (0.244880, 0.008909, 1.188497), 428: (0.258777, 0.009768, 1.258123),
    429: (0.271808, 0.010664, 1.323930), 430: (0.283900, 0.011600, 1.385600), 431: (0.294944, 0.012573, 1.442635),
    432: (0.304897, 0.013583, 1.494804), 433: (0.313787, 0.014630, 1.542190), 434: (0.321645, 0.015715, 1.584881),
    435: (0.328500, 0.016840, 1.622960), 436: (0.334351, 0.018007, 1.656405), 437: (0.339210, 0.019214, 1.685296),
    438: (0.343121, 0.020454, 1.709875), 439: (0.346130, 0.021718, 1.730382), 440: (0.348280, 0.023000, 1.747060),
    441: (0.349600, 0.024295, 1.760045), 442: (0.350147, 0.025610, 1.769623), 443: (0.350013, 0.026959, 1.776264),
    444: (0.349287, 0.028351, 1.780433), 445: (0.348060, 0.029800, 1.782600), 446: (0.346373, 0.031311, 1.782968),
    447: (0.344262, 0.032884, 1.781700), 448: (0.341809, 0.034521, 1.779198), 449: (0.339094, 0.036226, 1.775867),
    450: (0.336200, 0.038000, 1.772110), 451: (0.333198, 0.039847, 1.768259), 452: (0.330041, 0.041768, 1.764039),
    453: (0.326636, 0.043766, 1.758944), 454: (0.322887, 0.045843, 1.752466), 455: (0.318700, 0.048000, 1.744100),
    456: (0.314025, 0.050244, 1.733560), 457: (0.308884, 0.052573, 1.720858), 458: (0.303290, 0.054981, 1.705937),
    459: (0.297258, 0.057459, 1.688737), 460: (0.290800, 0.060000, 1.669200), 461: (0.283970, 0.062602, 1.647529),
    462: (0.276721, 0.065278, 1.623413), 463: (0.268918, 0.068042, 1.596022), 464: (0.260423, 0.070911, 1.564528),
    465: (0.251100, 0.073900, 1.528100), 466: (0.240848, 0.077016, 1.486111), 467: (0.229851, 0.080266, 1.439522),
    468: (0.218407, 0.083667, 1.389880), 469: (0.206812, 0.087233, 1.338736), 470: (0.195360, 0.090980, 1.287640),
    471: (0.184214, 0.094918, 1.237422), 472: (0.173327, 0.099046, 1.187824), 473: (0.162688, 0.103367, 1.138761),
    474: (0.152283, 0.107885, 1.090148), 475: (0.142100, 0.112600, 1.041900), 476: (0.132179, 0.117532, 0.994198),
    477: (0.122570, 0.122674, 0.947347), 478: (0.113275, 0.127993, 0.901453), 479: (0.104298, 0.133453, 0.856619),
    480: (0.095640, 0.139020, 0.812950), 481: (0.087300, 0.144676, 0.770517), 482: (0.079308, 0.150469, 0.729445),
    483: (0.071718, 0.156462, 0.689914), 484: (0.064581, 0.162718, 0.652105), 485: (0.057950, 0.169300, 0.616200),
    486: (0.051862, 0.176243, 0.582329), 487: (0.046282, 0.183558, 0.550416), 488: (0.041151, 0.191274, 0.520338),
    489: (0.036413, 0.199418, 0.491967), 490: (0.032010, 0.208020, 0.465180), 491: (0.027917, 0.217120, 0.439925),
    492: (0.024144, 0.226735, 0.416184), 493: (0.020687, 0.236857, 0.393882), 494: (0.017540, 0.247481, 0.372946),
    495: (0.014700, 0.258600, 0.353300), 496: (0.012162, 0.270185, 0.334858), 497: (0.009920, 0.282294, 0.317552),
    498: (0.007967, 0.295051, 0.301338), 499: (0.006296, 0.308578, 0.286169), 500: (0.004900, 0.323000, 0.272000),
    501: (0.003777, 0.338402, 0.258817), 502: (0.002945, 0.354686, 0.246484), 503: (0.002425, 0.371699, 0.234772),
    504: (0.002236, 0.389288, 0.223453), 505: (0.002400, 0.407300, 0.212300), 506: (0.002926, 0.425630, 0.201169),
    507: (0.003837, 0.444310, 0.190120), 508: (0.005175, 0.463394, 0.179225), 509: (0.006982, 0.482940, 0.168561),
    510: (0.009300, 0.503000, 0.158200), 511: (0.012149, 0.523569, 0.148138), 512: (0.015536, 0.544512, 0.138376),
    513: (0.019478, 0.565690, 0.128994), 514: (0.023993, 0.586965, 0.120075), 515: (0.029100, 0.608200, 0.111700),
    516: (0.034815, 0.629346, 0.103905), 517: (0.041120, 0.650307, 0.096667), 518: (0.047985, 0.670875, 0.089983),
    519: (0.055379, 0.690842, 0.083845), 520: (0.063270, 0.710000, 0.078250), 521: (0.071635, 0.728185, 0.073209),
    522: (0.080462, 0.745464, 0.068678), 523: (0.089740, 0.761969, 0.064568), 524: (0.099456, 0.777837, 0.060788),
    525: (0.109600, 0.793200, 0.057250), 526: (0.120167, 0.808110, 0.053904), 527: (0.131115, 0.822496, 0.050747),
    528: (0.142368, 0.836307, 0.047753), 529: (0.153854, 0.849492, 0.044899), 530: (0.165500, 0.862000, 0.042160),
    531: (0.177257, 0.873811, 0.039507), 532: (0.189140, 0.884962, 0.036936), 533: (0.201169, 0.895494, 0.034458),
    534: (0.213366, 0.905443, 0.032089), 535: (0.225750, 0.914850, 0.029840), 536: (0.238321, 0.923735, 0.027712),
    537: (0.251067, 0.932092, 0.025694), 538: (0.263992, 0.939923, 0.023787), 539: (0.277102, 0.947225, 0.021989),
    540: (0.290400, 0.954000, 0.020300), 541: (0.303891, 0.960256, 0.018718), 542: (0.317573, 0.966007, 0.017240),
    543: (0.331438, 0.971261, 0.015864), 544: (0.345483, 0.976023, 0.014585), 545: (0.359700, 0.980300, 0.013400),
    546: (0.374084, 0.984092, 0.012307), 547: (0.388640, 0.987481, 0.011302), 548: (0.403378, 0.990313, 0.010378),
    549: (0.418312, 0.992812, 0.009529), 550: (0.433450, 0.994950, 0.008750), 551: (0.448795, 0.996711, 0.008035),
    552: (0.464336, 0.998098, 0.007382), 553: (0.480064, 0.999112, 0.006785), 554: (0.495971, 0.999748, 0.006243),
    555: (0.512050, 1.000000, 0.005750), 556: (0.528296, 0.999857, 0.005304), 557: (0.544692, 0.999305, 0.004900),
    558: (0.561209, 0.998326, 0.004534), 559: (0.577822, 0.996899, 0.004202), 560: (0.594500, 0.995000, 0.003900),
    561: (0.611221, 0.992601, 0.003623), 562: (0.627976, 0.989743, 0.003371), 563: (0.644760, 0.986444, 0.003141),
    564: (0.661570, 0.982724, 0.002935), 565: (0.678400, 0.978600, 0.002750), 566: (0.695239, 0.974084, 0.002585),
    567: (0.712059, 0.969171, 0.002439), 568: (0.728828, 0.963857, 0.002309), 569: (0.745519, 0.958135, 0.002197),
    570: (0.762100, 0.952000, 0.002100), 571: (0.778543, 0.945450, 0.002018), 572: (0.794826, 0.938499, 0.001948),
    573: (0.810926, 0.931163, 0.001890), 574: (0.826825, 0.923458, 0.001841), 575: (0.842500, 0.915400, 0.001800),
    576: (0.857933, 0.907006, 0.001766), 577: (0.873082, 0.898277, 0.001738), 578: (0.887894, 0.889205, 0.001711),
    579: (0.902318, 0.879782, 0.001683), 580: (0.916300, 0.870000, 0.001650), 581: (0.929800, 0.859861, 0.001610),
    582: (0.942798, 0.849392, 0.001564), 583: (0.955278, 0.838622, 0.001514), 584: (0.967218, 0.827581, 0.001459),
    585: (0.978600, 0.816300, 0.001400), 586: (0.989386, 0.804795, 0.001337), 587: (0.999549, 0.793082, 0.001270),
    588: (1.009089, 0.781192, 0.001205), 589: (1.018006, 0.769155, 0.001147), 590: (1.026300, 0.757000, 0.001100),
    591: (1.033983, 0.744754, 0.001069), 592: (1.049860, 0.732422, 0.001049), 593: (1.047188, 0.720004, 0.001036),
    594: (1.052467, 0.707497, 0.001021), 595: (1.056700, 0.694900, 0.001000), 596: (1.059794, 0.682219, 0.000969),
    597: (1.061799, 0.669472, 0.000930), 598: (1.062807, 0.656674, 0.000887), 599: (1.062910, 0.643845, 0.000843),
    600: (1.062200, 0.631000, 0.000800), 601: (1.067352, 0.618156, 0.000761), 602: (1.058444, 0.605314, 0.000724),
    603: (1.055224, 0.592476, 0.000686), 604: (1.050977, 0.579638, 0.000645), 605: (1.045600, 0.566800, 0.000600),
    606: (1.039037, 0.553961, 0.000548), 607: (1.031361, 0.541137, 0.000492), 608: (1.022666, 0.528353, 0.000435),
    609: (1.013048, 0.515632, 0.000383), 610: (1.002600, 0.503000, 0.000340), 611: (0.991368, 0.490469, 0.000307),
    612: (0.979331, 0.478030, 0.000283), 613: (0.966492, 0.465678, 0.000265), 614: (0.952848, 0.453403, 0.000252),
    615: (0.938400, 0.441200, 0.000240), 616: (0.923194, 0.429080, 0.000230), 617: (0.907244, 0.417036, 0.000221),
    618: (0.890502, 0.405032, 0.000212), 619: (0.872920, 0.393032, 0.000202), 620: (0.854450, 0.381000, 0.000190),
    621: (0.835084, 0.368918, 0.000174), 622: (0.814946, 0.356827, 0.000156), 623: (0.794186, 0.344777, 0.000136),
    624: (0.772954, 0.332818, 0.000117), 625: (0.751400, 0.321000, 0.000100), 626: (0.729584, 0.309338, 0.000086),
    627: (0.707589, 0.297850, 0.000075), 628: (0.685602, 0.286594, 0.000065), 629: (0.663810, 0.275625, 0.000057),
    630: (0.642400, 0.265000, 0.000050), 631: (0.621515, 0.254763, 0.000044), 632: (0.601114, 0.244890, 0.000039),
    633: (0.581105, 0.235334, 0.000036), 634: (0.561398, 0.226053, 0.000033), 635: (0.541900, 0.217000, 0.000030),
    636: (0.522600, 0.208162, 0.000028), 637: (0.503546, 0.199549, 0.000026), 638: (0.484744, 0.191155, 0.000024),
    639: (0.466194, 0.182974, 0.000022), 640: (0.447900, 0.175000, 0.000020), 641: (0.429861, 0.167224, 0.000018),
    642: (0.412098, 0.159646, 0.000016), 643: (0.394644, 0.152278, 0.000014), 644: (0.377533, 0.145126, 0.000012),
    645: (0.360800, 0.138200, 0.000010), 646: (0.344456, 0.131500, 0.000008), 647: (0.328517, 0.125025, 0.000005),
    648: (0.313019, 0.118779, 0.000003), 649: (0.298001, 0.112769, 0.000001), 650: (0.283500, 0.107000, 0.000000),
    651: (0.269545, 0.101476, 0.000000), 652: (0.256118, 0.096189, 0.000000), 653: (0.243190, 0.091123, 0.000000),
    654: (0.230727, 0.086265, 0.000000), 655: (0.218700, 0.081600, 0.000000), 656: (0.207097, 0.077121, 0.000000),
    657: (0.195923, 0.072826, 0.000000), 658: (0.185171, 0.068710, 0.000000), 659: (0.174832, 0.064770, 0.000000),
    660: (0.164900, 0.061000, 0.000000), 661: (0.155367, 0.057396, 0.000000), 662: (0.146230, 0.053955, 0.000000),
    663: (0.137490, 0.050674, 0.000000), 664: (0.129147, 0.047550, 0.000000), 665: (0.121200, 0.044580, 0.000000),
    666: (0.113640, 0.041759, 0.000000), 667: (0.106465, 0.039085, 0.000000), 668: (0.099690, 0.036564, 0.000000),
    669: (0.093331, 0.034200, 0.000000), 670: (0.087400, 0.032000, 0.000000), 671: (0.081901, 0.029963, 0.000000),
    672: (0.076804, 0.028077, 0.000000), 673: (0.072077, 0.026329, 0.000000), 674: (0.067687, 0.024708, 0.000000),
    675: (0.063600, 0.023200, 0.000000), 676: (0.059807, 0.021801, 0.000000), 677: (0.056282, 0.020501, 0.000000),
    678: (0.052971, 0.019281, 0.000000), 679: (0.049819, 0.018121, 0.000000), 680: (0.046770, 0.017000, 0.000000),
    681: (0.043784, 0.015904, 0.000000), 682: (0.040875, 0.014837, 0.000000), 683: (0.038073, 0.013811, 0.000000),
    684: (0.035405, 0.012835, 0.000000), 685: (0.032900, 0.011920, 0.000000), 686: (0.030564, 0.011068, 0.000000),
    687: (0.028381, 0.010273, 0.000000), 688: (0.026345, 0.009533, 0.000000), 689: (0.024453, 0.008846, 0.000000),
    690: (0.022700, 0.008210, 0.000000), 691: (0.021084, 0.007624, 0.000000), 692: (0.019600, 0.007085, 0.000000),
    693: (0.018237, 0.006591, 0.000000), 694: (0.016987, 0.006138, 0.000000), 695: (0.015840, 0.005723, 0.000000),
    696: (0.014791, 0.005343, 0.000000), 697: (0.013831, 0.004996, 0.000000), 698: (0.012949, 0.004676, 0.000000),
    699: (0.012129, 0.004380, 0.000000), 700: (0.011359, 0.004102, 0.000000), 701: (0.010629, 0.003838, 0.000000),
    702: (0.009939, 0.003589, 0.000000), 703: (0.009288, 0.003354, 0.000000), 704: (0.008679, 0.003134, 0.000000),
    705: (0.008111, 0.002929, 0.000000), 706: (0.007582, 0.002738, 0.000000), 707: (0.007089, 0.002560, 0.000000),
    708: (0.006627, 0.002393, 0.000000), 709: (0.006195, 0.002237, 0.000000), 710: (0.005790, 0.002091, 0.000000),
    711: (0.005410, 0.001954, 0.000000), 712: (0.005053, 0.001825, 0.000000), 713: (0.004718, 0.001704, 0.000000),
    714: (0.004404, 0.001590, 0.000000), 715: (0.004109, 0.001484, 0.000000), 716: (0.003834, 0.001384, 0.000000),
    717: (0.003576, 0.001291, 0.000000), 718: (0.003334, 0.001204, 0.000000), 719: (0.003109, 0.001123, 0.000000),
    720: (0.002899, 0.001047, 0.000000), 721: (0.002704, 0.000977, 0.000000), 722: (0.002523, 0.000911, 0.000000),
    723: (0.002354, 0.000850, 0.000000), 724: (0.002197, 0.000793, 0.000000), 725: (0.002049, 0.000740, 0.000000),
    726: (0.001911, 0.000690, 0.000000), 727: (0.001781, 0.000643, 0.000000), 728: (0.001660, 0.000599, 0.000000),
    729: (0.001546, 0.000558, 0.000000), 730: (0.001440, 0.000520, 0.000000), 731: (0.001340, 0.000484, 0.000000),
    732: (0.001246, 0.000450, 0.000000), 733: (0.001158, 0.000418, 0.000000), 734: (0.001076, 0.000389, 0.000000),
    735: (0.001000, 0.000361, 0.000000), 736: (0.000929, 0.000335, 0.000000), 737: (0.000862, 0.000311, 0.000000),
    738: (0.000801, 0.000289, 0.000000), 739: (0.000743, 0.000268, 0.000000), 740: (0.000690, 0.000249, 0.000000),
    741: (0.000641, 0.000231, 0.000000), 742: (0.000595, 0.000215, 0.000000), 743: (0.000552, 0.000199, 0.000000),
    744: (0.000512, 0.000185, 0.000000), 745: (0.000476, 0.000172, 0.000000), 746: (0.000442, 0.000160, 0.000000),
    747: (0.000412, 0.000149, 0.000000), 748: (0.000383, 0.000138, 0.000000), 749: (0.000357, 0.000129, 0.000000),
    750: (0.000332, 0.000120, 0.000000), 751: (0.000310, 0.000112, 0.000000), 752: (0.000289, 0.000104, 0.000000),
    753: (0.000270, 0.000097, 0.000000), 754: (0.000252, 0.000091, 0.000000), 755: (0.000235, 0.000085, 0.000000),
    756: (0.000219, 0.000079, 0.000000), 757: (0.000205, 0.000074, 0.000000), 758: (0.000191, 0.000069, 0.000000),
    759: (0.000178, 0.000064, 0.000000), 760: (0.000166, 0.000060, 0.000000), 761: (0.000155, 0.000056, 0.000000),
    762: (0.000145, 0.000052, 0.000000), 763: (0.000135, 0.000049, 0.000000), 764: (0.000126, 0.000045, 0.000000),
    765: (0.000117, 0.000042, 0.000000), 766: (0.000110, 0.000040, 0.000000), 767: (0.000102, 0.000037, 0.000000),
    768: (0.000095, 0.000034, 0.000000), 769: (0.000089, 0.000032, 0.000000), 770: (0.000083, 0.000030, 0.000000),
    771: (0.000078, 0.000028, 0.000000), 772: (0.000072, 0.000026, 0.000000), 773: (0.000067, 0.000024, 0.000000),
    774: (0.000063, 0.000023, 0.000000), 775: (0.000059, 0.000021, 0.000000), 776: (0.000055, 0.000020, 0.000000),
    777: (0.000051, 0.000018, 0.000000), 778: (0.000048, 0.000017, 0.000000), 779: (0.000044, 0.000016, 0.000000),
    780: (0.000042, 0.000015, 0.000000), 781: (0.000039, 0.000014, 0.000000), 782: (0.000036, 0.000013, 0.000000),
    783: (0.000034, 0.000012, 0.000000), 784: (0.000031, 0.000011, 0.000000), 785: (0.000029, 0.000011, 0.000000),
    786: (0.000027, 0.000010, 0.000000), 787: (0.000026, 0.000009, 0.000000), 788: (0.000024, 0.000009, 0.000000),
    789: (0.000022, 0.000008, 0.000000), 790: (0.000021, 0.000007, 0.000000), 791: (0.000019, 0.000007, 0.000000),
    792: (0.000018, 0.000006, 0.000000), 793: (0.000017, 0.000006, 0.000000), 794: (0.000016, 0.000006, 0.000000),
    795: (0.000015, 0.000005, 0.000000), 796: (0.000014, 0.000005, 0.000000), 797: (0.000013, 0.000005, 0.000000),
    798: (0.000012, 0.000004, 0.000000), 799: (0.000011, 0.000004, 0.000000), 800: (0.000010, 0.000004, 0.000000),
    801: (0.000010, 0.000003, 0.000000), 802: (0.000009, 0.000003, 0.000000), 803: (0.000008, 0.000003, 0.000000),
    804: (0.000008, 0.000003, 0.000000), 805: (0.000007, 0.000003, 0.000000), 806: (0.000007, 0.000002, 0.000000),
    807: (0.000006, 0.000002, 0.000000), 808: (0.000006, 0.000002, 0.000000), 809: (0.000005, 0.000002, 0.000000),
    810: (0.000005, 0.000002, 0.000000), 811: (0.000005, 0.000002, 0.000000), 812: (0.000004, 0.000002, 0.000000),
    813: (0.000004, 0.000001, 0.000000), 814: (0.000004, 0.000001, 0.000000), 815: (0.000004, 0.000001, 0.000000),
    816: (0.000003, 0.000001, 0.000000), 817: (0.000003, 0.000001, 0.000000), 818: (0.000003, 0.000001, 0.000000),
    819: (0.000003, 0.000001, 0.000000), 820: (0.000003, 0.000001, 0.000000), 821: (0.000002, 0.000001, 0.000000),
    822: (0.000002, 0.000001, 0.000000), 823: (0.000002, 0.000001, 0.000000), 824: (0.000002, 0.000001, 0.000000),
    825: (0.000002, 0.000001, 0.000000), 826: (0.000002, 0.000001, 0.000000), 827: (0.000002, 0.000001, 0.000000),
    828: (0.000001, 0.000001, 0.000000), 829: (0.000001, 0.000000, 0.000000), 830: (0.000001, 0.000000, 0.000000)
}
