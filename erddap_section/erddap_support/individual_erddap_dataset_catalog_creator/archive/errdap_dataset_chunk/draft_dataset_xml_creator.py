import os
import shutil
import subprocess


class DraftDatasetChunkCreator:
    """
    Generate a draft ERDDAP dataset catalog chunk by using the GenerateDatasetXml.sh
    """

    DEFAULT_RAW_XML_NAME = 'draft_xml.out'

    def __init__(self, program_command, nc_file_path, output_dir, temp_working_dir):
        """
        :param program_command: A prompt free command for XML generate program
        :param nc_file_path: path of netcdf file for generate the draft XML
        :param output_dir: output folder for raw XML
        :param script_path: the path of the program
        :param temp_working_dir: working dir
        """
        self.program_command = program_command
        self.nc_file_path = nc_file_path
        self.erddap_config_output_dir = output_dir
        self.temp_folder = temp_working_dir

    def generate(self):
        """
        Generate a draft xml by using GenerateDatasetXml
        and move it to the working directory
        :return:
        """
        self.set_up_xml_tmp_folder(commit=True)
        self.prepare_sample_nc_file()
        self.generate_raw_xml()
        path = self.download_raw_xml_file()
        self.data_file_cleaning_up()
        return path

    def set_up_xml_tmp_folder(self, commit=False):
        """Create a tmp folder to keep the output result"""
        os.makedirs(self.temp_folder, exist_ok=True)


    def generate_raw_xml(self):
        """Use GenerateDatasetXml to generate the xml"""
        # os.system(self.program_command)
        subprocess.run(self.program_command, shell=True, check=True)
        # self.local_server_handler.script(self.program_command)
        # self.local_server_handler.commit()

    def prepare_sample_nc_file(self):
        """select a nc file for XML config generation"""
        sample_nc_file = os.path.join(self.temp_folder, os.path.basename(self.nc_file_path))
        shutil.copyfile(self.nc_file_path, sample_nc_file)
        return self.nc_file_path

    def download_raw_xml_file(self):
        """move the output xml to data catalog output dir"""
        output_raw_xml_temp_path = os.path.join(self.temp_folder, self.DEFAULT_RAW_XML_NAME)
        output_raw_xml_path = os.path.join(self.erddap_config_output_dir, self.DEFAULT_RAW_XML_NAME)
        if os.path.isfile(output_raw_xml_temp_path):
            os.rename(output_raw_xml_temp_path, output_raw_xml_path)
            return output_raw_xml_path

    def data_file_cleaning_up(self):
        """Cleaning the tmp directory after job done"""
        if os.path.isdir(self.temp_folder):
            shutil.rmtree(self.temp_folder)


class LocalRawDatasetXmlCreator(DraftDatasetChunkCreator):
    ...
