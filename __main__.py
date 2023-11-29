import sys
import argparse
import cleanup
from cleanup.management import get_command, commands

COMMAND_CHOICES = [
    command_name for command_name in commands
] + ['all']
DESCRIPTION = "A simple solution to declutter your MacOS system."
def main() -> int:
    _args = sys.argv
    command = _args[1]
    args = _args[2:]
    get_command(command, args=args).run()
    return 0
if __name__ == '__main__':
    sys.exit(main())