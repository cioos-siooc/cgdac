import os
import shutil
import tempfile

from .factory import BadFileTranslatorFactory
from .file_controller import FileSystemControllerFactory


class BadFileMonitor:
    def __init__(self, setting, output_dir):
        self.tmp_path = None
        self.output_dir = output_dir
        self.setting = setting

    def run(self) -> None:
        try:
            self.tmp_path = tempfile.mkdtemp()
            BadFileTranslatorFactory.FSC = FileSystemControllerFactory(self.setting)
            bff = BadFileTranslatorFactory(self.tmp_path, self.output_dir)
            bft_list = bff.build_bad_file_translator()
            for bft in bft_list:
                bft.run()
            prune_file_list = bff.need_to_prune_list
            # removed the old CSV bad files
            self.prune_old_files(prune_file_list)
        finally:
            # make sure the tmp file is getting deleted after the process is finished
            if self.tmp_path and os.path.isdir(self.tmp_path):
                shutil.rmtree(self.tmp_path)

    def prune_old_files(self, files):
        for file in files:
            if os.path.isfile(file):
                os.remove(file)
