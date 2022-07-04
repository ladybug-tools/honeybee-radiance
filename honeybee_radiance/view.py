# coding=utf-8
u"""Create a Radiance view."""
from __future__ import division

from .lightpath import light_path_from_room

from honeybee_radiance_command.options import TupleOption, \
    StringOptionJoined, NumericOption
import honeybee.typing as typing
import ladybug_geometry.geometry3d.pointvector as pv
from ladybug_geometry.geometry3d.plane import Plane
import ladybug.futil as futil

import math
import os
import re
import collections


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
        self._check_size_and_type()

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
        return self._type.value

    @property
    def vt(self):
        """View type as a string in radiance format."""
        return self._type.to_radiance()

    @type.setter
    def type(self, value):
        self._type.value = value[-1:]  # this will handle both vtv and v inputs
        self._check_size_and_type()

    @property
    def position(self):
        """Set the view position (-vp) to (x, y, z).

        This is the focal point of a perspective view or the center of a parallel
        projection. Default: (0, 0, 0)
        """
        return self._position.value

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
        return self._direction.value

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
        return self._up_vector.value

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

        For a perspective projection (including fisheye views), this is the horizontal
        field of view (in degrees). For a parallel projection, this is the view
        width in world coordinates.
        """
        return self._h_size.value

    @property
    def vh(self):
        """View horizontal size as a string in radiance format."""
        return self._h_size.to_radiance()

    @h_size.setter
    def h_size(self, value):
        self._h_size.value = value if value is not None else 60
        self._check_size_and_type()

    @property
    def v_size(self):
        """Set the view vertical size (-vv).

        For a perspective projection (including fisheye views), this is the horizontal
        field of view (in degrees). For a parallel projection, this is the view width in
        world coordinates.
        """
        return self._v_size.value

    @property
    def vv(self):
        """View vertical size as a string in radiance format."""
        return self._v_size.to_radiance()

    @v_size.setter
    def v_size(self, value):
        self._v_size.value = value if value is not None else 60
        self._check_size_and_type()

    @property
    def shift(self):
        """Set the view shift (-vs).

        This is the amount the actual image will be shifted to the right of the specified
        view. This option is useful for generating skewed perspectives or rendering an
        image a piece at a time. A value of 1 means that the rendered image starts just
        to the right of the normal view. A value of -1 would be to the left. Larger or
        fractional values are permitted as well.
        """
        return self._shift.value

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
        return self._lift.value

    @property
    def vl(self):
        """View lift as a string in radiance format."""
        return self._lift.to_radiance()

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
        return self._fore_clip.value

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
        return self._aft_clip.value

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
        passes. (eg. [['SouthWindow1'], ['__static_apertures__', 'NorthWindow2']]).
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

    def standardize_fisheye(self):
        """Automatically set view size to 180 degrees if the view type is a fisheye.

        Alternatively it sets the view size to 360 degrees if both the view type is
        angular fisheye and either the horizontal or vertical view size is 360 degrees.
        """
        if self.type in ('h', 's'):
            if self.h_size != 180:
                self.h_size = 180
            if self.v_size != 180:
                self.v_size = 180
        if self.type in ('a'):
            if self.h_size == 360 or self.v_size == 360:
                self.h_size = self.v_size = 360
            else:
                if self.h_size != 180:
                    self.h_size = 180
                if self.v_size != 180:
                    self.v_size = 180

    def _check_size_and_type(self):
        """Check to be sure the view size and type are compatible."""
        if self.type == 'v':
            assert self.h_size < 180, \
                '\n{} is an invalid horizontal view size for Perspective view.\n' \
                'The size should be smaller than 180.'.format(self.h_size)
            assert self.v_size < 180, \
                '\n{} is an invalid vertical view size for Perspective view.\n' \
                'The size should be smaller than 180.'.format(self.v_size)

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

        view_type = view_dict['view_type'][-1:] if 'view_type' in view_dict else 'v'
        view = cls(
            identifier=view_dict['identifier'],
            position=view_dict['position'],
            direction=view_dict['direction'],
            up_vector=view_dict['up_vector'],
            type=view_type,
            h_size=view_dict['h_size'],
            v_size=view_dict['v_size'],
            shift=view_dict['shift'],
            lift=view_dict['lift'],
        )

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
        options = cls._parse_radiance_options(view_string)

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

    @classmethod
    def from_grid(cls, grid, identifier='from_grid'):
        """Create view from a grid of views.
        Generally the grid argument should be the views generated by the grid method.
        Args:
            grid: A list of subviews. If only a single view is given, this view will be
                returned. The views can be either class instances of View, strings or
                .unf files. If strings are used, the views will be created by the
                from_string method. If .unf files are used, the views will be created by
                the from_string method using the view found in the Radiance header.
            identifier: Text string for a unique View ID. Must not contain spaces
                or special characters. This will be used to identify the object across
                a model and in the exported Radiance files. If None, this will be set
                to 'from_grid'. (Default: 'from_grid')
        """
        if not isinstance(grid, (list, tuple)):
            grid = [grid]

        views = []
        # check if grid argument views are valid
        for c, view in enumerate(grid):
            if isinstance(view, View):
                views.append(view)
            elif view.endswith('.unf'):
                try:
                    f = open(view, 'r', encoding='utf-8', errors='ignore')
                except Exception:
                    f = open(view, 'r')
                try:
                    for line in f:
                        if not line.strip():
                            break
                        else:
                            low_line = line.strip().lower()
                            if low_line.startswith('view='):
                                print(low_line)
                                views.append(cls.from_string('view_%04d' % c, low_line))
                except Exception:
                    raise ValueError('Failed to find view in Radiance header.')
                finally:
                    f.close()
            elif isinstance(view, str):
                views.append(cls.from_string('view_%04d' % c, view))
            else:
                raise ValueError(
                    'Expected Honeybee Radiance View, string or .unf file.'
                    'Got: {}'.format(type(view))
                )

        # if only a single (valid) view is given, then return the view
        if len(views) == 1:
            return views[0]

        _type = set()
        _view_point = set()
        _view_direction = set()
        _up_direction = set()
        _vh = set()
        _vv = set()
        _x_div_count = set()
        _y_div_count = set()
        # check if type, view point, view direction, and up direction are equal in views
        # all unique values are collected, all except -vh and -vv must be the same
        for _view in views:
            _type.add(_view.type)
            _view_point.add(_view.position)
            _view_direction.add(_view.direction)
            _up_direction.add(_view.up_vector)
            _vh.add(_view.h_size)
            _vv.add(_view.v_size)
            _x_div_count.add(_view.shift)
            _y_div_count.add(_view.lift)

        if len(_type) > 1:
            raise ValueError('All subviews must have the same view type.')
        if len(_view_point) > 1:
            raise ValueError('All subviews must have the same view point.')
        if len(_view_direction) > 1:
            raise ValueError('All subviews must have the same view direction.')
        if len(_up_direction) > 1:
            raise ValueError('All subviews must have the same up direction.')
        if len(_vh) > 1:
            raise ValueError('All subviews must have the same horizontal view size.')
        if len(_vv) > 1:
            raise ValueError('All subviews must have the same vertical view size.')

        # find the grid dimensions (x_count, y_count)
        x_div_count = len(_x_div_count)
        y_div_count = len(_y_div_count)

        # get the horizontal and vertical view size from the subviews
        _vh = list(_vh)[0]
        _vv = list(_vv)[0]

        # create instance of view
        view = cls(
            identifier=identifier,
            position=list(_view_point)[0],
            direction=list(_view_direction)[0],
            up_vector=list(_up_direction)[0],
            type=list(_type)[0])

        PI = math.pi
        # find the horizontal and vertical size
        if view.type == 'l' or view.type == 'a':
            # parallel view (vtl) or angular fisheye (vta)
            h_size = _vh * x_div_count
            v_size = _vv * y_div_count

        elif view.type == 'v':
            # perspective (vtv)
            pi2 = (2. * 180. / PI)
            h_size = pi2 * math.tan(_vh / (2. * 180. / PI)) * x_div_count
            v_size = pi2 * math.atan(math.tan(_vv / (2. * 180. / PI)) * y_div_count)

        elif view.type == 'h':
            # hemispherical fisheye (vth)
            pi2 = (2. * 180. / PI)
            h_size = pi2 * math.asin(math.sin(_vh / (2. * 180. / PI)) * x_div_count)
            v_size = pi2 * math.asin(math.sin(_vv / (2. * 180. / PI)) * y_div_count)

        else:
            raise ValueError(
                'Grid views are not supported for %s.' % view.type)

        # round the number to avoid cases like 59.99999999999999 when should be 60
        h_size = round(h_size, 10)
        v_size = round(v_size, 10)

        # update horizontal and vertical view size
        view.h_size = h_size
        view.v_size = v_size

        return view

    def dimension(self, x_res=None, y_res=None):
        """Get dimensions for this view as '-x %d -y %d [-ld-]'.

        This method is same as vwrays -d. Default values for x_res and y_res are set to
        match Radiance defaults.
        """
        x, y = self.dimension_x_y(x_res, y_res)
        return '-x %d -y %d -ld%s' % (x, y, '-' if (self.vo + self.va == '') else '+')

    def dimension_x_y(self, x_res=None, y_res=None):
        """Get dimensions for this view as x, y.

        Default values for x_res and y_res are set to match Radiance defaults.
        """
        # radiance default is 512
        x_res = int(x_res) if x_res is not None else 512
        y_res = int(y_res) if y_res is not None else 512

        if self.is_fisheye:
            return min(x_res, y_res), min(x_res, y_res)

        vh = self.h_size
        vv = self.v_size

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

        if self.type in ('l', 'a', 'c'):
            # parallel view (vtl) or angular fisheye (vta)
            _vh = self.h_size / x_div_count
            _vv = self.v_size / y_div_count

        elif self.type == 'v':
            # perspective (vtv)
            pi2 = (2. * 180. / PI)
            _vh = pi2 * math.atan(((PI / 180. / 2.) * self.h_size) / x_div_count)
            _vv = pi2 * math.atan(math.tan((PI / 180. / 2.) * self.v_size) / y_div_count)

        elif self.type == 's':
            # planisphere (stereographic)
            pi2 = (2. * 180. / PI * 2)
            _vh = pi2 * math.atan(math.sin((PI / 180. / 2.) * self.h_size) / x_div_count)
            _vv = pi2 * math.atan(math.sin((PI / 180. / 2.) * self.v_size) / y_div_count)

        elif self.type in ('h'):
            # hemispherical fish eye
            pi2 = (2. * 180. / PI)
            _vh = pi2 * math.asin(math.sin((PI / 180. / 2.) * self.h_size) / x_div_count)
            _vv = pi2 * math.asin(math.sin((PI / 180. / 2.) * self.v_size) / y_div_count)

        else:
            print("Grid views are not supported for %s." % self.type)
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
                _vl = ((int(view_count % y_div_count) / (y_div_count - 1)) - 0.5) \
                    * (y_div_count - 1)

            # create a copy from the current view
            _n_view = self.duplicate()
            _n_view.identifier = '%s_%d' % (self.identifier, view_count)
            # update parameters
            _n_view.h_size = _vh
            _n_view.v_size = _vv
            _n_view.shift = _vs
            _n_view.lift = _vl
            _n_view._fore_clip = self._fore_clip
            _n_view._aft_clip = self._aft_clip
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
            'position': self.position,
            'direction': self.direction,
            'up_vector': self.up_vector,
            'h_size': self.h_size,
            'v_size': self.v_size,
            'shift': self.shift,
            'lift': self.lift,
            'view_type': self.type,
            'fore_clip': self.fore_clip,
            'aft_clip': self.aft_clip
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
        if not (identifier.endswith('.vf') or identifier.endswith('.unf')):
            identifier += '.vf'
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

    @staticmethod
    def _parse_radiance_options(string):
        """Parse a radiance option string (e.g. '-ab 4 -ad 256').

        The string should start with a '-' otherwise it will be trimmed to the
        first '-' in the string.
        """
        try:
            index = string.index('-')
        except ValueError:
            if not ' '.join(string.split()).replace('"', '').replace("'", '').strip():
                return {}
            raise ValueError(
                'Invalid Radiance options string input. '
                'Failed to find - in input string.'
            )

        _rad_opt_pattern = r'-[a-zA-Z]+'
        _rad_opt_compiled_pattern = re.compile(_rad_opt_pattern)
        sub_string = ' '.join(string[index:].split())
        value = re.split(_rad_opt_compiled_pattern, sub_string)[1:]
        key = re.findall(_rad_opt_pattern, sub_string)

        options = collections.OrderedDict()
        for k, v in zip(key, value):
            values = v.split()
            count = len(values)
            if count == 0:
                values = ''
            elif count == 1:
                values = values[0]
            options[k[1:]] = values

        return options

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
        return (self.identifier, hash(self.position), hash(self.direction),
                hash(self.up_vector), self.type, self.h_size,
                self.v_size, self.shift, self.lift, self._display_name,
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
