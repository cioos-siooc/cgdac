import os
import time

from ..draft_dataset_xml_creator import LocalRawDatasetXmlCreator
from ..erddap_dataset_command_generate import ERDDAP2GenerateDatasetsXmlCommandGenerator


class DraftDatasetXmlCreatorFactory:
    DEFAULT_RAW_XML_NAME = 'draft_xml.out'

    def __init__(self, target_netcdf, output_destination_folder, config):
        self.target_netcdf = target_netcdf
        self.output_destination_folder = output_destination_folder
        self._svc_server_controller = None
        self._data_server_controller = None
        self.local_server_handler = None
        self.temp_folder = None
        self.config = config

    def run(self):
        return LocalRawDatasetXmlCreator(self.generate_command(), self.target_netcdf, self.output_destination_folder,
                                         self.get_xml_generation_working_folder())

    def get_xml_generate_script_path(self):
        xml_generator_path = self.config["GENERATE_DATASETS_XML_PROGRAM_PATH"]
        return xml_generator_path

    def get_file_regex(self):
        return ".*\.nc"

    def generate_command(self, info_url=None, institution=None, summary=None):
        # generate prompt free command for generate dataset xml program
        command_generator = self.create_command_generator()

        command = command_generator.generate(file_name_regex=self.get_file_regex(), info_url=info_url,
                                             institution=institution,
                                             summary=summary)
        return command

    def get_xml_generation_working_folder_root(self):
        return self.config["XML_TEMP_FOLDER"]

    def get_xml_generation_working_folder(self):
        # Create a tmp folder name. The actual folder will be created later
        if not self.temp_folder:
            time_stamp = time.time()
            time_stamp_str = str(time_stamp)
            root_folder = self.get_xml_generation_working_folder_root()
            the_path = os.path.join(root_folder, time_stamp_str)
            self.temp_folder = the_path
        return self.temp_folder

    def create_command_generator(self):
        # command generator is a tool which generate no prompt command to feed GenerateERRDAPDATASETXML
        nc_file_path = self.target_netcdf
        nc_file_name = os.path.basename(nc_file_path)
        feeding_nc_file = os.path.join(self.get_xml_generation_working_folder(), nc_file_name)
        output_path = os.path.join(*[self.temp_folder, self.DEFAULT_RAW_XML_NAME])
        return ERDDAP2GenerateDatasetsXmlCommandGenerator(self.get_xml_generate_script_path(),
                                                          feeding_nc_file,
                                                          None, output_path)

    def get_generate_datasets_xml_path(self):
        return self.config.GENERATE_DATASETS_XML_FOLDER_PATH
