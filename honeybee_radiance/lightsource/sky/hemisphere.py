"""Radiance sky hemisphere."""
import honeybee.typing as typing
import ladybug.futil as futil


class Hemisphere(object):
    """Radiance sky hemisphere.

    Sky hemisphere relies on skyfunc and must be used with one of the
    Radiance sky commands.

    .. code-block:: shell

        skyfunc glow sky_glow
        0
        0
        4 1 1 1 0
        sky_glow source sky
        0
        0
        4 0 0 1 180

    Note:
    For more information see Chapter `6.3.2  Example: CIE Overcast Sky` in
    Rendering with Radiance. The chapter is also accessible online at the
    link below.
    https://www.radiance-online.org/community/workshops/2003-berkeley/presentations/Mardaljevic/rwr_ch6.pdf

    Properties:
        * r_emittance
        * g_emittance
        * b_emittance
        * modifier

    """
    def __init__(self, modifier='skyfunc'):
        """Create sky hemisphere.

        Args:
            modifier: Optional input to change the modifier from skyfunc.

        """
        self.modifier = modifier
        self._r_emittance = 1.0
        self._g_emittance = 1.0
        self._b_emittance = 1.0

    @property
    def r_emittance(self):
        """Sky hemisphere emittance values for red channel (Default is 1.0)."""
        return self._r_emittance

    @r_emittance.setter
    def r_emittance(self, value):
        self._r_emittance = typing.float_in_range(value, 0, 1, 'r_emittance')

    @property
    def g_emittance(self):
        """Sky hemisphere emittance values for green channel (Default is 1.0)."""
        return self._g_emittance

    @g_emittance.setter
    def g_emittance(self, value):
        self._g_emittance = typing.float_in_range(value, 0, 1, 'g_emittance')

    @property
    def b_emittance(self):
        """Sky hemisphere emittance values for blue channel (Default is 1.0)."""
        return self._b_emittance

    @b_emittance.setter
    def b_emittance(self, value):
        self._b_emittance = typing.float_in_range(value, 0, 1, 'b_emittance')

    @property
    def modifier(self):
        "Sky hemisphere modifier."
        return self._modifier

    @modifier.setter
    def modifier(self, value):
        "Sky hemisphere modifier."
        self._modifier = str(value)

    @classmethod
    def from_dict(cls, input_dict):
        """Create sky_hemisphere from_dict.

        Args:
            input_dict: A python dictionary in the following format

        .. code-block:: python

                {
                'type': 'SkyHemisphere',
                'r_emittance': r_emittance,
                'g_emittance': g_emittance,
                'b_emittance': b_emittance,
                'modifier': modifier
                }
        """
        assert 'type' in input_dict, \
            'Input dict is missing type. Not a valid sky_hemisphere dictionary.'
        assert input_dict['type'] == 'SkyHemisphere', \
            'Input type must be SkyHemisphere not %s' % input_dict['type']
        sky_hemisphere = cls()
        sky_hemisphere.r_emittance = input_dict['r_emittance']
        sky_hemisphere.g_emittance = input_dict['g_emittance']
        sky_hemisphere.b_emittance = input_dict['b_emittance']
        sky_hemisphere.modifier = input_dict['modifier']
        return sky_hemisphere

    def to_file(self, folder='.', name=None, mkdir=False):
        """Write sky hemisphere to a sky_hemisphere.rad Radiance file.

        Args:
            folder: Target folder.
            name: File name.
            mkdir: A boolean to note if the directory should be created if doesn't
                exist (default: False).

        Returns:
            Full path to the newly created file.
        """
        content = self.to_radiance() + '\n'
        name = typing.valid_string(name) if name else 'sky_hemisphere.rad'
        return futil.write_to_file_by_name(folder, name, content, mkdir)

    def to_radiance(self):
        """Get sky hemisphere as a Radiance input string."""
        sky_hemisphere = '%s glow sky_glow\n0\n0\n4 %.3f %.3f %.3f 0\n' \
            'sky_glow source sky\n0\n0\n4 0 0 1 180' % (
                self._modifier, self.r_emittance, self.g_emittance, self.b_emittance
            )

        return sky_hemisphere

    def to_dict(self):
        """Translate sky hemisphere to a dictionary."""
        return {
            'type': 'SkyHemisphere',
            'r_emittance': self.r_emittance,
            'g_emittance': self.g_emittance,
            'b_emittance': self.b_emittance,
            'modifier': self.modifier
        }

    def __eq__(self, value):
        if type(value) != type(self):
            return False
        if (value.modifier, value.r_emittance, value.g_emittance, value.b_emittance) != \
                (self.modifier, self.r_emittance, self.g_emittance, self.b_emittance):
            return False
        return True

    def __ne__(self, value):
        return not self.__eq__(value)

    def __repr__(self):
        return self.to_radiance()
