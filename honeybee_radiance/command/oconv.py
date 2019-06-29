"""oconv command."""
from .options.oconv import OconvOptions
from ._command import Command
import warnings
import honeybee.typing as typing


class Oconv(Command):
    """oconv command."""

    __slots__ = ('_inputs',)

    def __init__(self, options=None, output=None, inputs=None):
        """Oconv command.

        Args:
            options: Oconv command (Default: OconvOptions()).
            output: Output file (Default: None).
            inputs: A collection of scene files (Default: [])
        """
        Command.__init__(self, output=output)
        self.inputs = inputs or []
        self.options = options

    @property
    def options(self):
        """Oconv options."""
        return self._options

    @options.setter
    def options(self, value):
        if value is None:
            value = OconvOptions()

        if not isinstance(value, OconvOptions):
            raise ValueError('Expected OconvOptions not {}'.format(type(value)))

        self._options = value

    @property
    def inputs(self):
        """Octree file.

        Get and set inputs files.
        """
        return self._inputs

    @inputs.setter
    def inputs(self, value):
        # ensure inputs is a list of values
        if not isinstance(value, (list, tuple)):
            raise ValueError(
                'Scene must be a collection of path to input files'
                ' not a {}'.format(type(value))
            )
        self._inputs = [typing.normpath(f) for f in value]

    def to_radiance(self, stdin_input=False):
        """Oconv in Radiance format.

        Args:
            stdin_input: A boolean that indicates if the input for this command
                comes from stdin. This is for instance the case when you pipe the input
                from another command (default: False).
        """
        self.validate()

        command_parts = [self.command]

        if self.options:
            command_parts.append(self.options.to_radiance())

        command_parts.append('-' if stdin_input else ' '.join(self.inputs))

        cmd = ' '.join(command_parts)

        if self.pipe_to:
            cmd = ' | '.join((cmd, self.pipe_to.to_radiance(stdin_input=True)))
        elif self.output:
            cmd = ' > '.join((cmd, self.output))

        return ' '.join(cmd.split())

    def validate(self):
        Command.validate(self)
        if len(self.inputs) == 0:
            warnings.warn('oconv: no inputs. the scene will be empty.')
