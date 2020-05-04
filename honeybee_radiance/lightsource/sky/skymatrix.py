"""Generate a point-in-time climate-based sky."""
from __future__ import division

from .sunmatrix import SunMatrix
import honeybee.typing as typing
from ladybug.wea import Wea


class SkyMatrix(SunMatrix):
    """Annual Climate-based Sky matrix.

    The output of SkyMatrix is similar to using command Radiance's gendaymtx command with
    default options. For more information see gendaymtx documentation.

    https://www.radiance-online.org/learning/documentation/manual-pages/pdfs/gendaymtx.pdf

    Args:
        wea: A Ladybug wea object.
        north: A number between -360 and 360 for the counterclockwise difference between
            the North and the positive Y-axis in degrees. 90 is West and 270 is East
            (Default: 0)
        density: Sky patch subdivision density. This values is similar to -m option
            in gendaymtx command. Default is 1 which means 145 sky patches and 1
            patch for the ground.

            One can add to the resolution typically by factors of two (2, 4, 8, ...)
            which yields a higher resolution sky using the Reinhart patch subdivision
            For example, setting density to 4 yields a sky with 2305 patches plus one
            patch for the ground.

    Properties:
        * wea
        * location
        * north
        * is_point_in_time
        * is_climate_based
    """

    __slots__ = ('_density',)

    def __init__(self, wea, north=0, density=1):
        """Create a climate-based sky matrix."""
        SunMatrix.__init__(self, wea, north)
        self.density = density

    @property
    def density(self):
        """Set and get sky patch subdivision density.

        This values is similar to -m option in gendaymtx command. Default is 1 which
        means 145 sky patches and 1 patch for the ground.

        One can add to the resolution typically by factors of two (2, 4, 8, ...) which
        yields a higher resolution sky using the Reinhart patch subdivision. For example,
        setting density to 4 yields a sky with 2305 patches plus one patch for the
        ground.
        """
        return self._density

    @density.setter
    def density(self, value):
        typing.int_in_range(value, 1, input_name='SkyMatrix subdivision density')
        self._density = value

    @classmethod
    def from_dict(cls, input_dict):
        """Create the sky from a dictionary.

        Args:
            input_dict: A python dictionary in the following format

        .. code-block:: python

                {
                'type': 'SkyMatrix',
                'wea': {},
                'north': 0.0  # optional
                'density': 1  # optional
                }
        """
        if 'type' not in input_dict or input_dict['type'] != 'SkyMatrix':
            raise ValueError('Input dict "type" must be "SkyMatrix".')
        if 'north' in input_dict:
            north = input_dict['north']
        else:
            north = 0
        if 'density' in input_dict:
            density = input_dict['density']
        else:
            density = 1

        sky = cls(Wea.from_dict(input_dict['wea']), north, density)

        return sky

    # TODO: add support for additional parameters
    # TODO: add gendaymtx to radiance-command and use it for validating inputs
    def to_radiance(
            self, output_type=0, wea_file=None, output_name=None, cumulative=False,
            components=0):
        """Return Radiance command to generate the sky.

        Note that you need to write the wea to a file (in.wea) before running this
        command.

        Alternatively you can use write method which will write the wea data to a file.

        Args:
            output_type: An integer between 0 to 1 for output type.
                * 0 = output in W/m2/sr visible (default)
                * 1 = output in W/m2/sr solar
            wea_file: Path to wea file (default: in.wea).
            output_name: A name for output files (default: sky_mtx).
            cumulative: A boolean to generate cumulative sky. This option is only
                available in Radiance 5.3 and higher versions (default: False).
            components: An integer between 0-2 to note the distribution of which
                components should be included. 0 might be used to include both sun and
                sky contribution. 1 may be used to produce a sun-only matrix, with no sky
                contributions.  Alternatively, 2 may be used to exclude any sun component
                from the output.  If there is a sun in the description, gendaymtx will
                include its contribution in the four nearest sky patches, distributing
                energy according to centroid proximity (default: 0).
        """
        output_type = typing.int_in_range(output_type, 0, 1, 'SkyMatrix output type')
        wea_file = wea_file or 'in.wea'
        output_name = output_name or 'sky'

        options = ['-O{}'.format(output_type)]
        if self.density != 1:
            options.append('-m %d' % self.density)
        if self.north != 0:
            options.append('-r {}'.format(self.north))
        if cumulative:
            options.append('-A')
        if components == 1:
            # sun-only
            options.append('-d')
        elif components == 2:
            # sky only
            options.append('-s')
        options.append(wea_file)
        # add all the other options here
        command = 'gendaymtx {0} > {1}.mtx'.format(' '.join(options), output_name)

        return command

    def to_dict(self):
        """Translate this matrix to a dictionary."""

        return {
            'type': 'SkyMatrix',
            'wea': self.wea.to_dict(),
            'north': self.north,
            'density': self.density
        }

    def __eq__(self, value):
        if type(value) != type(self) \
            or value.wea != self.wea \
            or value.north != self.north \
                or value.density != self.density:
            return False
        return True
