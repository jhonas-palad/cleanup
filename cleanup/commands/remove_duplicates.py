import sys
import os
from ..colors import textclr, Color
from ..management import Command
from argparse import ArgumentParser
from filecmp import cmp


class RemoveDuplicate(Command):
    prog="removeduplicate"
    usage="./cleanup_bin removeduplicate [.../path/to/directory]"
    description="Remove all duplicates inside the directory"
    def __init__(self, *args):
        super().__init__(*args)
        self._skipped_dirs = set()
        self._valid_dirs = set()
        self.file_duplicates = {}
    def parse_known_args(self, parser: ArgumentParser):
        parser.add_argument(
            'dirs', 
            action="store", 
            nargs="+",
            help="Directories you want to remove duplicates"
        )
        parser.add_argument(
            '-r',
            '--recursive',
            dest='recursive',
            default=False,
            action='store_true',
        )
        return parser.parse_args(self.initials_args)
    def run(self):
        super().run()
        self._directories = self.opts.dirs
        self.recursive = self.opts.recursive

        for _dir in self.directories:
            sys.stdout.write(f"Checking duplicates in {textclr(_dir, Color.LIGHT_PURPLE.value)}:\n")
            duplicates_list = self.find_duplicates(_dir)
            for i in duplicates_list:
                sorted_duplicate_list = sorted(i, key=lambda x: -len(x) , reverse=True)
                
                base_filepath = sorted_duplicate_list[0]
                
                self.map_file_duplicates(
                    base_filepath,
                    sorted_duplicate_list[1:]
                )
                self._remove_duplicates(base_filepath)
            
            if _dir in [os.path.dirname(filepath) for filepath in self.file_duplicates.keys()]:
                for filepath, duplicates in self.file_duplicates.items():
                    filename = os.path.basename(filepath)
                    sys.stdout.write(
                        f"> Duplicates of {textclr(filename, Color.LIGHT_BLUE.value)} in {textclr(os.path.dirname(filepath),Color.LIGHT_PURPLE.value)}:\n  - "
                        f"{'\n  - '.join([
                            f"{textclr(os.path.basename(filename), Color.LIGHT_BLUE.value)}" for filename in duplicates
                        ])}\n"
                    )
            else:
                sys.stdout.write(f"> {textclr("No duplicates found", Color.LIGHT_GREEN.value)}\n")

    @property
    def directories(self):
        if not hasattr(self,"_directories"):
            self._directories = self.opts.dirs
        if len(self._valid_dirs):
            return self._valid_dirs
        
        for _dir in self._directories:
            abs_dir = _dir
            if not os.path.isabs(_dir):
                abs_dir = os.path.abspath(os.path.expanduser(_dir))
            if not os.path.isdir(abs_dir):
                sys.stdout.write(f"{_dir} is not a directory or path doesn't exist.\n")
                self._skipped_dirs(abs_dir)
                continue
            self._valid_dirs.add(abs_dir)
            #add progress bar
            
        return self._valid_dirs
    def _remove_duplicates(self, filepath):
        duplicates = self.file_duplicates.get(filepath)
        for file in duplicates:
            if not os.path.exists:
                continue
            os.remove(file)

    def map_file_duplicates(self, base_filepath, duplicates):
        if not isinstance(duplicates, list):
            raise TypeError(f"{duplicates} should be type of {list.__name__}")
        self.file_duplicates[base_filepath] = duplicates
    def find_duplicates(self, directory):
        if self.recursive:
            for root, dirs, files in os.walk(directory):
                ...
        else:
            seen_files = []
            for file_name in os.listdir(directory):
                file_path = os.path.join(directory, file_name)
                if not os.path.isfile(file_path):
                    continue
                is_duplicate = False
                for seen_file in seen_files:
                    is_duplicate = cmp(
                        file_path,
                        seen_file[0],
                        shallow=False
                    )
                    if is_duplicate:
                        seen_file.append(file_path)
                        break
                if not is_duplicate:
                    seen_files.append([file_path])
            return [seen for seen in seen_files if len(seen) > 1]