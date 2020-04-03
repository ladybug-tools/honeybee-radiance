"""A grid of sensors."""
from __future__ import division
import ladybug.futil as futil
import honeybee.typing as typing
from .sensor import Sensor

import os
try:
    from itertools import izip as zip
except:
    # python 3
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
    """

    __slots__ = ('_identifier', '_display_name', '_sensors')

    def __init__(self, identifier, sensors):
        """Initialize a SensorGrid."""
        self.identifier = typing.valid_rad_string(identifier)
        self._display_name = None
        self._sensors = tuple(sensors)
        for sen in self._sensors:
            if not isinstance(sen, Sensor):
                raise ValueError(
                    'Sensors in SensorGrid must be form type Sensor not %s' % type(sen)
                )

    @classmethod
    def from_dict(cls, ag_dict):
        """Create a sensor grid from a dictionary in the following format.

        .. code-block:: python

            {
            "identifier": str,  # SensorGrid identifier
            "display_name": str,  # SensorGrid display name
            "sensors": []  # list of Sensor dictionaries
            }
        """
        sensors = (Sensor.from_dict(sensor) for sensor in ag_dict['sensors'])
        new_obj = cls(identifier=ag_dict["identifier"], sensors=sensors)
        if 'display_name' in ag_dict and ag_dict['display_name'] is not None:
            new_obj.display_name = ag_dict['display_name']
        return new_obj

    @classmethod
    def from_planar_grid(cls, identifier, positions, plane_normal):
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
    def from_file(cls, file_path, start_line=None, end_line=None, identifier=None):
        """Create a sensor grid from a sensors file.

        The sensors must be structured as

        x1, y1, z1, dx1, dy1, dz1
        x2, y2, z2, dx2, dy2, dz2
        ...

        The lines that starts with # will be considred as commented lines and won't be
        loaded. These lines will be considered in line count for start_line and end_line.

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
                line = next(inf)

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
        self._identifier = typing.valid_rad_string(n)

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
    def positions(self):
        """A generator of sensor positions as x, y, z."""
        return (ap.position for ap in self.sensors)

    @property
    def directions(self):
        """A generator of sensor directions as x, y , z."""
        return (ap.direction for ap in self.sensors)

    @property
    def sensors(self):
        """Return a list of sensors."""
        return self._sensors

    @property
    def count(self):
        """Number of sensors."""
        return len(self._sensors)

    def duplicate(self):
        """Duplicate SensorGrid."""
        return SensorGrid(self.identifier, (sen.duplicate() for sen in self.sensors))

    def to_radiance(self):
        """Return sensors grid as a Radiance string."""
        return "\n".join((ap.to_radiance() for ap in self._sensors))

    def to_file(self, folder, file_name=None, mkdir=False):
        """Write this sensor grid to a Radiance sensors file.

        Args:
            folder: Target folder.
            file_name: Optional file name without extension. (Default: self.identifier)
            mkdir: A boolean to indicate if the folder should be created in case it
                doesn't exist already (Default: False).

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
            base_name: Optional text for a unique base_name for sensor files.
                (Default: self.identifier)
            mkdir: A boolean to indicate if the folder should be created in case it
                doesn't exist already (Default: False).

        Returns:
            A list of dicts containing the grid name, path to the grid and full path
            to the grid.
        """
        count = typing.int_in_range(count, 1, input_name='file count')
        base_name = base_name or self.identifier
        if count == 1 or self.count == 0:
            full_path = self.to_file(folder, base_name, mkdir)
            return [{
                'name': base_name if not self.identifier.endswith('.pts') \
                    else self.identifier.replace('.pts', ''),
                'path': self.identifier + '.pts' if not self.identifier.endswith('.pts') \
                    else self.identifier,
                'full_path': full_path,
                'count': self.count
            }]
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

    def ToString(self):
        """Overwrite ToString .NET method."""
        return self.__repr__()

    def to_dict(self):
        """Convert SensorGrid to a dictionary."""
        base = {
            "identifier": self.identifier,
            "sensors": [sen.to_dict() for sen in self.sensors]
        }
        if self._display_name is not None:
            base['display_name'] = self.display_name
        return base

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
        new_obj = SensorGrid(self.identifier, self.sensors)
        new_obj._display_name = self._display_name
        return new_obj

    def __eq__(self, value):
        if not isinstance(value, SensorGrid) or len(value) != len(self):
            return False
        if self.identifier != value.identifier:
            return False
        if self.sensors != value.sensors:
            return False
        return True

    def __ne__(self, value):
        return not self.__eq__(value)

    def __iter__(self):
        """Sensors iterator."""
        return iter(self.sensors)

    def __str__(self):
        """String repr."""
        return self.to_radiance()

    def __repr__(self):
        """Return sensors and directions."""
        return 'SensorGrid::{}::#{}'.format(self._identifier, len(self.sensors))
