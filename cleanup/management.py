import argparse
commands = {}
class Command:
    prog = "cleanup"
    description = "An automation tool that cleanup your system's junks"
    usage="Deafult usage"
    def __init__(self, initial_args):
        self.initials_args = initial_args
    def create_parser(self, *args):
        return argparse.ArgumentParser(
            prog=self.prog,
            description=self.description,
            usage=self.usage
        )
    def parse_known_args(self, parser):
        raise NotImplementedError("Command subclass should implement this method")
    def run(self):
        parser = self.create_parser()
        self.opts = self.parse_known_args(parser)
    def __init_subclass__(cls) -> None:
        command_name = cls.__name__.lower()
        commands[command_name] = cls

def get_command(command_name, args = None):
    command = commands.get(command_name, None)
    if command is None:
        raise argparse.ArgumentError(argument=None,message=f"Invalid command {command_name}. "
                                             f"Choose only from these commands {tuple([command_ for command_ in commands])}")
    return command(args)
