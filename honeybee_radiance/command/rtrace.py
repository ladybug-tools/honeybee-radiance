"""rtrace command."""
from .options.rtrace import RtraceOptions
from ._command import Command
import honeybee_radiance.exception as exception
import honeybee.typing as typing


class Rtrace(Command):
    """rtrace command."""

    __slots__ = ('_octree', '_sensors')
    def __init__(self, options=None, output=None, octree=None, sensors=None):
        """Command.

        Args:
            options: Command options. It will be set to Radiance default values if not
                provided by user.
            output: Output file (Default: None).
            octree: Octree file (Default: None).
            sensors: Sensors file (Default: None).
        """
        Command.__init__(self, output=output)
        self.octree = octree
        self.options = options
        self.sensors = sensors

    @property
    def options(self):
        """Rtrace options."""
        return self._options

    @options.setter
    def options(self, value):
        if value is None:
            value = RtraceOptions()

        if not isinstance(value, RtraceOptions):
            raise ValueError('Expected RtraceOptions not {}'.format(type(value)))

        self._options = value

    @property
    def octree(self):
        """Octree file."""
        return self._octree

    @octree.setter
    def octree(self, value):
        if value is None:
            self._octree = value
        else:
            self._octree = typing.normpath(value)

    @property
    def sensors(self):
        """Sensor file."""
        return self._sensors

    @sensors.setter
    def sensors(self, value):
        if value is None:
            self._sensors = None
        else:
            self._sensors = typing.normpath(value)

    def to_radiance(self, stdin_input=False):
        """Command in Radiance format.
        
        Args:
            stdin_input: A boolean that indicates if the input for this command
                comes from stdin. This is for instance the case when you pipe the input
                from another command (default: False).
        """
        self.validate(stdin_input)

        command_parts = [self.command, self.options.to_radiance(), self.octree]
        cmd = ' '.join(command_parts)
        if not stdin_input and self.sensors:
            cmd = ' < '.join((cmd, self.sensors))
        if self.pipe_to:
            cmd = ' | '.join((cmd, self.pipe_to.to_radiance(stdin_input=True)))
        elif self.output:
            cmd = ' > '.join((cmd, self.output))

        return ' '.join(cmd.split())

    def validate(self, stdin_input=False):
        Command.validate(self)
        if self.octree is None:
            raise exception.MissingArgumentError(self.command, 'octree')
        if not stdin_input and not self.sensors:
            raise exception.MissingArgumentError(self.command, 'sensors')
