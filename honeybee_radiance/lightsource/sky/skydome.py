"""Virtual skydome for daylight coefficient studies with constant radiance."""

from ._skybase import _SkyDome
import honeybee.typing as typing


class SkyDome(_SkyDome):
    """Virtual skydome for daylight coefficient studies with constant radiance.

    Use this sky to calculate daylight matrix.

    .. code-block:: shell

        #@rfluxmtx h=u u=Y
        void glow ground_glow
        0
        0
        4 0.2 0.2 0.2 0

        ground_glow source ground
        0
        0
        4 0 0 -1 180

        #@rfluxmtx h=r1 u=Y
        void glow sky_glow
        0
        0
        4 1 1 1 0

        sky_glow source sky
        0
        0
        4 0 0 1 180

    Args:
        density: Sky patch subdivision density. This values is similar to -m option
            in gendaymtx command. Default is 1 which means 145 sky patches and 1
            patch for the ground.

            One can add to the resolution typically by factors of two (2, 4, 8, ...)
            which yields a higher resolution sky using the Reinhart patch subdivision
            For example, setting density to 4 yields a sky with 2305 patches plus one
            patch for the ground.
        ground_emittance: Ground emittance value between 0.0 and 1.0 - Default: 0.2
    """
    __slots__ = ('_sky_density', '_ground_emittance')

    def __init__(self, sky_density=1, ground_emittance=0.2):
        _SkyDome.__init__(self, modifier='void')
        self.sky_density = sky_density
        self.ground_hemisphere.r_emittance = ground_emittance
        self.ground_hemisphere.g_emittance = ground_emittance
        self.ground_hemisphere.b_emittance = ground_emittance

    @property
    def sky_density(self):
        """Set and get sky subdivision density."""
        return self._sky_density

    @sky_density.setter
    def sky_density(self, v):
        density = typing.int_in_range(v, 1, input_name='Sky subdivision density')
        self._sky_density = density

    def to_radiance(self):
        """Radiance definition for SkyDome."""

        return '#@rfluxmtx h=u u=Y\n%s\n\n#@rfluxmtx h=r%d u=Y\n%s\n' % (
            self.ground_hemisphere, self.sky_density, self.sky_hemisphere
        )


class UniformSky(_SkyDome):
    """Uniform sky is similar to a SkyDome but with no rfluxmtx header.

    .. code-block:: shell

        void glow sky_glow
        0
        0
        4 1 1 1 0

        sky_glow source sky
        0
        0
        4 0 0 1 180

        void glow ground_glow
        0
        0
        4 0.2 0.2 0.2 0

        ground_glow source ground
        0
        0
        4 0 0 -1 180

    Args:
        ground_emittance: Ground emittance value between 0.0 and 1.0 - Default: 0.2

    """
    __slots__ = ('_ground_emittance',)

    def __init__(self, ground_emittance=0.2):
        _SkyDome.__init__(self, modifier='void')
        self.ground_hemisphere.r_emittance = ground_emittance
        self.ground_hemisphere.g_emittance = ground_emittance
        self.ground_hemisphere.b_emittance = ground_emittance

    def to_radiance(self):
        """Radiance definition for uniform sky."""
        return '%s\n\n%s\n' % (self.sky_hemisphere, self.ground_hemisphere)
