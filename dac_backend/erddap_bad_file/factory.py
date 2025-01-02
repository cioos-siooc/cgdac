import os
from typing import List, Dict


from .bad_file_to_nc import BadFileTranslator


class BadFileTranslatorFactory:
    """
    For glider we have three type of glider id
    bond_20190724_102_delayed
    dal556_20190814_103_realtime
    cabot_20200601_110_delayed_test
    and errdap create dataset cache file folder base on last to letter,
    so we have ed me and st for glider datasets
    """
    GLIDER_CAHCE_DIRECTORY = "*"
    FSC = None

    def __init__(self, nc_bad_file_folder, output_dir):
        self.nc_bad_files_folder = nc_bad_file_folder
        self.svc_server_controller = self.FSC.get_controller("svc_server_controller")
        self.download_handler = self.FSC.get_controller("svc_download_controller")
        self.need_to_prune_list = []
        self.output_dir = output_dir

    def find_glider_bad_files(self) -> List[str]:
        # get all bad files
        all_bad_files = self.svc_server_controller.find_all_bad_files()
        # find the bad files for gliders
        glider_bad_files = self.filter_for_glider_bad_files(all_bad_files)
        return glider_bad_files

    def get_bad_file_dataset_id_from_path(self, bad_file_path):
        normalized_path = os.path.normpath(bad_file_path)
        path_components = normalized_path.split(os.sep)
        return path_components[-2]

    def filter_for_glider_bad_files(self, paths) -> List[str]:
        glider_ext = self.GLIDER_CAHCE_DIRECTORY
        glider_badfiles = []
        for path in paths[0]:  # todo: replace the hardcode number
            normalized_path = os.path.normpath(path)
            path_components = normalized_path.split(os.sep)
            e = path_components[-3]  # todo: replace the hardcode number
            if glider_ext == "*" or e in glider_ext:
                glider_badfiles.append(path)
        return glider_badfiles

    def find_badfiles_modified_time(self, bad_file_paths_on_remote) -> Dict[str, int]:
        modified_timestamp = {}
        for f in bad_file_paths_on_remote:
            res = self.svc_server_controller.get_file_modified(f)[0]
            modified_timestamp[f] = int(res[2])
        return modified_timestamp

    def discover_files_under_dir(self, file_dir: str) -> list:
        paths = []
        if os.path.isdir(file_dir):
            for file in os.listdir(file_dir):
                file_path = os.path.join(file_dir, file)
                if os.path.isfile(file_path):
                    paths.append(file_path)
        return paths

    def get_csv_bad_file_dir(self):
        return self.output_dir

    def find_local_xml_bad_files(self) -> List[str]:
        # find out the CSV bad files we already have
        files = self.discover_files_under_dir(self.get_csv_bad_file_dir())
        csv_files = []
        for file in files:
            if file.endswith("xml"):
                csv_files.append(file)
        return csv_files

    def download_bad_files(self, file_paths, output_dir):
        ret = {}
        for file_path in file_paths:
            dataset_is = self.get_bad_file_dataset_id_from_path(file_path)
            output_path = os.path.join(output_dir, "badFiles-{}.nc".format(dataset_is))
            self.download_handler.download_file_from_erddap(file_path=file_path, dest_path=output_path)
            self.download_handler.commit()
            ret[dataset_is] = {"output_path": output_path, "download_file_path": file_path}
        return ret

    def make_badfile_csv_name(self, dataset_id, modified_time):
        file_name_format = "{}-{}-{}.xml"
        file_name = file_name_format.format(dataset_id, "badFiles", modified_time)
        return file_name

    def covert_file_name_to_list(self, file_path):
        file_name_with_ext = os.path.basename(file_path)
        file_name, ext = os.path.splitext(file_name_with_ext)
        dataset_id, _, timestamp = file_name.split("-")
        return dataset_id, timestamp

    def find_bad_files_that_should_be_update_or_create(self, bad_files_modified_time: Dict[str, int],
                                                       local_csv_bad_files: List[str]) -> List[str]:

        dataset_id_and_timestamp_dict = {}
        for xml_file in local_csv_bad_files:
            dataset_id, timestamp = self.covert_file_name_to_list(xml_file)
            dataset_id_and_timestamp_dict[dataset_id] = timestamp
        bad_file_need_to_update_list = []
        for bad_file_path, modified_time in bad_files_modified_time.items():
            dataset_id = self.get_bad_file_dataset_id_from_path(bad_file_path)
            if dataset_id in dataset_id_and_timestamp_dict:
                if int(modified_time) != int(dataset_id_and_timestamp_dict[dataset_id]):
                    bad_file_need_to_update_list.append(bad_file_path)
            else:
                bad_file_need_to_update_list.append(bad_file_path)

        return bad_file_need_to_update_list

    def find_local_bad_files(self, dir):
        file_paths = self.discover_files_under_dir(dir)
        bad_file_nc = []
        for file in file_paths:
            if file.endswith("nc"):
                bad_file_nc.append(file)
        return bad_file_nc

    def create_prune_list(self, dataset_id, local_bad_file_csv):
        for file_path in local_bad_file_csv:
            file_name = os.path.basename(file_path)
            if file_name.startswith(dataset_id):
                self.need_to_prune_list.append(file_path)

    def clean_resolved_bad_file(self, current_bad_file_list, local_bad_file_doc_list):
        dataset_id_list = []
        for bad_file_path in current_bad_file_list:
            dataset_id = self.get_bad_file_dataset_id_from_path(bad_file_path)
            dataset_id_list.append(dataset_id)

        for file_path in local_bad_file_doc_list:
            for dataset_id in dataset_id_list:
                file_name = os.path.basename(file_path)
                if file_name.startswith(dataset_id):
                    break
            else:
                if file_path not in self.need_to_prune_list:
                    self.need_to_prune_list.append(file_path)

    def get_prune_file_list(self):
        return self.need_to_prune_list

    def find_local_bad_file_summaries(self):
        # find out the CSV bad files we already have
        files = self.discover_files_under_dir(self.get_csv_bad_file_dir())
        summary_txt = []
        for file in files:
            if file.endswith("_summary.txt"):
                summary_txt.append(file)
        return summary_txt

    def build_bad_file_translator(self) -> List[BadFileTranslator]:
        # find all glider bad files
        glider_bad_files = self.find_glider_bad_files()
        # find the modified timestamp of bad files
        glider_bad_files_modified_timestamp = self.find_badfiles_modified_time(glider_bad_files)
        local_bad_file_xml = self.find_local_xml_bad_files()
        local_bad_file_summaries = self.find_local_bad_file_summaries()
        local_bad_file_docs = local_bad_file_xml + local_bad_file_summaries
        need_to_update_bad_files_name_list = self.find_bad_files_that_should_be_update_or_create(
            glider_bad_files_modified_timestamp,
            local_bad_file_xml)
        downloaded_nc_badfiles_dict = self.download_bad_files(need_to_update_bad_files_name_list,
                                                              self.nc_bad_files_folder)

        translator_list = []
        for dataset_id, path_value_dict in downloaded_nc_badfiles_dict.items():
            modify_timestamp = glider_bad_files_modified_timestamp[path_value_dict["download_file_path"]]
            output_name = self.make_badfile_csv_name(dataset_id, modify_timestamp)
            output_path = os.path.join(self.get_csv_bad_file_dir(), output_name)
            translator_list.append(BadFileTranslator(path_value_dict["output_path"], dataset_id, output_path))
            # should remove the files that has newer version
            self.create_prune_list(dataset_id, local_bad_file_xml)
        # should remove the files which has been resolved
        self.clean_resolved_bad_file(glider_bad_files, local_bad_file_docs)
        return translator_list
