"""Honeybee radiance exceptions."""


class InvalidValueError(ValueError):
    """Invalid input value."""

    def __init__(self, name, value, valid_values=None):
        message = '{}: fatal - invalid input value: {}.'.format(name, value)
        if valid_values is not None:
            message = ' '.join(
                (message, 'valid input values are: {}'.format(valid_values))
            )
        super(InvalidValueError, self).__init__(message)


class MissingArgumentError(Exception):
    """Missing argument error for Radiance commands."""

    def __init__(self, command, arg):
        message = '{}: fatal - missing {} argument.'.format(command, arg)
        super(MissingArgumentError, self).__init__(message)


class ProtectedOptionError(Exception):
    """User tried to set up a protected value."""

    def __init__(self, command, opt):
        message = \
            '{}: -{} is controlled by rfluxmtx' \
            ' and may not be set by user.'.format(command, opt)
        super(ProtectedOptionError, self).__init__(message)


class ExclusiveOptionsError(Exception):
    """User tried to set up two options that cannot be set together."""

    def __init__(self, command, opt_1, opt_2):
        message = \
            '{}: you can either set -{} or -{} not both.'.format(command, opt_1, opt_2)
        super(ExclusiveOptionsError, self).__init__(message)


class EmptyFileError(Exception):
    """Exception for trying to load results from an empty file."""

    def __init__(self, file_path=None):
        message = ''
        if file_path:
            message = 'Failed to load the results form an empty file: {}\n' \
                'Double check inputs and outputs and make sure ' \
                'everything is run correctly.'.format(file_path)

        super(EmptyFileError, self).__init__(message)


class NoDirectValueError(Exception):
    """Exception for trying to load direct values when not available."""

    def __init__(self, name):
        message = 'Direct values are not available for {} simulation.'.format(name)
        super(NoDirectValueError, self).__init__(message)
