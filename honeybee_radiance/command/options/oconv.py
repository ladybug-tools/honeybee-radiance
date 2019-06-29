"""Oconv parameters."""
from .optionbase import OptionCollection, FileOption, TupleOption, IntegerOption, \
    BoolOption


class OconvOptions(OptionCollection):
    """
    [ -i octree | -b xmin ymin zmin size ][ -n objlim ][ -r maxres ][ -f ][ -w ]

    Also see: https://floyd.lbl.gov/radiance/man_html/oconv.1.html
    """

    __slots__ = ('_i', '_b', '_n', '_r', '_f', '_w')

    def __init__(self):
        """oconv command options."""
        OptionCollection.__init__(self)
        self._i = FileOption('i', 'existing octree file')
        self._b = TupleOption(
            'b', 'bounding box as min_x, min_y, min_z and size', None, 4, float
        )
        self._n = IntegerOption(
            'n', 'maximum surface set size for each voxel - default: 6', min_value=0
        )
        self._r = IntegerOption(
            'r', 'maximum octree resolution - default: 16384', min_value=0
        )
        self._f = BoolOption('f', 'frozen octree - default: off')
        self._w = BoolOption('w', 'warning messages - default: on')
        self._on_setattr_check = True

    def on_setattr(self):
        assert not (self.b.is_set and self.i.is_set), \
            'The -b and -i options are mutually exclusive.'

    @property
    def i(self):
        """input octree."""
        return self._i

    @i.setter
    def i(self, value):
        self._i.value = value

    @property
    def b(self):
        """Scene bounding cube.
        
        The -b option allows the user to give a bounding cube for the scene, starting at
        xmin ymin zmin and having a side length size. If the cube does not contain all of
        the surfaces, an error results.
        
        The -b and -i options are mutually exclusive.
        """
        return self._b

    @b.setter
    def b(self, value):
        self._b.value = value

    @property
    def n(self):
        """maximum surface set size for each voxel.

        The -n option specifies the maximum surface set size for each voxel. Larger
        numbers result in quicker octree generation, but potentially slower rendering.
        Smaller values may or may not produce faster renderings, since the default number
        (6) is close to optimal for most scenes.
        """
        return self._n

    @n.setter
    def n(self, value):
        self._n.value = value

    @property
    def r(self):
        """maximum octree resolution - default: 16384.
        
        The -r option specifies the maximum octree resolution. This should be greater
        than or equal to the ratio of the largest and smallest dimensions in the scene
        (ie. surface size or distance between surfaces). The default is 16384.
        """
        return self._r

    @r.setter
    def r(self, value):
        self._r.value = value

    @property
    def f(self):
        """frozen octree switch.

        The -f option produces a frozen octree containing all the scene information.
        Normally, only a reference to the scene files is stored in the octree, and
        changes to those files may invalidate the result. The freeze option is useful
        when the octree file's integrity and loading speed is more important than its
        size, or when the octree is to be relocated to another directory, and is
        especially useful for creating library objects for the "instance" primitive type.
        If the input octree is frozen, the output will be also.
        """
        return self._f

    @f.setter
    def f(self, value):
        self._f.value = value

    @property
    def w(self):
        """warning messages - default: on"""
        return self._w

    @w.setter
    def w(self, value):
        self._w.value = value
