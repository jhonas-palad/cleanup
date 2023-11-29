from ..management import Command
from argparse import ArgumentParser

class RemoveDuplicates(Command):
    prog="removeduplicate"
    usage="cleanup removeduplicate /path/to/directory"
    description="Remove all duplicates inside the directory"
    
    def parse_known_args(self, parser: ArgumentParser):
        parser.add_argument(
            'dirs', 
            action="store", 
            nargs="+",
            help="Directories you want to remove duplicates"
        )
        return parser.parse_args(self.initials_args)
    def run(self):
        super().run()
        #Perform remove duplicate