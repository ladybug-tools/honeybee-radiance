# coding=utf-8
u"""Create a Radiance view."""
from __future__ import division

from .lightpath import light_path_from_room

from honeybee_radiance_command.cutil import parse_radiance_options
from honeybee_radiance_command.options import TupleOption, \
    StringOptionJoined, NumericOption
import honeybee.typing as typing
import ladybug_geometry.geometry3d.pointvector as pv
from ladybug_geometry.geometry3d.plane import Plane
import ladybug.futil as futil

import math
import os


class View(object):
    u"""A Radiance view.

    Args:
        identifier: Text string for a unique View ID. Must not contain spaces
            or special characters. This will be used to identify the object across
            a model and in the exported Radiance files.
        position: Set the view position (-vp) to (x, y, z). This is the focal
            point of a perspective view or the center of a parallel projection.
            Default: (0, 0, 0)
        direction: Set the view direction (-vd) vector to (x, y, z). The
            length of this vector indicates the focal distance as needed by
            the pixel depth of field (-pd) in rpict. Default: (0, 0, 1)
        up_vector: Set the view up (-vu) vector (vertical direction) to
            (x, y, z) default: (0, 1, 0).
        type: A single character for the view type (-vt). Choose from the following.

            * v - Perspective
            * h - Hemispherical fisheye
            * l - Parallel
            * c - Cylindrical panorama
            * a - Angular fisheye
            * s - Planisphere [stereographic] projection

            For more detailed description about view types check rpict manual
            page: (http://radsite.lbl.gov/radiance/man_html/rpict.1.html)
        h_size: Set the view horizontal size (-vh). For a perspective
            projection (including fisheye views), val is the horizontal field
            of view (in degrees). For a parallel projection, val is the view
            width in world coordinates.
        v_size: Set the view vertical size (-vv). For a perspective
            projection (including fisheye views), val is the horizontal field
            of view (in degrees). For a parallel projection, val is the view
            width in world coordinates.
        shift: Set the view shift (-vs). This is the amount the actual
            image will be shifted to the right of the specified view. This
            option is useful for generating skewed perspectives or rendering
            an image a piece at a time. A value of 1 means that the rendered
            image starts just to the right of the normal view. A value of -1
            would be to the left. Larger or fractional values are permitted
            as well.
        lift: Set the view lift (-vl) to a value. This is the amount the
            actual image will be lifted up from the specified view.

    Properties:
        * identifier
        * display_name
        * position
        * direction
        * up_vector
        * type
        * h_size
        * v_size
        * shift
        * lift
        * room_identifier
        * light_path
        * group_identifier
        * full_identifier

    Usage:

    .. code-block:: python

        v = View()
        # add a fore clip
        v.fore_clip = 100
        print(v)

        > -vtv -vp 0.000 0.000 0.000 -vd 0.000 0.000 1.000 -vu 0.000 1.000
           0.000 -vh 60.000 -vv 60.000 -vo 100.000

        # split the view into a view grid
        gridViews = v.grid(2, 2, 600, 600)
        for g in gridViews:
            print(g)

        > -vtv -vp 0.000 0.000 0.000 -vd 0.000 0.000 1.000 -vu 0.000 1.000
           0.000 -vh 29.341 -vv 32.204  -vs -0.500 -vl -0.500 -vo 100.000

        > -vtv -vp 0.000 0.000 0.000 -vd 0.000 0.000 1.000 -vu 0.000 1.000
           0.000 -vh 29.341 -vv 32.204 -vs 0.500 -vl -0.500 -vo 100.000

        > -vtv -vp 0.000 0.000 0.000 -vd 0.000 0.000 1.000 -vu 0.000 1.000
           0.000 -vh 29.341 -vv 32.204 -vs -0.500 -vl 0.500 -vo 100.000

        > -vtv -vp 0.000 0.000 0.000 -vd 0.000 0.000 1.000 -vu 0.000 1.000
          0.000 -vh 29.341 -vv 32.204 -vs 0.500 -vl 0.500 -vo 100.000
    """

    __slots__ = ('_identifier', '_display_name', '_position', '_direction',
                 '_up_vector', '_h_size', '_v_size', '_shift', '_lift',
                 '_type', '_fore_clip', '_aft_clip', '_room_identifier',
                 '_light_path', '_group_identifier')

    def __init__(self, identifier, position=None, direction=None, up_vector=None,
                 type='v', h_size=60, v_size=60, shift=None, lift=None):
        u"""Create a view."""
        self.identifier = identifier
        self._display_name = None
        self._position = TupleOption(
            'vp', 'view position', position if position is not None else (0, 0, 0)
        )
        self._direction = TupleOption(
            'vd', 'view direction', direction if direction is not None else (0, 0, 1)
        )
        self._up_vector = TupleOption(
            'vu', 'view up vector', up_vector if up_vector is not None else (0, 1, 0)
        )
        self._h_size = NumericOption('vh', 'view horizontal size', h_size, min_value=0)
        self._v_size = NumericOption('vv', 'view vertical size', v_size, min_value=0)
        self._shift = NumericOption('vs', 'view shift', shift)
        self._lift = NumericOption('vl', 'view lift', lift)
        self._type = StringOptionJoined(
            'vt', 'view type', type, valid_values=['v', 'h', 'l', 'c', 'a', 's']
        )
        # set for_clip to None
        self._fore_clip = NumericOption('vo', 'view fore clip')
        self._aft_clip = NumericOption('va', 'view aft clip')

        self._room_identifier = None
        self._group_identifier = None
        self._light_path = None

    @property
    def identifier(self):
        """Get or set a text string for a unique View identifier."""
        return self._identifier

    @identifier.setter
    def identifier(self, n):
        self._identifier = typing.valid_rad_string(n, 'view identifier')

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
    def is_fisheye(self):
        """Check if the view type is one of the fisheye views."""
        return self.type in ('h', 'a', 's')

    @property
    def type(self):
        """Set and get view type (-vt) to one of the choices below.

            * v - Perspective (v)
            * h - Hemispherical fisheye (h)
            * l - Parallel (l)
            * c - Cylindrical panorama (c)
            * a - Angular fisheye (a)
            * s - Planisphere [stereographic] projection (s)
        """
        return self._type

    @property
    def vt(self):
        """View type as a string in radiance format."""
        return self._type.to_radiance()

    @type.setter
    def type(self, value):
        self._type.value = value[-1:]  # this will handle both vtv and v inputs

        # set view size to 180 degrees for fisheye views
        if self.type in ('h', 'a', 's'):
            if self.h_size != 180:
                self.h_size = 180
                print("Changed h_size to 180 for fisheye view type.")
            if self.v_size != 180:
                self.v_size = 180
                print("Changed v_size to 180 for fisheye view type.")

        elif self.type == 'v':
            assert self.h_size < 180, ValueError(
                '\n{} is an invalid horizontal view size for Perspective view.\n'
                'The size should be smaller than 180.'.format(self.h_size))
            assert self.v_size < 180, ValueError(
                '\n{} is an invalid vertical view size for Perspective view.\n'
                'The size should be smaller than 180.'.format(self.v_size))

    @property
    def position(self):
        """Set the view position (-vp) to (x, y, z).

        This is the focal point of a perspective view or the center of a parallel
        projection. Default: (0, 0, 0)
        """
        return self._position

    @property
    def vp(self):
        """View point / position as a string in radiance format."""
        return self._position.to_radiance()

    @position.setter
    def position(self, value):
        self._position.value = value

    @property
    def direction(self):
        """Set the view direction (-vd) vector to (x, y, z).

        The length of this vector indicates the focal distance as needed by
        the pixel depth of field (-pd) in rpict. Default: (0, 0, 1)
        """
        return self._direction

    @property
    def vd(self):
        """View direction as a string in radiance format."""
        return self._direction.to_radiance()

    @direction.setter
    def direction(self, value):
        self._direction.value = value

    @property
    def up_vector(self):
        """Set and get the view up (-vu) vector (vertical direction) to (x, y, z)

        Default: (0, 1, 0).
        """
        return self._up_vector

    @property
    def vu(self):
        """View up as a string in radiance format."""
        return self._up_vector.to_radiance()

    @up_vector.setter
    def up_vector(self, value):
        self._up_vector.value = value

    @property
    def h_size(self):
        """Set the view horizontal size (-vh).

        For a perspective projection (including fisheye views), val is the horizontal
        field of view (in degrees). For a parallel projection, val is the view
        width in world coordinates.
        """
        return self._h_size

    @property
    def vh(self):
        """View horizontal size as a string in radiance format."""
        return self._h_size.to_radiance()

    @h_size.setter
    def h_size(self, value):
        self._h_size.value = value if value is not None else 60

    @property
    def v_size(self):
        """Set the view vertical size (-vv).

        For a perspective projection (including fisheye views), val is the horizontal
        field of view (in degrees). For a parallel projection, val is the view width in
        world coordinates.
        """
        return self._v_size

    @property
    def vv(self):
        """View vertical size as a string in radiance format."""
        return self.v_size.to_radiance()

    @v_size.setter
    def v_size(self, value):
        self._v_size.value = value if value is not None else 60

    @property
    def shift(self):
        """Set the view shift (-vs).

        This is the amount the actual image will be shifted to the right of the specified
        view. This option is useful for generating skewed perspectives or rendering an
        image a piece at a time. A value of 1 means that the rendered image starts just
        to the right of the normal view. A value of -1 would be to the left. Larger or
        fractional values are permitted as well.
        """
        return self._shift

    @property
    def vs(self):
        """View shift as a string in radiance format."""
        return self._shift.to_radiance()

    @shift.setter
    def shift(self, value):
        self._shift.value = value

    @property
    def lift(self):
        """Set the view lift (-vl) to a value.

        This is the amount the actual image will be lifted up from the specified view.
        """
        return self._lift

    @property
    def vl(self):
        """View lift as a string in radiance format."""
        return self.lift.to_radiance()

    @lift.setter
    def lift(self, value):
        self._lift.value = value

    @property
    def fore_clip(self):
        """View fore clip (-vo) at a distance from the view point.

        The plane will be perpendicular to the view direction for perspective
        and parallel view types. For fisheye view types, the clipping plane is
        actually a clipping sphere, centered on the view point with radius val.
        Objects in front of this imaginary surface will not be visible. This may
        be useful for seeing through walls (to get a longer perspective from an
        exterior view point) or for incremental rendering. A value of zero implies
        no foreground clipping. A negative value produces some interesting effects,
        since it creates an inverted image for objects behind the viewpoint.
        """
        return self._fore_clip

    @property
    def vo(self):
        """View fore clip as a string in radiance format."""
        return self._fore_clip.to_radiance()

    @fore_clip.setter
    def fore_clip(self, distance):
        self._fore_clip.value = distance

    @property
    def aft_clip(self):
        """View aft clip (-va) at a distance from the view point.

        Set the view aft clipping plane at a distance of val from the view point. Like
        the view fore plane, it will be perpendicular to the view direction for
        perspective and parallel view types. For fisheye view types, the clipping plane
        is actually a clipping sphere, centered on the view point with radius val.
        Objects behind this imaginary surface will not be visible. A value of zero means
        no aft clipping, and is the only way to see infinitely distant objects such as
        the sky.
        """
        return self._aft_clip

    @property
    def va(self):
        """View aft clip as a string in radiance format."""
        return self._aft_clip.to_radiance()

    @aft_clip.setter
    def aft_clip(self, distance):
        self._aft_clip.value = distance

    @property
    def room_identifier(self):
        """Get or set text for the Room identifier to which this View belongs.

        This will be used in the info_dict method to narrow down the
        number of aperture groups that have to be run with this view. If None,
        the view will be run with all aperture groups in the model.
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

        You may use / in name to identify nested view groups. For example
        floor_1/living_room create a view under living_room/floor_1 subfolder.

        If None, the view will be written to the root of grids folder.
        """
        return self._group_identifier

    @group_identifier.setter
    def group_identifier(self, identifier_key):
        if identifier_key is not None:
            identifier_key = \
                '/'.join(
                    typing.valid_rad_string(key, 'view group identifier')
                    for key in identifier_key.split('/')
                )
        self._group_identifier = identifier_key

    @property
    def full_identifier(self):
        """Get full identifier for view.

        For a view with group identifier it will be group_identifier/identifier
        """
        return self.identifier if not self.group_identifier \
            else '%s/%s' % (self.group_identifier, self.identifier)

    @property
    def light_path(self):
        """Get or set list of lists for the light path from the view to the sky.

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

    @classmethod
    def from_dict(cls, view_dict):
        """Create a view from a dictionary in the following format.

        .. code-block:: python

            {
            'type': 'View',
            'identifier': str,  # View identifier
            "display_name": str,  # View display name
            'position': [],  # list with position value
            'direction': [],  # list with direction value
            'up_vector': [],  # list with up_vector value
            'h_size': number,  # h_size.value
            'v_size': number,  # v_size value
            'shift': number,  # shift value
            'lift': number,  # lift value
            'view_type': number,  # view_type value
            'fore_clip': number,  # fore_clip value
            'aft_clip': number,  # aft_clip value
            'room_identifier': str,  # optional room identifier
            'light_path':  []  # optional list of lists for light path
            }
        """
        assert view_dict['type'] == 'View', \
            'Expected View dictionary. Got {}.'.format(view_dict['type'])

        view = cls(
            identifier=view_dict['identifier'],
            position=view_dict['position'],
            direction=view_dict['direction'],
            up_vector=view_dict['up_vector'],
            h_size=view_dict['h_size'],
            v_size=view_dict['v_size'],
            shift=view_dict['shift'],
            lift=view_dict['lift'],
        )

        if 'view_type' in view_dict:
            view.type = view_dict['view_type']
        if 'fore_clip' in view_dict:
            view.fore_clip = view_dict['fore_clip']
        if 'aft_clip' in view_dict:
            view.aft_clip = view_dict['aft_clip']
        if 'display_name' in view_dict and view_dict['display_name'] is not None:
            view.display_name = view_dict['display_name']
        if 'room_identifier' in view_dict and view_dict['room_identifier'] is not None:
            view.room_identifier = view_dict['room_identifier']
        if 'light_path' in view_dict and view_dict['light_path'] is not None:
            view.light_path = view_dict['light_path']
        if 'group_identifier' in view_dict and view_dict['group_identifier'] is not None:
            view_dict.group_identifier = view_dict['group_identifier']
        return view

    @classmethod
    def from_string(cls, identifier, view_string):
        """Create a view object from a string.

        This method is similar to from_string method for radiance parameters with the
        difference that all the parameters that are not related to view will be ignored.
        """
        mapper = {
            'identifier': identifier, 'vp': 'position', 'vd': 'direction',
            'vu': 'up_vector', 'vh': 'h_size', 'vv': 'v_size', 'vs': 'shift',
            'vl': 'lift', 'vo': 'fore_clip', 'va': 'aft_clip'
        }

        base = {
            'type': 'View',
            'identifier': identifier,
            'position': None,
            'direction': None,
            'up_vector': None,
            'h_size': None,
            'v_size': None,
            'shift': None,
            'lift': None,
            'view_type': None,
            'fore_clip': None,
            'aft_clip': None
        }

        # parse the string here
        options = parse_radiance_options(view_string)

        for opt, value in options.items():
            if opt in mapper:
                base[mapper[opt]] = value
            elif opt[:2] == 'vt':
                base['view_type'] = opt
            else:
                print('%s is not a view parameter and is ignored.' % opt)

        return cls.from_dict(base)

    @classmethod
    def from_file(cls, file_path, identifier=None):
        """Create view from a view file.

        Args:
            file_path: Full path to view file.
            identifier: Optional ext string for a unique View ID. Must not contain spaces
                or special characters. This will be used to identify the object across
                a model and in the exported Radiance files. If None, this will be set
                to file name. (Default: None)
        """

        if not os.path.isfile(file_path):
            raise IOError("Can't find {}.".format(file_path))
        identifier = identifier or os.path.split(os.path.splitext(file_path)[0])[-1]

        with open(file_path, 'r') as input_data:
            view_string = str(input_data.read()).rstrip()

        assert view_string[:3] == 'rvu', \
            'View file must start with rvu not %s' % view_string[:3]
        return cls.from_string(identifier, view_string)

    def dimension(self, x_res=None, y_res=None):
        """Get dimensions for this view as '-x %d -y %d [-ld-]'.

        This method is same as vwrays -d. Default values for x_res and y_res are set to
        match Radiance defaults.
        """
        x, y = self.dimension_x_y(x_res, y_res)
        return '-x %d -y %d -ld%s' % (
            x, y,
            '-' if (self.fore_clip.to_radiance() + self.aft_clip.to_radiance() == '')
            else '+'
        )

    def dimension_x_y(self, x_res=None, y_res=None):
        """Get dimensions for this view as x, y.

        Default values for x_res and y_res are set to match Radiance defaults.
        """
        # radiance default is 512
        x_res = int(x_res) if x_res is not None else 512
        y_res = int(y_res) if y_res is not None else 512

        if self.is_fisheye:
            return min(x_res, y_res), min(x_res, y_res)

        vh = self.h_size.value
        vv = self.v_size.value

        if self.type == 'v':
            hv_ratio = math.tan(math.radians(vh) / 2.0) / \
                math.tan(math.radians(vv) / 2.0)
        else:
            hv_ratio = vh / vv

        # radiance keeps the largest max size and tries to scale the other size
        # to fit the aspect ratio. In case the size doesn't match it reverses
        # the process.
        if y_res <= x_res:
            new_x = int(round(hv_ratio * y_res))
            if new_x <= x_res:
                return new_x, y_res
            else:
                new_y = int(round(x_res / hv_ratio))
                return x_res, new_y
        else:
            new_y = int(round(x_res / hv_ratio))
            if new_y <= y_res:
                return x_res, new_y
            else:
                new_x = int(round(hv_ratio * y_res))
                return new_x, y_res

    def grid(self, x_div_count=1, y_div_count=1):
        """Break-down the view into a grid of views based on x and y grid count.

        Views will be returned row by row from right to left.

        Args:
            x_div_count: Set number of divisions in x direction (Default: 1).
            y_div_count: Set number of divisions in y direction (Default: 1).

        Returns:
            A tuple of views. Views are sorted row by row from right to left.
        """
        PI = math.pi
        try:
            x_div_count = abs(x_div_count)
            y_div_count = abs(y_div_count)
        except TypeError as e:
            raise ValueError("Division count should be a number.\n%s" % str(e))

        assert x_div_count * y_div_count != 0, "Division count should be larger than 0."

        if x_div_count == y_div_count == 1:
            return [self]

        _views = list(range(x_div_count * y_div_count))

        if self.type == 'l':
            # parallel view (vtl)
            _vh = self.h_size / x_div_count
            _vv = self.v_size / y_div_count

        elif self.type == 'v':
            # perspective (vtv)
            _vh = (2. * 180. / PI) * \
                math.atan(((PI / 180. / 2.) * self.h_size) / x_div_count)
            _vv = (2. * 180. / PI) * \
                math.atan(math.tan((PI / 180. / 2.) * self.v_size) / y_div_count)

        elif self.is_fisheye:
            # fish eye
            _vh = (2. * 180. / PI) * \
                math.asin(math.sin((PI / 180. / 2.) * self.h_size) / x_div_count)
            _vv = (2. * 180. / PI) * \
                math.asin(math.sin((PI / 180. / 2.) * self.v_size) / y_div_count)

        else:
            print("Grid views are not supported for %s." % self.type.to_radiance())
            return [self]

        # create a set of new views
        for view_count in range(len(_views)):
            # calculate view shift and view lift
            if x_div_count == 1:
                _vs = 0
            else:
                _vs = (((view_count % x_div_count) / (x_div_count - 1)) - 0.5) \
                    * (x_div_count - 1)

            if y_div_count == 1:
                _vl = 0
            else:
                _vl = ((int(view_count / y_div_count) / (y_div_count - 1)) - 0.5) \
                    * (y_div_count - 1)

            # create a copy from the current copy
            _n_view = View('%s_%d' % (self.identifier, view_count))

            # update parameters
            _n_view.h_size = _vh
            _n_view.v_size = _vv
            _n_view.shift = _vs
            _n_view.lift = _vl
            _n_view._fore_clip = self._fore_clip
            _n_view._aft_clip = self._aft_clip
            _n_view._room_identifier = self._room_identifier
            _n_view._light_path = self._light_path
            try:
                _n_view.display_name = '%s_%d' % (self.display_name, view_count)
            except UnicodeEncodeError:  # character no found on machine
                pass

            # add the new view to views list
            _views[view_count] = _n_view

        return _views

    def to_radiance(self):
        """Return full Radiance definition as a string."""
        # create base information of view
        view_options = ' '.join((
            self.vt, self.vp, self.vd, self.vu,
            self.vh, self.vv, self.vs, self.vl,
            self.vo, self.va
        ))

        return ' '.join(view_options.split())  # remove white spaces

    def info_dict(self, model=None):
        """Get a dictionary with information about the View.

        This can be written as a JSON into a model radiance folder to narrow
        down the number of aperture groups that have to be run with this view.

        Args:
            model: A honeybee Model object which will be used to identify
                the aperture groups that will be run with this view. Default: None.
        """
        base = {}
        if self._light_path:
            base['light_path'] = self._light_path
        elif model and self._room_identifier:  # auto-calculate the light path
            base['light_path'] = light_path_from_room(model, self._room_identifier)

        if self._group_identifier:
            base['group_identifier'] = self._group_identifier

        return base

    def to_dict(self):
        """Translate view to a dictionary."""
        base = {
            'type': 'View',
            'identifier': self.identifier,
            'position': self.position.value,
            'direction': self.direction.value,
            'up_vector': self.up_vector.value,
            'h_size': self.h_size.value,
            'v_size': self.v_size.value,
            'shift': self.shift.value,
            'lift': self.lift.value,
            'view_type': self.type.value,
            'fore_clip': self.fore_clip.value,
            'aft_clip': self.aft_clip.value
        }
        if self._display_name is not None:
            base['display_name'] = self.display_name
        if self._room_identifier is not None:
            base['room_identifier'] = self.room_identifier
        if self._light_path is not None:
            base['light_path'] = self.light_path
        if self._group_identifier is not None:
            base['group_identifier'] = self.group_identifier
        return base

    def to_file(self, folder, file_name=None, mkdir=False):
        """Save view to a file.

        Args:
            folder: Target folder.
            file_name: Optional file name without extension (Default: self.identifier).
            mkdir: A boolean to indicate if the folder should be created in case it
                doesn't exist already (Default: False).

        Returns:
            Full path to newly created file.
        """

        identifier = file_name or self.identifier + '.vf'
        # add rvu before the view itself
        content = 'rvu ' + self.to_radiance()
        return futil.write_to_file_by_name(folder, identifier, content, mkdir)

    def move(self, moving_vec):
        """Move this view along a vector.

        Args:
            moving_vec: A ladybug_geometry Vector3D with the direction and distance
                to move the view.
        """
        position = pv.Point3D(*self.position)
        self.position = tuple(position.move(moving_vec))

    def rotate(self, angle, axis=None, origin=None):
        """Rotate this view by a certain angle around an axis and origin.

        Args:
            angle: An angle for rotation in degrees.
            axis: Rotation axis as a Vector3D. If None, self.up_vector will be
                used. (Default: None).
            origin: A ladybug_geometry Point3D for the origin around which the
                object will be rotated. If None, self.position is used. (Default: None).
        """
        view_up_vector = pv.Vector3D(*self.up_vector)
        view_position = pv.Point3D(*self.position)
        view_direction = pv.Vector3D(*self.direction)
        view_plane = Plane(n=view_up_vector, o=view_position, x=view_direction)
        axis = axis if axis is not None else view_up_vector
        position = origin if origin is not None else view_position

        rotated_plane = view_plane.rotate(axis, math.radians(angle), position)
        self._apply_plane_properties(rotated_plane, view_direction, view_up_vector)

    def rotate_xy(self, angle, origin=None):
        """Rotate this view counterclockwise in the world XY plane by a certain angle.

        Args:
            angle: An angle in degrees.
            origin: A ladybug_geometry Point3D for the origin around which the
                object will be rotated. If None, self.position is used. (Default: None).
        """
        view_up_vector = pv.Vector3D(*self.up_vector)
        view_position = pv.Point3D(*self.position)
        view_direction = pv.Vector3D(*self.direction)
        view_plane = Plane(n=view_up_vector, o=view_position, x=view_direction)
        position = origin if origin is not None else view_position

        rotated_plane = view_plane.rotate_xy(math.radians(angle), position)
        self._apply_plane_properties(rotated_plane, view_direction, view_up_vector)

    def reflect(self, plane):
        """Reflect this view across a plane.

        Args:
            plane: A ladybug_geometry Plane across which the object will
                be reflected.
        """
        view_up_vector = pv.Vector3D(*self.up_vector)
        view_position = pv.Point3D(*self.position)
        view_direction = pv.Vector3D(*self.direction)
        view_plane = Plane(n=view_up_vector, o=view_position, x=view_direction)

        ref_plane = view_plane.reflect(plane.n, plane.o)
        self._apply_plane_properties(ref_plane, view_direction, view_up_vector)

    def scale(self, factor, origin=None):
        """Scale this view by a factor from an origin point.

        Args:
            factor: A number representing how much the object should be scaled.
            origin: A ladybug_geometry Point3D representing the origin from which
                to scale. If None, it will be scaled from the World origin (0, 0, 0).
        """
        view_position = pv.Point3D(*self.position)
        self.position = view_position.scale(factor, origin)
        self.direction = pv.Vector3D(*self.direction) * factor
        self.up_vector = pv.Vector3D(*self.up_vector) * factor

    def _apply_plane_properties(self, plane, view_direction, view_up_vector):
        """Re-set the position, direction and up_vector from a Plane.

        This method also ensures that the magnitude of the vectors is unchanged
        (since all Plane objects will have unitized vectors).
        """
        self.position = plane.o
        self.direction = plane.x * view_direction.magnitude
        self.up_vector = plane.n * view_up_vector.magnitude

    def duplicate(self):
        """Get a copy of this object."""
        return self.__copy__()

    def __copy__(self):
        new_obj = View(
            self.identifier, position=self.position, direction=self.direction,
            up_vector=self.up_vector, type=self.type, h_size=self.h_size,
            v_size=self.v_size, shift=self.shift, lift=self.lift)
        new_obj._display_name = self._display_name
        new_obj._room_identifier = self._room_identifier
        new_obj._light_path = self._light_path
        return new_obj

    def ToString(self):
        """Overwrite .NET ToString."""
        return self.__repr__()

    def __key(self):
        """A tuple based on the object properties, useful for hashing."""
        return (self.identifier, hash(self.position.value), hash(self.direction.value),
                hash(self.up_vector.value), self.type.value, self.h_size.value,
                self.v_size.value, self.shift.value, self.lift.value, self._display_name,
                self._room_identifier)

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        return isinstance(other, View) and self.__key() == other.__key() and \
            self.light_path == other.light_path

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        """View representation."""
        return self.to_radiance()
