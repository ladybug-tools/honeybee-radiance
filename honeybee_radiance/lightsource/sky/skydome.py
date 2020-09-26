"""Virtual skydome for daylight coefficient studies with constant radiance.

Here is an example of the output.

.. code-block:: shell

    #@rfluxmtx h=u u=Y
    void glow grd_glow
    0
    0
    4 1 1 1 0

    grd_glow source ground
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

"""

from ._skybase import _SkyDome
import honeybee.typing as typing


class SkyDome(_SkyDome):
    """Virtual skydome for daylight coefficient studies with constant radiance.

    Use this sky to calculate daylight matrix.
    """
    def __init__(self):
        _SkyDome.__init__(self, modifier='void')

    def to_radiance(self, density=1):
        """Radiance definition for SkyDome.

        Args:
            density: Sky patch subdivision density. This values is similar to -m option
                in gendaymtx command. Default is 1 which means 145 sky patches and 1
                patch for the ground.

                One can add to the resolution typically by factors of two (2, 4, 8, ...)
                which yields a higher resolution sky using the Reinhart patch subdivision
                For example, setting density to 4 yields a sky with 2305 patches plus one
                patch for the ground.
        """
        density = typing.int_in_range(density, 1, input_name='Sky subdivision density')
        return '#@rfluxmtx h=u u=Y\n%s\n\n#@rfluxmtx h=r%d u=Y\n%s\n' % (
            self.ground_hemisphere, density, self.sky_hemisphere
        )
