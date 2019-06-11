# coding=utf-8
u"""Create a Radiance view."""
from __future__ import division
import honeybee_radiance.typing as typing
import honeybee_radiance.parser as parser
import math
import os
from copy import deepcopy
import ladybug_geometry.geometry3d.pointvector as pv
import ladybug_geometry.geometry3d.plane as plane
import ladybug.futil as futil


# TODO: Add support for move, rotate, etc.
class View(object):
    u"""A Radiance view.

    Usage:

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
           0.000 -vh 29.341 -vv 32.204 -x 300 -y 300 -vs -0.500 -vl -0.500
           -vo 100.000

        > -vtv -vp 0.000 0.000 0.000 -vd 0.000 0.000 1.000 -vu 0.000 1.000
           0.000 -vh 29.341 -vv 32.204 -x 300 -y 300 -vs 0.500 -vl -0.500
           -vo 100.000

        > -vtv -vp 0.000 0.000 0.000 -vd 0.000 0.000 1.000 -vu 0.000 1.000
           0.000 -vh 29.341 -vv 32.204 -x 300 -y 300 -vs -0.500 -vl 0.500
           -vo 100.000

        > -vtv -vp 0.000 0.000 0.000 -vd 0.000 0.000 1.000 -vu 0.000 1.000
          0.000 -vh 29.341 -vv 32.204 -x 300 -y 300 -vs 0.500 -vl 0.500
          -vo 100.000
    """

    VIEWTYPES = {0: 'vtv', 1: 'vth', 2: 'vtl', 3: 'vtc', 4: 'vta', 5: 'vts'}

    def __init__(self, name, origin=None, direction=None, up_vector=None, type=0,
                 h_size=60, v_size=60, shift=0, lift=0):
        u"""Create a view.

        Arg:
            origin: Set the view origin location (-vp) to (x, y, z). This is the focal
                point of a perspective view or the center of a parallel projection.
                Default: (0, 0, 0)
            direction: Set the view direction (-vd) vector to (x, y, z). The
                length of this vector indicates the focal distance as needed by
                the pixel depth of field (-pd) in rpict. Default: (0, 0, 1)
            up_vector: Set the view up (-vu) vector (vertical direction) to
                (x, y, z) default: (0, 1, 0).
            type: Set view type (-vt) to one of the choices below.
                    0 - Perspective (v)
                    1 - Hemispherical fisheye (h)
                    2 - Parallel (l)
                    3 - Cylindrical panoroma (c)
                    4 - Angular fisheye (a)
                    5 - Planisphere [stereographic] projection (s)
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
                image starts just to the right of the normal view. A value of −1
                would be to the left. Larger or fractional values are permitted
                as well.
            lift: Set the view lift (-vl) to a value. This is the amount the
                actual image will be lifted up from the specified view.        
        """
        self.name = name
        self.origin = origin
        self.direction = direction
        self.up_vector = up_vector
        self.h_size = h_size
        self.v_size = v_size
        self.shift = shift
        self.lift = lift
        self.type = type
        # set for_clip to None
        self._fore_clip = None
        self._aft_clip = None

    @property
    def name(self):
        """AnalysisGrid name."""
        return self._name

    @name.setter
    def name(self, n):
        self._name = typing.valid_string(n)

    @property
    def type(self):
        """Set and get view type (-vt) to one of the choices below (0-5).

        0 - Perspective (v), 1 - Hemispherical fisheye (h),
        2 - Parallel (l),    3 - Cylindrical panorma (c),
        4 - Angular fisheye (a),
        5 - Planisphere [stereographic] projection (s)
        """
        return self._type

    @property
    def vt(self):
        """view type in radiance format."""
        return self.VIEWTYPES[self._type]

    @type.setter
    def type(self, value):
        self._type = typing.int_in_range(value, 0, 5)

        # set view size to 180 degrees for fisheye views
        if self.type in (1, 4, 5):
            if self.h_size != 180:
                self.h_size = 180
                print("Changed h_size to 180 for fisheye view type.")
            if self.v_size != 180:
                self.v_size = 180
                print("Changed v_size to 180 for fisheye view type.")

        elif self.type == 0:
            assert self.h_size < 180, ValueError(
                '\n{} is an invalid horizontal view size for Perspective view.\n'
                'The size should be smaller than 180.'.format(self.h_size))
            assert self.v_size < 180, ValueError(
                '\n{} is an invalid vertical view size for Perspective view.\n'
                'The size should be smaller than 180.'.format(self.v_size))

    @property
    def origin(self):
        """Set the view origin (-vp) to (x, y, z).

        This is the focal point of a perspective view or the center of a parallel
        projection. Default: (0, 0, 0)
        """
        return self._location

    @property
    def vp(self):
        """View point / origin."""
        return '%.3f %.3f %.3f' % (self.origin.x, self.origin.y, self.origin.z)

    @origin.setter
    def origin(self, value):
        self._location = pv.Point3D(*(float(v) for v in value)) \
            if value is not None else pv.Point3D(0, 0, 0)

    @property
    def direction(self):
        """Set the view direction (-vd) vector to (x, y, z).

        The length of this vector indicates the focal distance as needed by
        the pixel depth of field (-pd) in rpict. Default: (0, 0, 1)
        """
        return self._direction

    @property
    def vd(self):
        """View direction."""
        return '%.3f %.3f %.3f' % (self.direction.x, self.direction.y, self.direction.z)

    @direction.setter
    def direction(self, value):
        self._direction = pv.Vector3D(*(float(v) for v in value)) \
            if value is not None else pv.Vector3D(0, 0, 1)

    @property
    def up_vector(self):
        return self._up_vector

    @up_vector.setter
    def up_vector(self, value):
        """Set the view up (-vu) vector (vertical direction) to (x, y, z)

        Default: (0, 1, 0).
        """
        self._up_vector = pv.Vector3D(*(float(v) for v in value)) \
            if value is not None else pv.Vector3D(0, 1, 0)

    @property
    def vu(self):
        """View up."""
        return '%.3f %.3f %.3f' % (self.up_vector.x, self.up_vector.y, self.up_vector.z)

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
        """View horizontal size."""
        return str(self.h_size)

    @h_size.setter
    def h_size(self, value):
        self._h_size = typing.float_positive(value) if value is not None else 0

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
        """View vertical size."""
        return str(self.v_size)

    @v_size.setter
    def v_size(self, value):
        self._v_size = typing.float_positive(value) if value is not None else 0

    @property
    def shift(self):
        """Set the view shift (-vs).

        This is the amount the actual image will be shifted to the right of the specified
        view. This option is useful for generating skewed perspectives or rendering an
        image a piece at a time. A value of 1 means that the rendered image starts just
        to the right of the normal view. A value of −1 would be to the left. Larger or
        fractional values are permitted as well.
        """
        return self._shift

    @property
    def vs(self):
        """View shift."""
        return str(self.shift)

    @shift.setter
    def shift(self, value):
        self._shift = float(value) if value is not None else 0

    @property
    def lift(self):
        """Set the view lift (-vl) to a value.

        This is the amount the actual image will be lifted up from the specified view.
        """
        return self._lift

    @property
    def vl(self):
        """View lift."""
        return str(self.lift)

    @lift.setter
    def lift(self, value):
        self._lift = float(value) if value is not None else 0

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
        """View fore clip."""
        return str(self.fore_clip)

    @fore_clip.setter
    def fore_clip(self, distance):
        self._fore_clip = float(distance) if distance is not None else 0

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
        """View aft clip."""
        return str(self.aft_clip)

    @aft_clip.setter
    def aft_clip(self, distance):
        self._aft_clip = float(distance) if distance is not None else 0

    @classmethod
    def from_dict(cls, view_dict):
        """Create a view from a dictionary."""

        view = cls(
            name=view_dict['name'],
            origin=view_dict['origin'],
            direction=view_dict['direction'],
            up_vector=view_dict['up_vector'],
            h_size=view_dict['h_size'],
            v_size=view_dict['v_size'],
            shift=view_dict['shift'],
            lift=view_dict['lift'],
        )

        if view_dict['fore_clip'] is not None:
            view.fore_clip = view_dict['fore_clip']
        if view_dict['aft_clip'] is not None:
            view.aft_clip = view_dict['aft_clip']
        
        return view

    @classmethod
    def from_string(cls, name, view_string):
        """Create a view object from a string.
        
        This method is similar to from_string method for radiance parameters with the
        difference that all the parameters that are not related to view will be ignored.
        """
        view_mapper = {k:v for v, k in cls.VIEWTYPES.items()}

        mapper = {
            'name': name, 'vp': 'origin', 'vd': 'direction', 'vu': 'up_vector',
            'vh': 'h_size', 'vv': 'v_size', 'vs': 'shift', 'vl': 'lift',
            'vo': 'fore_clip', 'va': 'aft_clip'
        }

        base = {
            'name': name,
            'origin': None,
            'direction': None,
            'up_vector': None, 
            'h_size': None,
            'v_size': None,
            'shift': None,
            'lift': None,
            'type': None,
            'fore_clip': None,
            'aft_clip': None
        }

        # parse the string here
        options = parser.parse_radiance_options(view_string)

        for opt, value in options.items():
            if opt in mapper:
                base[mapper[opt]] = value
            elif opt[:2] == 'vt':
                base['type'] = view_mapper[opt]
            else:
                print('%s is not a view parameter and is ignored.' % opt)

        return cls.from_dict(base)

    @classmethod
    def from_file(self, file_path, name=None):
        if not os.path.isfile(file_path):
            raise IOError("Can't find {}.".format(file_path))
        name = name or os.path.split(os.path.splitext(file_path)[0])[-1]

        with open(file_path, 'r') as input_data:
            view_string = str(input_data.read()).rstrip()

        assert view_string[:3] == 'rvu', \
            'View file must start with rvu not %s' % view_string[:3]
        return self.from_string(name, view_string)

    def dimension(self, x_res=None, y_res=None):
        """Get dimensions for this view as '-x %d -y %d [-ld-]'.

        This method is same as vwrays -d. Default values for x_res and y_res are set to
        match Radiance defaults.
        """
        x, y = self.dimension_x_y(x_res, y_res)
        return '-x %d -y %d -ld%s' % (
            x, y, '-' if (self.fore_clip is None and self.aft_clip is None) else '+')

    def dimension_x_y(self, x_res=None, y_res=None):
        """Get dimensions for this view as x, y.
        
        Default values for x_res and y_res are set to match Radiance defaults.
        """
        # radiance default is 512
        x_res = int(x_res) if x_res is not None else 512
        y_res = int(y_res) if y_res is not None else 512

        if self.type in (1, 4, 5):
            return min(x_res, y_res), min(x_res, y_res)

        vh = self.h_size
        vv = self.v_size

        if self.type == 0:
            hv_ratio = math.tan(math.radians(vh) / 2.0) / \
                math.tan(math.radians(vv) / 2.0)
        else:
            hv_ratio = vh / vv

        # radiance keeps the larges max size and tries to scale the other size
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

        if self.type == 2:
            # parallel view (vtl)
            _vh = self.h_size / x_div_count
            _vv = self.v_size / y_div_count

        elif self.type == 0:
            # perspective (vtv)
            _vh = (2. * 180. / PI) * \
                math.atan(((PI / 180. / 2.) * self.h_size) / x_div_count)
            _vv = (2. * 180. / PI) * \
                math.atan(math.tan((PI / 180. / 2.) * self.v_size) / y_div_count)

        elif self.type in [1, 4, 5]:
            # fish eye
            _vh = (2. * 180. / PI) * \
                math.asin(math.sin((PI / 180. / 2.) * self.h_size) / x_div_count)
            _vv = (2. * 180. / PI) * \
                math.asin(math.sin((PI / 180. / 2.) * self.v_size) / y_div_count)

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
                _vl = ((int(view_count / y_div_count) / (y_div_count - 1)) - 0.5) \
                    * (y_div_count - 1)

            # create a copy from the current copy
            _n_view = View('%s_%d' % (self.name, view_count))

            # update parameters
            _n_view.h_size = _vh
            _n_view.v_size = _vv
            _n_view.shift = _vs
            _n_view.lift = _vl

            # add the new view to views list
            _views[view_count] = _n_view

        return _views

    def to_radiance(self):
        """Return full Radiance definition."""
        # create base information of view
        view = '-%s -vp %s -vd %s -vu %s' % (self.vt, self.vp, self.vd, self.vu)
        # view size properties
        viewSize = '-vh %.3f -vv %.3f' % (self.h_size, self.v_size)

        components = [view, viewSize]

        # add lift and shift if not 0
        if self.lift != 0 or self.shift != 0:
            components.append('-vs %.3f -vl %.3f' % (self.shift, self.lift))

        if self.fore_clip is not None:
            components.append('-vo %.3f' % self.fore_clip)

        if self.aft_clip is not None:
            components.append('-va %.3f' % self.aft_clip)

        return ' '.join(components)

    def to_dict(self):
        """Translate view to a dictionary."""
        return {
            'name': self.name,
            'origin': self.origin.to_dict(),
            'direction': self.direction.to_dict(),
            'up_vector': self.up_vector.to_dict(), 
            'h_size': self.h_size,
            'v_size': self.v_size, 
            'shift': self.shift,
            'lift': self.lift,
            'type': self.type, 
            'fore_clip': self.fore_clip,
            'aft_clip': self.aft_clip
        }

    def to_file(self, folder, file_name=None, mkdir=False):
        """Save view to a file.

        Args:
            folder: Target folder.
            file_name: Optional file name without extension (Default: self.name).
            mkdir: A boolean to indicate if the folder should be created in case it
                doesn't exist already (Default: False). 

        Returns:
            Full path to newly created file.
        """

        name = file_name or self.name + '.vf'
        # add rvu before the view itself
        content = 'rvu ' + self.to_radiance()
        return futil.write_to_file_by_name(folder, name, content, mkdir)

    def move(self, vector):
        """Move view."""
        self.origin = self.origin.move(pv.Vector3D(*vector))

    def rotate(self, angle, axis, origin):
        """Rotate view around an axis.

        Args:
            angle: Rotation angle in radians.
            axis: Rotation axis as a Vector3D (Default: self.up_vector).
            origin: Rotation origin point as a Point3D (Default: self.origin)
        """
        view_plane = plane.Plane(self.up_vector, self.origin, self.direction)
        axis = pv.Vector3D(*axis) or self.up_vector
        origin = pv.Point3D(*origin) or self.origin
        
        rotated_plane = view_plane.rotate(axis, angle, origin)
        self.origin = rotated_plane.o
        self.direction = rotated_plane.x
        self.up_vector = rotated_plane.n

    def ToString(self):
        """Overwrite .NET ToString."""
        return self.__repr__()

    def __repr__(self):
        """View representation."""
        return self.to_radiance()
