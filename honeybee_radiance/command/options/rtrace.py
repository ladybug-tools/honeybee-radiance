from .optionbase import OptionCollection, BoolOption, NumericOption, StringOption,\
    StringOptionJoined, IntegerOption, TupleOption, FileOption


class RtraceOptions(OptionCollection):
    """rtrace command options.

    Also see: https://floyd.lbl.gov/radiance/man_html/rtrace.1.html
    """

    __slots__ = (
        '_n', '_x', '_y', '_ld', '_h', '_f', '_o', '_w', '_i', '_u', '_bv', '_dt',
        '_dc', '_dj', '_ds', '_dr', '_dp', '_dv', '_ss', '_st', '_av', '_aw', '_ab',
        '_aa', '_ar', '_ad', '_as', '_me', '_ma', '_mg', '_ms', '_lr', '_lw', '_I',
        '_e', '_te', '_tE', '_ti', '_tI', '_af', '_ae', '_ai', '_aE', '_aI'
    )

    def __init__(self):
        """rtrace command options.

        Usage:

            options = RtraceOptions()
            options.ab = 5
            print(options.to_radiance())
            -ab 5

            options.u = False
            print(options.to_radiance())
            -ab 5 -u-
        """
        OptionCollection.__init__(self)
        self._n = IntegerOption('n', 'number of rendering processes - default: 1')
        self._x = IntegerOption('x', 'flush interval - default: 0')
        self._y = IntegerOption('y', 'y resolution - default: 0')
        self._ld = BoolOption('ld', 'limit distance - default: off')
        self._h = BoolOption('h', 'output header - default: on')
        self._f = StringOptionJoined(
            'f', 'format input/output = ascii/ascii - default: faa',
            valid_values=['a', 'f', 'd', 'c'], whole=False
        )
        self._o = StringOptionJoined(
            'o', 'output value - default: ov',
            valid_values=['o', 'd', 'v', 'V', 'w', 'W', 'l', 'L', 'c', 'p', 'n', 'N',
            's', 'm', 'M', '~'], whole=False
        )
        self._w = BoolOption('w', 'warning messages - default: on')
        self._i = BoolOption('i', 'irradiance calculation - default: off')
        self._I = BoolOption('I', 'irradiance calculation switch - default: off')
        self._u = BoolOption('u', 'uncorrelated Monte Carlo sampling - default: on')
        self._bv = BoolOption('bv', 'back face visibility - default: on')
        self._dt = NumericOption('dt', 'direct threshold - default: 0.030000')
        self._dc = NumericOption('dc', 'direct certainty - default: 0.750000')
        self._dj = NumericOption('dj', 'direct jitter - default: 0.000000',
                                 max_value=1.0)
        self._ds = NumericOption('ds', 'direct sampling - default: 0.200000')
        self._dr = IntegerOption('dr', 'direct relays - default: 2')
        self._dp = IntegerOption('dp', 'direct pretest density - default: 512')
        self._dv = BoolOption('dv', 'direct visibility - default: on')
        self._ss = NumericOption('ss', 'specular sampling - default: 1.000000')
        self._st = NumericOption('st', 'specular threshold - default: 0.150000')
        self._av = TupleOption(
            'av', 'ambient value - default: 0.000000 0.000000 0.000000', None, 3, float
        )
        self._aw = IntegerOption('aw', 'ambient value weight - default: 0')
        self._ab = IntegerOption('ab', 'ambient bounces - default: 0')
        self._aa = NumericOption('aa', 'ambient accuracy - default: 0.100000')
        self._ar = IntegerOption('ar', 'ambient resolution - default: 256')
        self._ad = IntegerOption('ad', 'ambient divisions - default: 1024')
        self._as = IntegerOption('as', 'ambient super-samples - default: 512')
        self._me = TupleOption(
            'me',
            'mist extinction coefficient - default: 0.00e+000 0.00e+000 0.00e+000', None,
            3, float)
        self._ma = TupleOption(
            'ma', 'mist scattering albedo - default: 0.000000 0.000000 0.000000', None,
            3, float)
        self._mg = NumericOption(
            'mg', 'mist scattering eccentricity - default: 0.000000')
        self._ms = NumericOption('ms', 'mist sampling distance - default: 0.000000')
        self._lr = IntegerOption(
            'lr', 'limit reflection (Russian roulette) - default: -10')
        self._lw = NumericOption('lw', 'limit weight - default: 2.00e-003')
        self._te = StringOption('te', 'trace excluded modifier')
        self._tE = FileOption('tE', 'trace excluded modifiers file')
        self._ti = StringOption('ti', 'trace included modifier')
        self._tI = FileOption('tI', 'trace included modifiers file')
        self._af = StringOption('af', 'ambient file')
        self._ae = StringOption('ae', 'ambient excluded modifier')
        self._aE = FileOption('aE', 'ambient excluded modifiers file')
        self._ai = StringOption('ai', 'ambient included modifier')
        self._aI = FileOption('aI', 'ambient included modifiers file')
        self._e = FileOption('e', 'error file')
        self._on_setattr_check = True

    def on_setattr(self):
        # -i and -I cannot both be True.
        assert not (self.i == True and self.I == True), \
            'You can either set -i or -I to True not both.'
        assert not (self.ti.is_set and self.te.is_set), \
            'Both ti and te are set. The program can use either an include list or ' \
            'an exclude list, but not both.'
        assert not (self.tI.is_set and self.tE.is_set), \
            'Both tI and tE are set. The program can use either an include list or ' \
            'an exclude list, but not both.'
        assert not (self.ai.is_set and self.ae.is_set), \
            'Both ai and ae are set. The program can use either an include list or ' \
            'an exclude list, but not both.'
        assert not (self.aI.is_set and self.aE.is_set), \
            'Both aI and aE are set. The program can use either an include list or ' \
            'an exclude list, but not both.'
        
        if self.n.is_set and self.n > 1:
            assert not 't' in self.o.to_radiance().lower(), \
            'Multiple processes also do not work properly with ray tree output using' \
            ' any of the `-o*t*` options.'

        if self.n.is_set and self.x.is_set:
            assert self.n <= self.x, \
                'There is no benefit from specifying more processes than the -x ' \
                'setting, which forces a wait at each flush.'

    @property
    def n(self):
        """number of rendering processes - default: 1
        
        Execute in parallel on nproc local processes.
        
        NOTE:
        
        This option is incompatible with the -P and -PP, options. Multiple processes also
        do not work properly with ray tree output using any of the `-o*t*` options. There
        is no benefit from specifying more processes than there are cores available on
        the system or the -x setting, which forces a wait at each flush.
        """
        return self._n

    @n.setter
    def n(self, value):
        self._n.value = value

    @property
    def x(self):
        """flush interval - default: 0

        Set the x resolution to res. The output will be flushed after every res input
        rays if -y is set to zero. A value of one means that every ray will be flushed,
        whatever the setting of -y. A value of zero means that no output flushing will
        take place.
        """
        return self._x

    @x.setter
    def x(self, value):
        self._x.value = value

    @property
    def y(self):
        """y resolution - default: 0
        
        Set the y resolution to res. The program will exit after res scanlines have been
        processed, where a scanline is the number of rays given by the -x option, or 1 if
        -x is zero. A value of zero means the program will not halt until the end of file
        is reached. 
        
        If both -x and -y options are given, a resolution string is printed at the
        beginning of the output. This is mostly useful for recovering image dimensions
        with pvalue, and for creating valid Radiance picture files using the color output
        format. (See the -f option, above.) 
        """
        return self._y

    @y.setter
    def y(self, value):
        self._y.value = value

    @property
    def ld(self):
        """limit distance - default: off"""
        return self._ld

    @ld.setter
    def ld(self, value):
        self._ld.value = value

    @property
    def h(self):
        """output header - default: on
        
        Boolean switch for information header on output
        """
        return self._h

    @h.setter
    def h(self, value):
        self._h.value = value

    @property
    def f(self):
        """format input/output = ascii/ascii - default: faa

        Format input according to the character `i` and output according to the character
        `o`. Rtrace understands the following input and output formats
        - `a` for ascii
        - `f` for single-precision floating point
        - `d` for double-precision floating point

        In addition to these three choices, the character `c` may be used to denote
        4-byte floating point (Radiance) color format for the output of values only (-ov
        option, below). If the output character is missing, the input format is used.
        """
        return self._f

    @f.setter
    def f(self, value):
        self._f.value = value

    @property
    def o(self):
        """output value - default: ov
        -o[spec]
        
        Produce output fields according to spec. Characters are interpreted as follows:
        o - origin (input)
        d - direction (normalized)
        v - value (radiance)
        V - contribution (radiance)
        w - weight
        W - color coefficient
        l - effective length of ray
        L - first intersection distance
        c - local (u,v) coordinates
        p - point of intersection
        n - normal at intersection (perturbed)
        N - normal at intersection (unperturbed)
        s - surface name
        m - modifier name
        M - material name
        ~ tilde (end of trace marker)
        If the letter `t` appears in spec, then the fields following will be printed for
        every ray traced, not just the final result. If the capital letter `T` is given
        instead of `t`, then all rays will be reported, including shadow testing rays to
        light sources. Spawned rays are indented one tab for each level. The tilde
        marker (`~`) is a handy way of differentiating the final ray value from daughter
        values in a traced ray tree, and usually appears right before the `t` or `T`
        output flags. E.g., -ov~TmW will emit a tilde followed by a tab at the end of
        each trace, which can be easily distinguished even in binary output.
        """
        return self._o

    @o.setter
    def o(self, value):
        self._o.value = value

    @property
    def te(self):
        """Append modifier to the trace exclude list.
        
        The excluded modifier will not be reported by the trace option `-o*t*`. Any ray
        striking an object having mod as its modifier will not be reported to the
        standard output with the rest of the rays being traced. This option has no
        effect unless either the `t` or `T` option has been given as part of the output
        specifier. Any number of excluded modifiers may be given, but each must appear in
        a separate option.
        """
        return self._te

    @te.setter
    def te(self, value):
        self._te.value = value

    @property
    def ti(self):
        """Add modifier to the trace include list.
        
        Add modifier to the trace include list, so that it will be reported by the trace
        option. The program can use either an include list or an exclude list, but not
        both. 
        """
        return self._ti

    @ti.setter
    def ti(self, value):
        self._ti.value = value

    @property
    def tE(self):
        """Append modifier to the trace exclude list from file.
        
        Same as -te, except read modifiers to be excluded from file. The RAYPATH
        environment variable determines which directories are searched for this file. The
        modifier names are separated by white space in the file.
        """
        return self._tE

    @tE.setter
    def tE(self, value):
        self._tE.value = value

    @property
    def tI(self):
        """Add modifier to the trace include list from file.

        Same as -ti, except read modifiers to be included from file.
        """
        return self._tI

    @tI.setter
    def tI(self, value):
        self._tI.value = value

    @property
    def w(self):
        """warning messages - default: on"""
        return self._w

    @w.setter
    def w(self, value):
        self._w.value = value

    @property
    def e(self):
        """Send error messages and progress reports to efile.
        
        By default the error messages are directed to standard error."""
        return self._e

    @e.setter
    def e(self, value):
        self._e.value = value

    @property
    def i(self):
        """irradiance calculation - default: off
        
        Boolean switch to compute irradiance rather than radiance values. This
        only affects the final result, substituting a Lambertian surface and
        multiplying the radiance by pi. Glass and other transparent surfaces are
        ignored during this stage. Light sources still appear with their original
        radiance values, though the -dv option (below) may be used to override
        this. This option is especially useful in conjunction with ximage for computing
        illuminance at scene points.

        Keep in mind that -i sends a ray into the scene and calculates the incident
        irradiance at that surface point. For calculating irradiance at the sensor point
        see -I.

        For understanding the difference between -i and -I see here:
        https://discourse.radiance-online.org/t/rtrace-i-i-flags/4192/3
        """
        return self._i

    @i.setter
    def i(self, value):
        self._i.value = value

    @property
    def I(self):
        """irradiance calculation switch - default: off
        
        Boolean switch to compute irradiance rather than radiance, with the input origin
        and direction interpreted instead as measurement point and orientation.

        For understanding the difference between -i and -I see here:
        https://discourse.radiance-online.org/t/rtrace-i-i-flags/4192/3
        """
        return self._I

    @I.setter
    def I(self, value):
        self._I.value = value

    @property
    def u(self):
        """uncorrelated Monte Carlo sampling - default: on
        
        Boolean switch to control uncorrelated random sampling. When "off", a
        low-discrepancy sequence is used, which reduces variance but can result
        in a brushed appearance in specular highlights. When "on", pure Monte
        Carlo sampling is used in all calculations.
        """
        return self._u

    @u.setter
    def u(self, value):
        self._u.value = value

    @property
    def bv(self):
        """back face visibility - default: on
        
        Boolean switch for back face visibility. With this switch off, back faces of
        opaque objects will be invisible to all rays. This is dangerous unless the model
        was constructed such that all surface normals on opaque objects face outward.
        Although turning off back face visibility does not save much computation time
        under most circumstances, it may be useful as a tool for scene debugging, or for
        seeing through one-sided walls from the outside. This option has no effect on
        transparent or translucent materials. 
        """
        return self._bv

    @bv.setter
    def bv(self, value):
        self._bv.value = value

    @property
    def dt(self):
        """direct threshold - default: 0.030000

        Set the direct threshold to frac. Shadow testing will stop when the
        potential contribution of at least the next and at most all remaining
        light source samples is less than this fraction of the accumulated value.
        The remaining light source contributions are approximated statistically.
        A value of zero means that all light source samples will be tested for
        shadow.
        """
        return self._dt

    @dt.setter
    def dt(self, value):
        self._dt.value = value

    @property
    def dc(self):
        """direct certainty - default: 0.750000

        Set the direct certainty to frac. A value of one guarantees that the
        absolute accuracy of the direct calculation will be equal to or better
        than that given in the -dt specification. A value of zero only insures
        that all shadow lines resulting in a contrast change greater than the
        -dt specification will be calculated.
        """
        return self._dc

    @dc.setter
    def dc(self, value):
        self._dc.value = value

    @property
    def dj(self):
        """direct jitter - default: 0.000000

        Set the direct jittering to frac. A value of zero samples each source
        at specific sample points (see the -ds option below), giving a smoother
        but somewhat less accurate rendering. A positive value causes rays to
        be distributed over each source sample according to its size,
        resulting in more accurate penumbras. This option should never be
        greater than 1, and may even cause problems (such as speckle) when the
        value is smaller. A warning about aiming failure will issued if frac is
        too large. It is usually wise to turn off image sampling when using
        direct jitter by setting -ps to 1.
        """
        return self._dj

    @dj.setter
    def dj(self, value):
        self._dj.value = value

    @property
    def ds(self):
        """direct sampling - default: 0.200000

        Set the direct sampling ratio to frac. A light source will be subdivided
        until the width of each sample area divided by the distance to the
        illuminated point is below this ratio. This assures accuracy in regions
        close to large area sources at a slight computational expense. A value
        of zero turns source subdivision off, sending at most one shadow ray to
        each light source.
        """
        return self._ds

    @ds.setter
    def ds(self, value):
        self._ds.value = value

    @property
    def dr(self):
        """direct relays - default: 2

        Set the number of relays for secondary sources to N. A value of 0 means
        that secondary sources will be ignored. A value of 1 means that sources
        will be made into first generation secondary sources; a value of 2 means
        that first generation secondary sources will also be made into second
        generation secondary sources, and so on.
        """
        return self._dr

    @dr.setter
    def dr(self, value):
        self._dr.value = value

    @property
    def dp(self):
        """direct pretest density - default: 512

        Set the secondary source presampling density to D. This is the number of
        samples per steradian that will be used to determine ahead of time
        whether or not it is worth following shadow rays through all the
        reflections and/or transmissions associated with a secondary source path.
        A value of 0 means that the full secondary source path will always be
        tested for shadows if it is tested at all.
        """
        return self._dp

    @dp.setter
    def dp(self, value):
        self._dp.value = value

    @property
    def dv(self):
        """direct visibility - default: on
        
        Boolean switch for light source visibility. With this switch off, sources will be
        black when viewed directly although they will still participate in the direct
        calculation. This option is mostly for the program `mkillum` to avoid
        inappropriate counting of light sources, but it may also be desirable in
        conjunction with the -i option.
        """
        return self._dv

    @dv.setter
    def dv(self, value):
        self._dv.value = value

    @property
    def ss(self):
        """specular sampling - default: 1.000000

        Set the specular sampling to samp. For values less than 1, this is the
        degree to which the highlights are sampled for rough specular materials.
        A value greater than one causes multiple ray samples to be sent to reduce
        noise at a commmesurate cost. A value of zero means that no jittering
        will take place, and all reflections will appear sharp even when they
        should be diffuse. This may be desirable when used in combination with
        image sampling to obtain faster renderings.
        """
        return self._ss

    @ss.setter
    def ss(self, value):
        self._ss.value = value

    @property
    def st(self):
        """specular threshold - default: 0.150000

        Set the specular sampling threshold to frac. This is the minimum
        fraction of reflection or transmission, under which no specular sampling
        is performed. A value of zero means that highlights will always be
        sampled by tracing reflected or transmitted rays. A value of one means
        that specular sampling is never used. Highlights from light sources
        will always be correct, but reflections from other surfaces will be
        approximated using an ambient value. A sampling threshold between zero
        and one offers a compromise between image accuracy and rendering time.
        """
        return self._st

    @st.setter
    def st(self, value):
        self._st.value = value

    @property
    def av(self):
        """ambient value - default: 0.000000 0.000000 0.000000
        
        Set the ambient value to a radiance of red grn blu . This is the final value used
        in place of an indirect light calculation. If the number of ambient bounces is
        one or greater and the ambient value weight is non-zero (see -aw and -ab below),
        this value may be modified by the computed indirect values to improve overall
        accuracy.
        """
        return self._av

    @av.setter
    def av(self, value):
        self._av.value = value

    @property
    def aw(self):
        """ambient value weight - default: 0
        
        Set the relative weight of the ambient value given with the -av option. As
        new indirect irradiances are computed, they will modify the default ambient
        value in a moving average, with the specified weight assigned to the initial
        value given on the command and all other weights set to 1. If a value of 0 is
        given with this option, then the initial ambient value is never modified. This is
        the safest value for scenes with large differences in indirect contributions,
        such as when both indoor and outdoor (daylight) areas are visible.
        """
        return self._aw

    @aw.setter
    def aw(self, value):
        self._aw.value = value

    @property
    def ab(self):
        """ambient bounces - default: 0

        Number of ambient bounces. This is the maximum number of diffuse bounces computed
        by the indirect calculation. A value of zero implies no indirect calculation.
        """
        return self._ab

    @ab.setter
    def ab(self, value):
        self._ab.value = value

    @property
    def aa(self):
        """ambient accuracy - default: 0.100000

        Number of ambient accuracy. This value will approximately equal the error from
        indirect illuminance interpolation. A value of zero implies no interpolation.
        """
        return self._aa

    @aa.setter
    def aa(self, value):
        self._aa.value = value

    @property
    def ar(self):
        """ambient resolution - default: 256

        This number will determine the maximum density of ambient values used in
        interpolation. Error will start to increase on surfaces spaced closer than the
        scene size divided by the ambient resolution. The maximum ambient value density
        is the scene size times the ambient accuracy.
        """
        return self._ar

    @ar.setter
    def ar(self, value):
        self._ar.value = value

    @property
    def ad(self):
        """ambient divisions - default: 1024

        Number of ambient divisions. The error in the Monte Carlo calculation of indirect
        illuminance will be inversely proportional to the square root of this number. A
        value of zero implies no indirect calculation.
        """
        return self._ad

    @ad.setter
    def ad(self, value):
        self._ad.value = value

    @property
    def as_(self):
        """ambient super-samples - default: 512

        Number of ambient super-samples. Super-samples are applied only to the ambient
        divisions which show a significant change.
        """
        return self._as

    @as_.setter
    def as_(self, value):
        self._as.value = value

    @property
    def ae(self):
        """Append modifier to the ambient exclude list.
        
        So that it will not be considered during the indirect calculation. This is a hack
        for speeding the indirect computation by ignoring certain objects. Any object
        having mod as its modifier will get the default ambient level rather than a
        calculated value. Any number of excluded modifiers may be given, but each must
        appear in a separate option.
        """
        return self._ae

    @ae.setter
    def ae(self, value):
        self._ae.value = value

    @property
    def ai(self):
        """Add modifier to the ambient include list.

        So that it will be considered during the indirect calculation. The program can
        use either an include list or an exclude list, but not both.
        """
        return self._ai

    @ai.setter
    def ai(self, value):
        self._ai.value = value

    @property
    def aE(self):
        """Append modifier to the ambient exclude list from file.

        Same as -ae, except read modifiers to be excluded from file. The RAYPATH
        environment variable determines which directories are searched for this file. The
        modifier names are separated by white space in the file. 
        """
        return self._aE

    @aE.setter
    def aE(self, value):
        self._aE.value = value

    @property
    def aI(self):
        """Add modifier to the ambient include list from file.

        Same as -ai, except read modifiers to be included from file.
        """
        return self._aI

    @aI.setter
    def aI(self, value):
        self._aI.value = value


    @property
    def af(self):
        """Set the ambient file to filename.
        
        This is where indirect illuminance will be stored and retrieved. Normally,
        indirect illuminance values are kept in memory and lost when the program
        finishes or dies. By using a file, different invocations can share illuminance
        values, saving time in the computation. The ambient file is in a
        machine-independent binary format which can be examined with lookamb.
        
        The ambient file may also be used as a means of communication and data sharing
        between simultaneously executing processes. The same file may be used by multiple
        processes, possibly running on different machines and accessing the file via the
        network (ie. nfs(4)). The network lock manager lockd(8) is used to insure that
        this information is used consistently. 
        
        If any calculation parameters are changed or the scene is modified, the old
        ambient file should be removed so that the calculation can start over from
        scratch. For convenience, the original ambient parameters are listed in the
        header of the ambient file. Getinfo(1) may be used to print out this information.
        """
        return self._af

    @af.setter
    def af(self, value):
        self._af.value = value

    @property
    def me(self):
        """mist extinction coefficient - default: 0.00e+000 0.00e+000 0.00e+000
        
        Set the global medium extinction coefficient to the indicated color, in units of
        1/distance (distance in world coordinates). Light will be scattered or absorbed
        over distance according to this value. The ratio of scattering to total
        scattering plus absorption is set by the albedo parameter, described below. 
        """
        return self._me

    @me.setter
    def me(self, value):
        self._me.value = value

    @property
    def ma(self):
        """mist scattering albedo - default: 0.000000 0.000000 0.000000

        Set the global medium albedo to the given value between 0 0 0 and 1 1 1. A zero
        value means that all light not transmitted by the medium is absorbed. A unitary
        value means that all light not transmitted by the medium is scattered in some new
        direction. The isotropy of scattering is determined by the Heyney-Greenstein
        parameter, described below. 
        """
        return self._ma

    @ma.setter
    def ma(self, value):
        self._ma.value = value

    @property
    def mg(self):
        """mist scattering eccentricity - default: 0.000000
        
        Set the medium Heyney-Greenstein eccentricity parameter. This parameter
        determines how strongly scattering favors the forward direction. A value of 0
        indicates perfectly isotropic scattering. As this parameter approaches 1,
        scattering tends to prefer the forward direction.
        """
        return self._mg

    @mg.setter
    def mg(self, value):
        self._mg.value = value

    @property
    def ms(self):
        """mist sampling distance - default: 0.000000

        Set the medium sampling distance, in world coordinate units. During source
        scattering, this will be the average distance between adjacent samples. A
        value of 0 means that only one sample will be taken per light source within a
        given scattering volume. 
        """
        return self._ms

    @ms.setter
    def ms(self, value):
        self._ms.value = value

    @property
    def lr(self):
        """limit reflection (Russian roulette) - default: -10

        Limit reflections to a maximum of N, if N is a positive integer. If N
        is zero, then Russian roulette is used for ray termination, and the
        -lw setting (below) must be positive. If N is a negative integer, then
        this sets the upper limit of reflections past which Russian roulette
        will be used. In scenes with dielectrics and total internal reflection,
        a setting of 0 (no limit) may cause a stack overflow.
        """
        return self._lr

    @lr.setter
    def lr(self, value):
        self._lr.value = value

    @property
    def lw(self):
        """limit weight - default: 2.00e-003
        
        Limit the weight of each ray to a minimum of frac. During ray-tracing,
        a record is kept of the estimated contribution (weight) a ray would have
        in the image. If this weight is less than the specified minimum and the
        -lr setting (above) is positive, the ray is not traced. Otherwise,
        Russian roulette is used to continue rays with a probability equal to
        the ray weight divided by the given frac.
        """
        return self._lw

    @lw.setter
    def lw(self, value):
        self._lw.value = value
