from .optionbase import BoolOption, StringOption, StringOptionJoined, IntegerOption, \
    FileOption
from .rtrace import RtraceOptions
import honeybee_radiance.exception as exception
import warnings


# TODO: Add input pattern check for -p
class RcontribOptions(RtraceOptions):
    """rcontrib command options.

    [ -n nprocs ][ -V ][ -c count ][ -fo | -r ][ -e expr ][ -f source ][ -o ospec ]
    [ -p p1=V1,p2=V2][ -b binv ][ -bn nbins ] { -m mod | -M file } [ $EVAR ] [ @file ]
    [ rtrace options ]
    
    NOTE:
    https://www.radiance-online.org/learning/documentation/manual-pages/pdfs/rcontrib.pdf
    """

    __slots__ = ('_c', '_V', '_fo', '_f', '_e', '_r', '_p', '_b', '_bn', '_m', '_M',
        '_o', '_ap')

    def __init__(self):
        """rcontrib command options."""
        RtraceOptions.__init__(self)
        self._on_setattr_check = False
        self._c = IntegerOption('c', 'accumulated rays per record - default: 1')
        self._V = BoolOption('V', 'output coefficients - default: off')
        self._fo = BoolOption('fo', 'format output - default: off')
        self._o = StringOption('o', 'output file. it can include ')
        self._r = BoolOption('r', 'data recovery on existing files')
        self._f = StringOption('f', 'source file - e.g. klems_ang.cal')
        self._e = StringOption('e', 'expression')
        self._p = StringOption('p', 'additional parameters')
        # b and bn are tricky as they can be string values like tbin or Ntbins and they
        # can be integer values like 0, 1, etc or as mix like
        # kbin(0.525,0.0136,-0.851,0,0,1)! I leave them to be string for now.
        self._b = StringOption('b', 'bin numbers')
        self._bn = StringOption('bn', 'number of bins')
        self._m = StringOption('m', 'modifier name')
        self._M = FileOption('M', 'modifiers file')
        self._ap = FileOption('ap', 'photon map contribution support')
        self._on_setattr_check = True

    def on_setattr(self):
        RtraceOptions.on_setattr(self)
        # -r and -fo cannot both be True.
        if not hasattr(self, 'r'):
            return  # this happens on init
        if self.r.is_set and self.fo.is_set:
            raise exception.ExclusiveOptionsError(self.command, 'r', 'fo')
        if self.m.is_set and self.M.is_set:
            raise exception.ExclusiveOptionsError(self.command, 'm', 'M')
        if self.ar.is_set or (self.aa.is_set and self.aa != 0):
            # warning about aa being set to 0 in rcontrib
            warn = '%s: aa will be set to 0 in rcontrib.' % self.command
            if self.ar.is_set:
                warn = ' '.join((
                    warn,
                    'there will be no ambient caching '
                    'and the value for ar will be ignored.'
                ))
            warnings.warn(warn)

    @property
    def c(self):
        """accumulated rays per record - default: 1
        
        The -c option tells rcontrib how many rays to accumulate for each record. The
        default value is one, meaning a full record will be produced for each input ray.
        For values greater than one, contributions will be averaged together over the
        given number of input rays.
        
        If set to zero, only a single record will be produced at the very end,
        corresponding to the sum of all rays given on the input (rather than the
        average). This is equivalent to passing all the output records through a program
        like total to sum RGB values together, but is much more efficient. Using this
        option, it is possible to reverse sampling, sending rays from a parallel source
        such as the sun to a diffuse surface, for example. Note that output flushing via
        zero-direction rays is disabled with -c set to zero.
        """
        return self._c

    @c.setter
    def c(self, value):
        self._c.value = value

    @property
    def V(self):
        """output contribution versus coefficients - default: off = coefficients
        
        By setting the boolean -V option, you may instruct rcontrib to report the
        contribution from each material rather than the ray coefficient. This is
        particularly useful for light sources with directional output distributions,
        whose value would otherwise be lost in the shuffle.
        
        With the default -V- setting, the output of rcontrib is a coefficient that must
        be multiplied by the radiance of each material to arrive at a final contribution.
        
        This is more convenient for computing daylight coefficients, or cases where the
        actual radiance is not desired. Use the -V+ setting when you wish to simply sum
        together contributions (with possible adjustment factors) to obtain a final
        radiance value. Combined with the -i or -I option, irradiance contributions are
        reported by -V+ rather than radiance, and -V- coefficients contain an additional
        factor of PI.
        """
        return self._V

    @V.setter
    def V(self, value):
        self._V.value = value

    @property
    def fo(self):
        """format output."""
        return self._fo

    @fo.setter
    def fo(self, value):
        self._fo.value = value

    @property
    def f(self):
        """source file."""
        return self._f

    @f.setter
    def f(self, value):
        self._f.value = value

    @property
    def r(self):
        """data recovery."""
        return self._r

    @r.setter
    def r(self, value):
        self._r.value = value

    @property
    def e(self):
        """expression.
        
        The -e expr option can be used to define variables on the command line. Since
        many of the characters in an expression have special meaning to the shell, it
        should usually be enclosed in single quotes. 
        """
        return self._e

    @e.setter
    def e(self, value):
        self._f.value = value

    @property
    def p(self):
        """additional parameters."""
        return self._p

    @p.setter
    def p(self, value):
        self._p.value = value

    @property
    def b(self):
        """bin numbers.
        
        The -b option may be used to further define a "bin number" within each object if
        finer resolution is needed, and this will be applied to a "%d" format in the
        output file specification if present. (The final integer will be offset
        incrementally if the output is a RADIANCE picture and more than one modifier has
        the same format specification.) The actual bin number is computed at run time
        based on ray direction and surface intersection.
        """
        return self._b

    @b.setter
    def b(self, value):
        self._b.value = value

    @property
    def bn(self):
        """number of bins.
        
        The number of bins must be specified in advance with the -bn option, and this is
        critical for output files containing multiple values per record. A variable or
        constant name may be given for this parameter if it has been defined via a
        previous -f or -e option. Since bin numbers start from zero, the bin count is
        always equal to the last bin plus one. The most recent -p, -b, -bn and -o options
        to the left of each -m setting are the ones used for that modifier.
        """
        return self._bn

    @bn.setter
    def bn(self, value):
        self._bn.value = value

    @property
    def m(self):
        """modifier name."""
        return self._m

    @m.setter
    def m(self, value):
        self._m.value = value

    @property
    def M(self):
        """modifiers file.
        
        A modifier list may be read from a file using the -M option. The RAYPATH
        environment variable determines directories to search for this file. (No search
        takes place if a file name begins with a `.`, `/` or `~` character.)
        """
        return self._M

    @M.setter
    def M(self, value):
        self._M.value = value

    @property
    def ap(self):
        """photon map generated file.
        
        Rcontrib supports light source contributions from photon maps generated by mkpmap
        with its -apC option. Enabling photon mapping is described in the rtrace man page
        along with its relevant settings. In photon mapping mode, rcontrib only supports
        contributions from light sources, not arbitrary modifiers.
        """
        return self._ap

    @ap.setter
    def ap(self, value):
        self._ap.value = value
    