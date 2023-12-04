import sys
import os
from ..colors import textclr, Color
from ..management import Command
from argparse import ArgumentParser
from filecmp import cmp
from tqdm import tqdm
import time
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
    @property
    def directories(self):
        if not hasattr(self,"_directories"):
            self._directories = self.opts.dirs
        
        for _dir in self._directories:
            abs_dir = _dir
            if not os.path.isabs(_dir):
                abs_dir = os.path.abspath(os.path.expanduser(_dir))
            if not os.path.isdir(abs_dir):
                continue
            yield abs_dir
    def run(self):
        """
        1. Traverse each directories passed in the arguments
        2. Search for duplicate files
        3. Choose the base file whose filename is the shortest of the duplicate files.
        4. Remove each duplicates and leave the base file.
        """
        super().run()
        self._directories = self.opts.dirs
        self.recursive = self.opts.recursive
        self.handle()
    def handle(self):
        directories = self.directories
        
        for _dir in directories:
            duplicates_list = self.find_duplicates(_dir)
            if not duplicates_list:
                sys.stdout.write("> %s:\n  %s\n" % (_dir, textclr("No duplicates found", Color.LIGHT_PURPLE.value)))
                continue
            total_files = len(duplicates_list)
            for i in duplicates_list:
                
                sorted_duplicate_list = sorted(i, key=lambda x: -len(x) , reverse=True)
                
                base_filepath = sorted_duplicate_list[0]
                
                self.map_file_duplicates(
                    base_filepath,
                    sorted_duplicate_list[1:]
                )
                self._remove_duplicates(base_filepath)
    
            
    def _remove_duplicates(self, filepath):
        directory = os.path.dirname(filepath)
        filename = os.path.basename(filepath)
        duplicates = self.file_duplicates.get(filepath)
        total_duplicates = len(duplicates)
        
        for duplicate_file in tqdm(duplicates, 
                                   total=total_duplicates, 
                                   desc=f"Removing duplicates of {textclr(filename, Color.LIGHT_GREEN.value)} in {textclr(filename, Color.LIGHT_PURPLE.value)}"):
            if os.path.exists(duplicate_file):
                os.remove(duplicate_file)

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