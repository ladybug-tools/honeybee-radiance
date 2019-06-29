from honeybee_radiance.command._command import Command


def test_defaults():
    cmd = Command()
    assert cmd.command == 'command'
    assert cmd.output is None
    assert cmd.pipe_to is None
    assert cmd.to_radiance() == 'command'


def test_output_assignment():
    cmd = Command(output='command.res')
    assert cmd.output == 'command.res'
    assert cmd.to_radiance() == 'command > command.res'


def test_pipe_to():
    cmd_1 = Command(output='command_1.res')
    assert cmd_1.output == 'command_1.res'
    cmd_2 = Command(output='command_2.res')
    cmd_1.pipe_to = cmd_2
    assert cmd_1.to_radiance() == 'command | command > command_2.res'


def test_subclass():

    class Rtrace(Command):
        pass

    rtrace = Rtrace()
    assert rtrace.command == 'rtrace'
