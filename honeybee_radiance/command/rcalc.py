"""rcalc command."""
from .options.rcalc import RcalcOptions
from ._command import Command
import warnings
import honeybee.typing as typing
try:
    basestring
except NameError:
    basestring = str


class Rcalc(Command):
    """rcalc command.
    
    Rcalc transforms "records" from each file according to the given set of literal and
    relational information. By default, records are separated by newlines, and contain
    numeric fields separated by tabs. The -tS option is used to specify an alternate tab
    character.

    See RcalcOptions for more information.
    """

    __slots__ = ('_inputs',)

    def __init__(self, options=None, output=None, inputs=None):
        """Rcalc command.

        Args:
            options: Rcalc command (Default: RcalcOptions()).
            output: Output file (Default: None).
            inputs: A collection of scene files (Default: [])
        """
        Command.__init__(self, output=output)
        self.inputs = inputs or []
        self.options = options

    @property
    def options(self):
        """Rcalc options."""
        return self._options

    @options.setter
    def options(self, value):
        if value is None:
            value = RcalcOptions()

        if not isinstance(value, RcalcOptions):
            raise ValueError('Expected RcalcOptions not {}'.format(type(value)))

        self._options = value

    @property
    def inputs(self):
        """Octree file.

        Get and set inputs files.
        """
        return self._inputs

    @inputs.setter
    def inputs(self, value):
        if isinstance(value, basestring):
            value = [value]
        self._inputs = [typing.normpath(f) for f in value]

    def to_radiance(self, stdin_input=False):
        """Rcalc in Radiance format.

        Args:
            stdin_input: A boolean that indicates if the input for this command
                comes from stdin. This is for instance the case when you pipe the input
                from another command (default: False).
        """
        self.validate()

        command_parts = [self.command]

        if self.options:
            command_parts.append(self.options.to_radiance())

        command_parts.append('' if stdin_input else ' '.join(self.inputs))

        cmd = ' '.join(command_parts)

        if self.pipe_to:
            cmd = ' | '.join((cmd, self.pipe_to.to_radiance(stdin_input=True)))
        elif self.output:
            cmd = ' > '.join((cmd, self.output))

        return ' '.join(cmd.split())

    def validate(self):
        Command.validate(self)
        if len(self.inputs) == 0:
            warnings.warn('rcalc: no inputs.')
