from ..colors import textclr, Color
from ..management import Command
import sys
import os
from argparse import ArgumentParser
from filecmp import cmp
from tqdm import tqdm
import time
class RemoveDuplicate(Command):
    prog="removeduplicate"
    usage="./cleanup_bin removeduplicate [.../path/to/directory]"
    description="Remove all duplicates inside the directory"
    default_dirs = ['~/Downloads', '~/Documents']
    def __init__(self, *args):
        super().__init__(*args)
        self.file_duplicates = {}
    def parse_known_args(self, parser: ArgumentParser):
        parser.add_argument(
            '--dirs', 
            action="store", 
            nargs="+",
            default=[],
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
        
        directories = set(self._directories)
        
        if self.recursive:
            for directory in directories.copy():
                directories.update([root for root, _1, _2 in os.walk(directory)])
        for _dir in directories:
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
        self._directories = self.opts.dirs or self.default_dirs
        self.recursive = self.opts.recursive
        self.handle()
    def handle(self):
        directories = self.directories
        
        for _dir in directories:
            duplicates_list = self.find_duplicates(_dir)
            sys.stdout.write(
                f"> {_dir}:\n"
            )
            if not duplicates_list:
                sys.stdout.write("  %s\n" % (textclr("No duplicates found", Color.LIGHT_PURPLE.value)))
                continue
            for i in duplicates_list:
                
                sorted_duplicate_list = sorted(i, key=lambda x: -len(x) , reverse=True)
                
                base_filepath = sorted_duplicate_list[0]
                
                self.map_file_duplicates(
                    base_filepath,
                    sorted_duplicate_list[1:]
                )
                self._remove_duplicates(base_filepath)

    def _remove_duplicates(self, filepath):
        filename = os.path.basename(filepath)
        duplicates = self.file_duplicates.get(filepath)
        total_duplicates = len(duplicates)
        sys.stdout.write("  Duplicate files of %s:\n\t- %s\n" % (
            textclr(filename, Color.LIGHT_GREEN.value),
            '\n\t- '.join([textclr(os.path.basename(duplicate), Color.LIGHT_GREEN.value) for duplicate in duplicates])))
        for duplicate_file in tqdm(duplicates, 
                                   total=total_duplicates, 
                                   desc="  Removing duplicates"):
            if os.path.exists(duplicate_file):
                os.remove(duplicate_file)
            time.sleep(0.3)
    def map_file_duplicates(self, base_filepath, duplicates):
        if not isinstance(duplicates, list):
            raise TypeError(f"{duplicates} should be type of {list.__name__}")
        self.file_duplicates[base_filepath] = duplicates
    def find_duplicates(self, directory):
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