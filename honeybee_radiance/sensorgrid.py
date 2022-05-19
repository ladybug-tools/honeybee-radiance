"""A grid of sensors."""
from __future__ import division

from .sensor import Sensor
from .lightpath import light_path_from_room

from honeybee.facetype import AirBoundary
import honeybee.typing as typing
import ladybug.futil as futil
from ladybug_geometry.geometry3d.pointvector import Point3D, Vector3D
from ladybug_geometry.geometry3d.face import Face3D
from ladybug_geometry.geometry3d.mesh import Mesh3D

import os
import json
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
        * group_identifier
        * full_identifier

    """

    __slots__ = ('_identifier', '_display_name', '_sensors', '_room_identifier',
                 '_light_path', '_mesh', '_base_geometry', '_group_identifier')

    def __init__(self, identifier, sensors):
        """Initialize a SensorGrid."""
        self.identifier = identifier
        self._display_name = None
        self.sensors = sensors
        self._room_identifier = None
        self._group_identifier = None
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
            'group_identifier': str,  # optional group identifier
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
        if 'group_identifier' in ag_dict and ag_dict['group_identifier'] is not None:
            new_obj.group_identifier = ag_dict['group_identifier']
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
            positions: A list of (x, y ,z) tuples for position of sensors.
            plane_normal: (x, y, z) tuples for direction of sensors.
        """
        sg = (Sensor(pt, plane_normal) for pt in positions)
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
            positions: A list of (x, y ,z) tuples for position of sensors.
            directions: A list of (x, y, z) tuples for direction of sensors.
        """
        sg = tuple(Sensor(pt, v) for pt, v in zip(positions, directions))
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
    def from_face3d(cls, identifier, faces, x_dim, y_dim=None, offset=0, flip=False):
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
            faces: An array of ladybug_geometry Face3Ds from which a SensorGrid will
                be generated.
            x_dim: The x dimension of the grid cells as a number.
            y_dim: The y dimension of the grid cells as a number. Default is None,
                which will assume the same cell dimension for y as is set for x.
            offset: A number for how far to offset the grid from the base face.
            flip: Set to True to have the mesh normals reversed from the direction of
                this face and to have the offset input move the mesh in the opposite
                direction from this face normal. Defaults to False, which means the
                normal direction of the face will be used as the direction of the
                sensor grids.
        """
        meshes = []
        for face in faces:
            try:
                meshes.append(face.mesh_grid(x_dim, y_dim, offset, flip))
            except AssertionError:  # tiny geometry not compatible with quad faces
                continue
        assert len(meshes) > 0, 'None of the Face3Ds input to SensorGrid.from_face3d ' \
            'can produce a quad grid at the specified grid dimensions.'
        if len(meshes) == 1:
            s_grid = cls.from_mesh3d(identifier, meshes[0])
        elif len(meshes) > 1:
            s_grid = cls.from_mesh3d(identifier, Mesh3D.join_meshes(meshes))
        s_grid.base_geometry = faces
        return s_grid

    @classmethod
    def from_positions_radial(
            cls, identifier, positions, dir_count=8, start_vector=Vector3D(0, -1, 0),
            mesh_radius=0):
        """Create a sensor grid from radial directions around sensor positions.

        This type of sensor grid is particularly helpful for studies of multiple view
        directions, such as imageless glare studies.

        Args:
            identifier: Text string for a unique SensorGrid ID. Must not contain spaces
                or special characters. This will be used to identify the object across
                a model and in the exported Radiance files.
            positions: A list of (x, y ,z) tuples for position of sensors.
            dir_count: A positive integer for the number of radial directions
                to be generated around each position. (Default: 8).
            start_vector: A Vector3D to set the start direction of the generated
                directions. This can be used to orient the resulting sensors to
                specific parts of the scene. It can also change the elevation of the
                resulting directions since this start vector will always be rotated in
                the XY plane to generate the resulting directions. (Default: (0, -1, 0)).
            mesh_radius: An optional number that can be used to generate a Mesh3D
                that is aligned with the resulting sensors and will automatically
                be assigned to the grid's mesh property. Such meshes will resemble
                a circle around each sensor with the specified radius and will
                contain triangular faces that can be colored with simulation results.
                If zero, no mesh will be generated for the sensor grid. (Default: 0).
        """
        # set up the vectors to generate the rays
        inc_ang = (math.pi * 2) / dir_count
        vw_vecs = [start_vector.rotate_xy(i * inc_ang) for i in range(dir_count)]
        vw_vecs = [(round(v.x, 5), round(v.y, 5), round(v.z, 3)) for v in vw_vecs]
        # set up the sensor grid object
        sensors = tuple(Sensor(pt, v) for pt in positions for v in vw_vecs)
        sg = cls(identifier, sensors)
        # generate the mesh if it was requested
        if mesh_radius > 0:
            sg.mesh = cls.radial_positions_mesh(
                positions, dir_count, start_vector, mesh_radius)
        return sg

    @classmethod
    def from_mesh3d_radial(
            cls, identifier, mesh, dir_count=8, start_vector=Vector3D(0, -1, 0),
            mesh_radius=0):
        """Create a sensor grid from radial directions around centroids of a Mesh3D.

        This type of sensor grid is particularly helpful for studies of multiple view
        directions, such as imageless glare studies.

        Args:
            identifier: Text string for a unique SensorGrid ID. Must not contain spaces
                or special characters. This will be used to identify the object across
                a model and in the exported Radiance files.
            mesh: A ladybug_geometry Mesh3D from which the sensor grid will be generated.
            dir_count: A positive integer for the number of radial directions
                to be generated around each position. (Default: 8).
            start_vector: A Vector3D to set the start direction of the generated
                directions. This can be used to orient the resulting sensors to
                specific parts of the scene. It can also change the elevation of
                the resulting directions since this start vector will always be
                rotated in the XY plane to generate the resulting directions.
            mesh_radius: An optional number that can be used to generate a Mesh3D
                that is aligned with the resulting sensors and will automatically
                be assigned to the grid's mesh property. Such meshes will resemble
                a circle around each sensor with the specified radius and will
                contain triangular faces that can be colored with simulation results.
                If zero, no mesh will be generated for the sensor grid. (Default: 0).
        """
        assert isinstance(mesh, Mesh3D), 'Expected ladybug_geometry Mesh3D for ' \
            'SensorGrid.from_mesh3d. Got {}.'.format(type(mesh))
        positions = [(pt.x, pt.y, pt.z) for pt in mesh.face_centroids]
        return cls.from_positions_radial(
            identifier, positions, dir_count, start_vector, mesh_radius)

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
        return (ap.pos for ap in self.sensors)

    @property
    def directions(self):
        """Get a generator of sensor directions as x, y , z."""
        return (ap.dir for ap in self.sensors)

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
    def group_identifier(self):
        """Get or set text for the grid group identifier to which this SensorGrid belongs.

        This will be used in the write to radiance folder method to write all the grids
        with the same group identifier under the same subfolder.

        You may use / in name to identify nested grid groups. For example
        floor_1/living_room create a sensor grid under living_room/floor_1 subfolder.

        If None, the grid will be written to the root of grids folder.
        """
        return self._group_identifier

    @group_identifier.setter
    def group_identifier(self, identifier_key):
        if identifier_key is not None:
            identifier_key = \
                '/'.join(
                    typing.valid_rad_string(key, 'sensor grid group identifier')
                    for key in identifier_key.split('/')
                )
        self._group_identifier = identifier_key

    @property
    def full_identifier(self):
        """Get full identifier for a sensor grid.

        For a sensor grid with group identifier it will be group_identifier/identifier
        """
        return self.identifier if not self.group_identifier \
            else '%s/%s' % (self.group_identifier, self.identifier)

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
        base = {
            'count': self.count,
            'name': self.display_name,
            'identifier': self.identifier,
            'group': self.group_identifier or '',
            'full_id': self.full_identifier
        }
        if self._light_path:
            base['light_path'] = self._light_path
        elif model and self._room_identifier:  # auto-calculate the light path
            try:
                base['light_path'] = light_path_from_room(model, self._room_identifier)
            except ValueError:  # room is not in the model; just ignore light path
                pass

        if self._group_identifier:
            base['group_identifier'] = self._group_identifier

        return base

    def enclosure_info_dict(self, model, air_boundary_distance=0):
        """Get a dictionary with information about sensor relation to rooms.

        This can be written as a JSON in order to map sensors with appropriate
        energy simulation results in thermal mapping workflows.

        Args:
            model: A honeybee Model object which will be used to identify
                the rooms/enclosure that each sensor in the grid is contained within.
            air_boundary_distance: An optional number to set the distance from
                air boundaries over which values should be interpolated.
                Using 0 will assume a hard edge between Rooms of the same
                radiant enclosures. (Default: 0).
        """
        # setup rooms and lists to check enclosure info
        enclosures, sensor_indices, air_bound_proximity = {}, [], {}
        has_indoor, has_outdoor = False, False
        rooms = model._rooms
        if self.room_identifier:  # put the assigned room first for faster calculation
            rooms = model.rooms_by_identifier([self.room_identifier]) + rooms

        # have a dictionary to track proximity to AirBoundary faces
        model_ab = {}
        for room in rooms:
            model_ab[room.identifier] = \
                [f for f in room.faces if isinstance(f.type, AirBoundary)]

        def _air_boundary_info(distance, face, room_index):
            """Method to perform interpolation across AirBoundary Faces."""
            adj_room = face.boundary_condition.boundary_condition_objects[-1]
            try:
                adj_i = enclosures[adj_room]
            except KeyError:  # the first time that this room is needed
                adj_i = len(enclosures)
                enclosures[adj_room] = len(enclosures)
            fac_1 = 0.5 + (distance / (air_boundary_distance * 2))
            return {room_index: fac_1, adj_i: 1 - fac_1}

        # loop through the sensors and verify the room that they belong to
        for i, sensor in enumerate(self.sensors):
            sensor_pt = Point3D(*sensor.pos)
            for room in rooms:
                if room.geometry.is_point_inside(sensor_pt):
                    # add the room index of the sensor
                    try:
                        sensor_indices.append(enclosures[room.identifier])
                    except KeyError:  # the first time that this room is needed
                        enclosures[room.identifier] = len(enclosures)
                        sensor_indices.append(enclosures[room.identifier])
                    has_indoor = True
                    # test if the sensor is near any AriBoundary faces
                    air_b = model_ab[room.identifier]
                    if air_boundary_distance > 0 and len(air_b) != 0:
                        for face in air_b:
                            fg = face.geometry
                            close_pt = fg._plane.closest_point(sensor_pt)
                            p_dist = sensor_pt.distance_to_point(close_pt)
                            if p_dist <= air_boundary_distance:
                                close_pt_2d = fg._plane.xyz_to_xy(close_pt)
                                g_dist = fg.polygon2d.distance_to_point(close_pt_2d)
                                f_dist = math.sqrt(p_dist ** 2 + g_dist ** 2)
                                if f_dist <= air_boundary_distance:
                                    ab_info = _air_boundary_info(
                                        f_dist, face, sensor_indices[-1])
                                    try:
                                        air_bound_proximity[i].append(ab_info)
                                    except KeyError:
                                        air_bound_proximity[i] = [ab_info]
                    break  # we found the room and we don't need to iterate
            else:  # the sensor is completely outside and not a part of a room
                sensor_indices.append(-1)
                has_outdoor = True

        # write out the enclosure info JSON
        mapper = sorted(enclosures, key=enclosures.__getitem__)
        return {
            'has_indoor': has_indoor,
            'has_outdoor': has_outdoor,
            'mapper': mapper,
            'sensor_indices': sensor_indices,
            'air_bound_proximity': air_bound_proximity
        }

    def to_radiance(self):
        """Return sensors grid as a Radiance string."""
        return "\n".join((ap.to_radiance() for ap in self._sensors))

    def to_file(self, folder, file_name=None, mkdir=False, ignore_group=False):
        """Write this sensor grid to a Radiance sensors file.

        Args:
            folder: Target folder. If grid is part of a sensor group identifier it will
                be written to a subfolder with group identifier name.
            file_name: Optional file name without extension. (Default: self.identifier)
            mkdir: A boolean to indicate if the folder should be created in case it
                doesn't exist already. (Default: False).
            ignore_group: A boolean to indicate if creating a new subfolder for sensor
                group should be ignored. (Default: False).

        Returns:
            Full path to newly created file.
        """
        identifier = file_name or self.identifier + '.pts'
        if not identifier.endswith('.pts'):
            identifier += '.pts'
        if not ignore_group and self.group_identifier:
            folder = os.path.normpath(os.path.join(folder, self.group_identifier))
            mkdir = True  # in most cases the subfolder does not exist already

        return futil.write_to_file_by_name(
            folder, identifier, self.to_radiance() + '\n', mkdir)

    def to_files(self, folder, count, base_name=None, mkdir=False):
        """Split this sensor grid and write them to several files.

        This method writes the files directly to the folder and doesn't create a
        subfolder for sensor groups if any. You can add the group subfolder to folder
        before calling the method.

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
            full_path = self.to_file(folder, name, mkdir, ignore_group=True)
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
        if self._group_identifier is not None:
            base['group_identifier'] = self.group_identifier
        if self._light_path is not None:
            base['light_path'] = self.light_path
        if self._mesh is not None:
            base['mesh'] = self._mesh.to_dict()
        if self._base_geometry is not None:
            base['base_geometry'] = [face.to_dict() for face in self._base_geometry]
        if self._group_identifier is not None:
            base['group_identifier'] = self.group_identifier
        return base

    def to_json(self, folder, file_name=None, mkdir=False, ignore_group=False):
        """Write this sensor grid to a JSON file.

        Args:
            folder: Target folder. If grid is part of a sensor group identifier it will
                be written to a subfolder with group identifier name.
            file_name: Optional file name without extension. (Default: self.identifier)
            mkdir: A boolean to indicate if the folder should be created in case it
                doesn't exist already. (Default: False).
            ignore_group: A boolean to indicate if creating a new subfolder for sensor
                group should be ignored. (Default: False).

        Returns:
            Full path to newly created file.
        """
        identifier = file_name or self.identifier + '.json'
        if not identifier.endswith('.json'):
            identifier += '.json'
        if not ignore_group and self.group_identifier:
            folder = os.path.normpath(os.path.join(folder, self.group_identifier))
            mkdir = True  # in most cases the subfolder does not exist already
        return futil.write_to_file_by_name(
            folder, identifier, json.dumps(self.to_dict()), mkdir)

    def to_radial_grid(self, dir_count=8, start_vector=Vector3D(0, -1, 0),
                       mesh_radius=0):
        """Get a radial sensor grid using the positions of this grid as a base.

        All properties of this grid will be transferred to the new grid, including
        the identifier, room_identifier, etc. The mesh will be recomputed based
        on the input mesh_radius but any base_geometry will be transferred.

        Note that calling this method on a SensorGrid that is already formatted
        as a radial grid will result in a lot of unwanted duplication of sensors.

        Args:
            dir_count: A positive integer for the number of radial directions
                to be generated around each position. (Default: 8).
            start_vector: A Vector3D to set the start direction of the generated
                directions. This can be used to orient the resulting sensors to
                specific parts of the scene. It can also change the elevation of the
                resulting directions since this start vector will always be rotated in
                the XY plane to generate the resulting directions. (Default: (0, -1, 0)).
            mesh_radius: An optional number that can be used to generate a Mesh3D
                that is aligned with the resulting sensors and will automatically
                be assigned to the grid's mesh property. Such meshes will resemble
                a circle around each sensor with the specified radius and will
                contain triangular faces that can be colored with simulation results.
                If zero, no mesh will be generated for the sensor grid. (Default: 0).
        """
        new_grid = SensorGrid.from_positions_radial(
            self.identifier, self.positions, dir_count, start_vector, mesh_radius)
        new_grid._display_name = self._display_name
        new_grid._room_identifier = self._room_identifier
        new_grid.group_identifier = self.group_identifier
        new_grid._light_path = self._light_path
        new_grid._base_geometry = self._base_geometry
        return new_grid

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

    @staticmethod
    def from_face3d_arrays(
            base_identifier, face_arrays, x_dim, y_dim=None, offset=0, flip=False):
        """Get an array of SensorGrids from an matrix (list of lists) of Face3Ds.

        This method uses the from_face3d classmethod but includes checks to
        catch cases where not of the input Face3Ds can support the generation of
        quad grids. In this case, the invalid SensorGrid will not be generated
        and will be excluded form the output list of SensorGrids.

        Args:
            base_identifier: Text string for a unique SensorGrid ID, which will be used
                as a base for all of the output SensorGrid IDs. Must not contain spaces
                or special characters.
            faces: An matrix (list of lists) of ladybug_geometry Face3Ds from which
                SensorGrids will be generated.
            x_dim: The x dimension of the grid cells as a number.
            y_dim: The y dimension of the grid cells as a number. Default is None,
                which will assume the same cell dimension for y as is set for x.
            offset: A number for how far to offset the grid from the base face.
            flip: Set to True to have the mesh normals reversed from the direction of
                this face and to have the offset input move the mesh in the opposite
                direction from this face normal. Defaults to False, which means the
                normal direction of the face will be used as the direction of the
                sensor grids.
        """
        grids = []
        for i, faces in enumerate(face_arrays):
            grid_id = '{}_{}'.format(base_identifier, i)
            try:
                grids.append(
                    SensorGrid.from_face3d(grid_id, faces, x_dim, y_dim, offset, flip)
                )
            except AssertionError:  # none of the Face3Ds make a valid grid
                continue
        return grids

    @staticmethod
    def radial_positions_mesh(
            positions, dir_count=8, start_vector=Vector3D(0, -1, 0), mesh_radius=1):
        """Generate a Mesh3D resembling a circle around each position.

        Args:
            positions: A list of (x, y ,z) tuples for position of sensors.
            dir_count: A positive integer for the number of radial directions
                to be generated around each position. (Default: 8).
            start_vector: A Vector3D to set the start direction of the generated
                directions. (Default: (0, -1, 0)).
            mesh_radius: A number for the radius of the radial mesh to be
                generated around each sensor. (Default: 1).
        """
        # set up the start vector and rotation angles
        st_vec = Vector3D(start_vector.x, start_vector.y, 0).normalize()
        st_vec = st_vec * mesh_radius
        inc_ang = (math.pi * 2) / dir_count
        st_vec = st_vec.rotate_xy(-inc_ang / 2)
        # loop through the positions and angles to create the mesh
        verts, faces = [], []
        v_count = 0
        for pt in positions:
            st_pt = Point3D(*pt)
            nxt_pt = st_pt.move(st_vec)
            verts.extend([st_pt, nxt_pt])
            for i in range(dir_count - 1):
                new_pt = verts[-1].rotate_xy(inc_ang, st_pt)
                new_f = (v_count, v_count + i + 1, v_count + i + 2)
                verts.append(new_pt)
                faces.append(new_f)
            faces.append((v_count, v_count + dir_count, v_count + 1))
            v_count += (dir_count + 1)
        return Mesh3D(verts, faces)

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
        new_obj.group_identifier = self.group_identifier
        new_obj._light_path = self._light_path
        new_obj._mesh = self._mesh
        new_obj._base_geometry = self._base_geometry
        return new_obj

    def __key(self):
        """A tuple based on the object properties, useful for hashing."""
        return (
            self.identifier, self._display_name, self._room_identifier,
            self._room_identifier) + tuple(hash(sensor) for sensor in self.sensors)

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
