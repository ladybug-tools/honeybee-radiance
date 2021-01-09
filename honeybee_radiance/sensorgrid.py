"""A grid of sensors."""
from __future__ import division

from .sensor import Sensor
from .lightpath import light_path_from_room

import honeybee.typing as typing
import ladybug.futil as futil
from ladybug_geometry.geometry3d.face import Face3D
from ladybug_geometry.geometry3d.mesh import Mesh3D

import os
import math
try:
    from itertools import izip as zip
except ImportError:  # python 3
    pass


class SensorGrid(object):
    """A grid of sensors.

    Args:
        identifier: Text string for a unique SensorGrid ID. Must not contain spaces
            or special characters. This will be used to identify the object in the
            exported Radiance files.
        sensors: A collection of Sensors.

    Properties:
        * identifier
        * display_name
        * sensors
        * positions
        * directions
        * room_identifier
        * light_path
        * mesh
        * base_geometry
    """

    __slots__ = ('_identifier', '_display_name', '_sensors', '_room_identifier',
                 '_light_path', '_mesh', '_base_geometry')

    def __init__(self, identifier, sensors):
        """Initialize a SensorGrid."""
        self.identifier = typing.valid_rad_string(identifier)
        self._display_name = None
        self.sensors = sensors
        self._room_identifier = None
        self._light_path = None
        self._mesh = None
        self._base_geometry = None

    @classmethod
    def from_dict(cls, ag_dict):
        """Create a sensor grid from a dictionary in the following format.

        .. code-block:: python

            {
            "type": "SensorGrid",
            "identifier": str,  # SensorGrid identifier
            "display_name": str,  # SensorGrid display name
            "sensors": [],  # list of Sensor dictionaries
            'room_identifier': str,  # optional room identifier
            'light_path':  []  # optional list of lists for light path
            }
        """
        assert ag_dict['type'] == 'SensorGrid', \
            'Expected SensorGrid dictionary. Got {}.'.format(ag_dict['type'])
        sensors = (Sensor.from_dict(sensor) for sensor in ag_dict['sensors'])
        new_obj = cls(identifier=ag_dict["identifier"], sensors=sensors)
        if 'display_name' in ag_dict and ag_dict['display_name'] is not None:
            new_obj.display_name = ag_dict['display_name']
        if 'room_identifier' in ag_dict and ag_dict['room_identifier'] is not None:
            new_obj.room_identifier = ag_dict['room_identifier']
        if 'light_path' in ag_dict and ag_dict['light_path'] is not None:
            new_obj.light_path = ag_dict['light_path']
        if 'mesh' in ag_dict and ag_dict['mesh'] is not None:
            new_obj.mesh = Mesh3D.from_dict(ag_dict['mesh'])
        if 'base_geometry' in ag_dict and ag_dict['base_geometry'] is not None:
            new_obj.base_geometry = \
                tuple(Face3D.from_dict(face) for face in ag_dict['base_geometry'])
        return new_obj

    @classmethod
    def from_planar_positions(cls, identifier, positions, plane_normal):
        """Create a sensor grid from a collection of positions with the same direction.

        Args:
            identifier: Text string for a unique SensorGrid ID. Must not contain spaces
                or special characters. This will be used to identify the object across
                a model and in the exported Radiance files.
            positions: A list of (x, y ,z) for position of sensors.
            plane_normal: (x, y, z) for direction of sensors.
        """
        sg = (Sensor(l, plane_normal) for l in positions)
        return cls(identifier, sg)

    @classmethod
    def from_position_and_direction(cls, identifier, positions, directions):
        """Create a sensor grid from a collection of positions and directions.

        The length of positions and directions should be the same. In case the lists have
        different lengths the shorter list will be used as the reference.

        Args:
            identifier: Text string for a unique SensorGrid ID. Must not contain spaces
                or special characters. This will be used to identify the object across
                a model and in the exported Radiance files.
            positions: A list of (x, y ,z) for position of sensors.
            directions: A list of (x, y, z) for direction of sensors.
        """
        sg = tuple(Sensor(l, v) for l, v in zip(positions, directions))
        return cls(identifier, sg)

    @classmethod
    def from_mesh3d(cls, identifier, mesh):
        """Create a sensor grid from a ladybug_geometry Mesh3D.

        The centroids of the mesh faces will be used to create the sensor positions
        and the normals of the faces will set the directions. The mesh will be
        assigned to the resulting SensorGrid's mesh property.

        Args:
            identifier: Text string for a unique SensorGrid ID. Must not contain spaces
                or special characters. This will be used to identify the object across
                a model and in the exported Radiance files.
            mesh: A ladybug_geometry Mesh3D.
        """
        assert isinstance(mesh, Mesh3D), 'Expected ladybug_geometry Mesh3D for ' \
            'SensorGrid.from_mesh3d. Got {}.'.format(type(mesh))
        positions = [(pt.x, pt.y, pt.z) for pt in mesh.face_centroids]
        directions = [(vec.x, vec.y, vec.z) for vec in mesh.face_normals]
        s_grid = cls.from_position_and_direction(identifier, positions, directions)
        s_grid.mesh = mesh
        return s_grid

    @classmethod
    def from_face3d(cls, identifier, faces, x_dim, y_dim=None, offset=0):
        """Create a sensor grid from an array of ladybug_geometry Face3D.

        The Face3D will be converted into a gridded mesh using the input x_dim
        and y_dim. The centroids of the mesh faces will be used to create the
        sensor positions and the normals of the faces will set the directions.
        The mesh will be assigned to the resulting SensorGrid's mesh property
        and the Face3Ds assigned to the base_geometry.

        Args:
            identifier: Text string for a unique SensorGrid ID. Must not contain spaces
                or special characters. This will be used to identify the object across
                a model and in the exported Radiance files.
            faces: An array of ladybug_geometry Face3D.
            x_dim: The x dimension of the grid cells as a number.
            y_dim: The y dimension of the grid cells as a number. Default is None,
                which will assume the same cell dimension for y as is set for x.
            offset: A number for how far to offset the grid from the base face.
        """
        meshes = [face.mesh_grid(x_dim, y_dim, offset, True) for face in faces]
        if len(meshes) == 1:
            s_grid = cls.from_mesh3d(identifier, meshes[0])
        elif len(meshes) > 1:
            s_grid = cls.from_mesh3d(identifier, Mesh3D.join_meshes(meshes))
        s_grid.base_geometry = faces
        return s_grid

    @classmethod
    def from_file(cls, file_path, start_line=None, end_line=None, identifier=None):
        """Create a sensor grid from a sensor (.pts) file.

        The sensors must be structured as

        x1, y1, z1, dx1, dy1, dz1
        x2, y2, z2, dx2, dy2, dz2
        ...

        The lines that start with # will be considred as commented lines and won't be
        loaded. However, these commented lines are still considered in total line
        count for the start_line and end_line inputs.

        Args:
            file_path: Full path to sensors file
            start_line: Start line including the comments (default: 0).
            end_line: End line as an integer including the comments
                (default: last line in file).
            identifier: Text string for a unique SensorGrid ID. Must not contain spaces
                or special characters. This will be used to identify the object across
                a model and in the exported Radiance files. If None, the file name
                will be used. (Default: None)
        """
        if not os.path.isfile(file_path):
            raise IOError("Can't find {}.".format(file_path))
        identifier = identifier or os.path.split(os.path.splitext(file_path)[0])[-1]

        start_line = int(start_line) if start_line is not None else 0
        try:
            end_line = int(end_line)
        except TypeError:
            end_line = float('+inf')

        line_count = end_line - start_line + 1

        sensors = []
        with open(file_path, 'r') as inf:
            for _ in range(start_line):
                next(inf)

            for count, l in enumerate(inf):
                if not count < line_count:
                    break
                if not l or l[0] == '#':
                    # commented line
                    continue
                sensors.append(Sensor.from_raw_values(*l.split()))

        return cls(identifier, sensors)

    @property
    def identifier(self):
        """Get or set text for a unique SensorGrid identifier."""
        return self._identifier

    @identifier.setter
    def identifier(self, n):
        self._identifier = typing.valid_rad_string(n, 'sensor grid identifier')

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
    def sensors(self):
        """Get or set a tuple of Sensor objects for the grid sensors."""
        return self._sensors

    @sensors.setter
    def sensors(self, value):
        self._sensors = tuple(value)
        for sen in self._sensors:
            if not isinstance(sen, Sensor):
                raise ValueError(
                    'SensorGrid sensors must be of the Sensor type not %s' % type(sen))

    @property
    def positions(self):
        """Get a generator of sensor positions as x, y, z."""
        return (ap.position for ap in self.sensors)

    @property
    def directions(self):
        """Get a generator of sensor directions as x, y , z."""
        return (ap.direction for ap in self.sensors)

    @property
    def count(self):
        """Get the number of sensors."""
        return len(self._sensors)

    @property
    def room_identifier(self):
        """Get or set text for the Room identifier to which this SensorGrid belongs.

        This will be used in the info_dict method to narrow down the
        number of aperture groups that have to be run with this sensor grid.
        If None, the grid will be run with all aperture groups in the model.
        """
        return self._room_identifier

    @room_identifier.setter
    def room_identifier(self, n):
        self._room_identifier = typing.valid_string(n)

    @property
    def light_path(self):
        """Get or set list of lists for the light path from the grid to the sky.

        Each sub-list contains identifiers of aperture groups through which light
        passes. (eg. [['SouthWindow1'], ['static_apertures', 'NorthWindow2']]).
        Setting this property will override any auto-calculation of the light
        path from the model upon export to the simulation.
        """
        return self._light_path

    @light_path.setter
    def light_path(self, l_path):
        if l_path is not None:
            assert isinstance(l_path, (tuple, list)), 'Expected list or tuple for ' \
                'light_path. Got {}.'.format(type(l_path))
            for ap_list in l_path:
                assert isinstance(ap_list, (tuple, list)), 'Expected list or tuple ' \
                    'for light_path sub-list. Got {}.'.format(type(ap_list))
                for ap in ap_list:
                    assert isinstance(ap, str), 'Expected text for light_path ' \
                        'aperture group identifier. Got {}.'.format(type(ap))
        self._light_path = l_path

    @property
    def mesh(self):
        """Get or set an optional ladybug_geometry Mesh3D that aligns with the sensors.

        Note that the number of sensors in the grid must match the number of
        faces or the number vertices within the Mesh3D.
        """
        return self._mesh

    @mesh.setter
    def mesh(self, value):
        if value is not None:
            assert isinstance(value, Mesh3D), \
                'Expected Mesh3D for SensorGrid mesh. Got {}.'.format(type(value))
            assert self.count == len(value.faces) or self.count == len(value.vertices), \
                'Number of sensors ({}) does not match the number of mesh faces ({}) ' \
                'nor the number of vertices ({}).'.format(
                    self.count, len(value.faces), len(value.vertices))
        self._mesh = value

    @property
    def base_geometry(self):
        """Get or set an optional array of ladybug_geometry Face3D used to make the grid.

        There are no restrictions on how this property relates to the sensors and it
        is provided only to assist with the display of the grid when the number
        of sensors or the mesh is too large to be practically visualized.
        """
        return self._base_geometry

    @base_geometry.setter
    def base_geometry(self, value):
        if value is not None:
            if not isinstance(value, tuple):
                value = tuple(value)
            for face in value:
                assert isinstance(face, Face3D), 'Expected Face3D for SensorGrid ' \
                    'base_geometry. Got {}.'.format(type(value))
        self._base_geometry = value

    def info_dict(self, model=None):
        """Get a dictionary with information about the SensorGrid.

        This can be written as a JSON into a model radiance folder to narrow
        down the number of aperture groups that have to be run with this sensor grid.

        Args:
            model: A honeybee Model object which will be used to identify
                the aperture groups that will be run with this sensor grid.
        """
        base = {'count': self.count}
        if self._light_path:
            base['light_path'] = self._light_path
        elif model and self._room_identifier:  # auto-calculate the light path
            base['light_path'] = light_path_from_room(model, self._room_identifier)
        return base

    def to_radiance(self):
        """Return sensors grid as a Radiance string."""
        return "\n".join((ap.to_radiance() for ap in self._sensors))

    def to_file(self, folder, file_name=None, mkdir=False):
        """Write this sensor grid to a Radiance sensors file.

        Args:
            folder: Target folder.
            file_name: Optional file name without extension. (Default: self.identifier)
            mkdir: A boolean to indicate if the folder should be created in case it
                doesn't exist already. (Default: False).

        Returns:
            Full path to newly created file.
        """
        identifier = file_name or self.identifier + '.pts'
        if not identifier.endswith('.pts'):
            identifier += '.pts'
        return futil.write_to_file_by_name(
            folder, identifier, self.to_radiance() + '\n', mkdir)

    def to_files(self, folder, count, base_name=None, mkdir=False):
        """Split this sensor grid and write them to several files.

        Args:
            folder: Target folder.
            count: Number of files.
            base_name: Optional text string for a unique base name for the sensor
                grid files. (Default: self.identifier)
            mkdir: A boolean to indicate if the folder should be created in case it
                doesn't exist already (Default: False).

        Returns:
            A list of dicts containing the grid name, path to the grid and full path
            to the grid.
        """
        count = typing.int_in_range(count, 1, input_name='file count')
        base_name = base_name or self.identifier
        if count == 1 or self.count == 0:
            name = '%s_0000' % base_name
            full_path = self.to_file(folder, name, mkdir)
            return [
                {'name': name if not name.endswith('.pts') else name.replace('.pts', ''),
                 'path': name + '.pts' if not name.endswith('.pts') else name,
                 'full_path': full_path,
                 'count': self.count}
            ]
        # calculate sensor count in each file
        sc = int(round(self.count / count))
        sensors = iter(self._sensors)
        for fc in range(count - 1):
            name = '%s_%04d.pts' % (base_name, fc)
            content = '\n'.join((next(sensors).to_radiance() for _ in range(sc)))
            futil.write_to_file_by_name(folder, name, content + '\n', mkdir)

        # write whatever is left to the last file
        name = '%s_%04d.pts' % (base_name, count - 1)
        content = '\n'.join((sensor.to_radiance() for sensor in sensors))
        futil.write_to_file_by_name(folder, name, content + '\n', mkdir)

        grids_info = []

        for c in range(count):
            name = '%s_%04d' % (base_name, c)
            path = '%s.pts' % name
            full_path = os.path.join(folder, path)

            grids_info.append({
                'name': name,
                'path': path,
                'full_path': full_path,
                'count': sc
            })

        # adjust the count for the last grid
        grids_info[-1]['count'] = self.count - sc * (count - 1)

        return grids_info

    def to_dict(self):
        """Convert SensorGrid to a dictionary."""
        base = {
            'type': 'SensorGrid',
            'identifier': self.identifier,
            'sensors': [sen.to_dict() for sen in self.sensors]
        }
        if self._display_name is not None:
            base['display_name'] = self.display_name
        if self._room_identifier is not None:
            base['room_identifier'] = self.room_identifier
        if self._light_path is not None:
            base['light_path'] = self.light_path
        if self._mesh is not None:
            base['mesh'] = self._mesh.to_dict()
        if self._base_geometry is not None:
            base['base_geometry'] = [face.to_dict() for face in self._base_geometry]
        return base

    def move(self, moving_vec):
        """Move this sensor grid along a vector.

        Args:
            moving_vec: A ladybug_geometry Vector3D with the direction and distance
                to move the sensor.
        """
        for sens in self._sensors:
            sens.move(moving_vec)
        if self._mesh is not None:
            self._mesh = self._mesh.move(moving_vec)
        if self._base_geometry is not None:
            self._base_geometry = \
                tuple(face.move(moving_vec) for face in self._base_geometry)

    def rotate(self, angle, axis, origin):
        """Rotate this sensor grid by a certain angle around an axis and origin.

        Args:
            angle: An angle for rotation in degrees.
            axis: Rotation axis as a Vector3D.
            origin: A ladybug_geometry Point3D for the origin around which the
                object will be rotated.
        """
        for sens in self._sensors:
            sens.rotate(angle, axis, origin)
        r_angle = math.radians(angle)
        if self._mesh is not None:
            self._mesh = self._mesh.rotate(r_angle, axis, origin)
        if self._base_geometry is not None:
            self._base_geometry = \
                tuple(face.rotate(r_angle, axis, origin) for face in self._base_geometry)

    def rotate_xy(self, angle, origin):
        """Rotate this sensor grid counterclockwise in the world XY plane by an angle.

        Args:
            angle: An angle in degrees.
            origin: A ladybug_geometry Point3D for the origin around which the
                object will be rotated.
        """
        for sens in self._sensors:
            sens.rotate_xy(angle, origin)
        r_angle = math.radians(angle)
        if self._mesh is not None:
            self._mesh = self._mesh.rotate_xy(r_angle, origin)
        if self._base_geometry is not None:
            self._base_geometry = \
                tuple(face.rotate_xy(r_angle, origin) for face in self._base_geometry)

    def reflect(self, plane):
        """Reflect this sensor grid across a plane.

        Args:
            plane: A ladybug_geometry Plane across which the object will
                be reflected.
        """
        for sens in self._sensors:
            sens.reflect(plane)
        if self._mesh is not None:
            self._mesh = self._mesh.reflect(plane.n, plane.o)
        if self._base_geometry is not None:
            self._base_geometry = \
                tuple(face.reflect(plane.n, plane.o) for face in self._base_geometry)

    def scale(self, factor, origin=None):
        """Scale this sensor grid by a factor from an origin point.

        Args:
            factor: A number representing how much the object should be scaled.
            origin: A ladybug_geometry Point3D representing the origin from which
                to scale. If None, it will be scaled from the World origin (0, 0, 0).
        """
        for sens in self._sensors:
            sens.scale(factor, origin)
        if self._mesh is not None:
            self._mesh = self._mesh.scale(factor, origin)
        if self._base_geometry is not None:
            self._base_geometry = \
                tuple(face.scale(factor, origin) for face in self._base_geometry)

    def duplicate(self):
        """Get a copy of this object."""
        return self.__copy__()

    def __len__(self):
        """Number of sensors in this grid."""
        return len(self.sensors)

    def __getitem__(self, index):
        """Get a sensor for an index."""
        return self.sensors[index]

    def __copy__(self):
        new_obj = SensorGrid(self.identifier, (sen.duplicate() for sen in self.sensors))
        new_obj._display_name = self._display_name
        new_obj._room_identifier = self._room_identifier
        new_obj._light_path = self._light_path
        new_obj._mesh = self._mesh
        new_obj._base_geometry = self._base_geometry
        return new_obj

    def __key(self):
        """A tuple based on the object properties, useful for hashing."""
        return (self.identifier, self._display_name, self._room_identifier) + \
            tuple(hash(sensor) for sensor in self.sensors)

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        return isinstance(other, SensorGrid) and self.__key() == other.__key() and \
            self.light_path == other.light_path

    def __ne__(self, value):
        return not self.__eq__(value)

    def __iter__(self):
        """Sensors iterator."""
        return iter(self.sensors)

    def __str__(self):
        """String repr."""
        return self.to_radiance()

    def ToString(self):
        """Overwrite ToString .NET method."""
        return self.__repr__()

    def __repr__(self):
        """Get the string representation of the sensor grid."""
        return 'SensorGrid: {} [{} sensors]'.format(self.display_name, len(self.sensors))
