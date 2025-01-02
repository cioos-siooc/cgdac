import os
import shutil
import logging
import subprocess
from typing import Dict
import pty


class DraftDatasetChunkCreator:
    """
    Generate a draft ERDDAP dataset catalog chunk by using the GenerateDatasetXml.sh
    """

    DEFAULT_RAW_XML_NAME = 'dataset_draft.xml'

    def __init__(self, program_command: str, dataset_dict: Dict[str, str], erddap_dict: Dict[str, str],
                 output_dir: str) -> None:
        """
        :param program_command: A prompt free command for XML generate program
        :param nc_file_path: path of netcdf file for generate the draft XML
        :param output_dir: output folder for raw XML
        :param script_path: the path of the program
        :param temp_working_dir: working dir
        """
        self.dataset_XML_generation_command = program_command
        self.dataset_dict = dataset_dict
        self.erddap_dict = erddap_dict
        self.erddap_config_output_dir = output_dir

        self._nc_file_path = None
        self._generate_datasets_xml_out_path = None
        self._output_dir = output_dir
        self._draft_dataset_output_path = None

    @property
    def nc_file_path(self) -> str:
        if self._nc_file_path is None:
            self._nc_file_path = self.dataset_dict["nc_file_path"]
        return self._nc_file_path

    @property
    def draft_output_log_path(self) -> str:
        erddap_big_parents_path = self.erddap_dict["erddap_big_parents_path"]
        erddap_logs_path = os.path.join(erddap_big_parents_path, "logs")
        if self._generate_datasets_xml_out_path is None:
            self._generate_datasets_xml_out_path = os.path.join(erddap_logs_path, "GenerateDatasetsXml.out")
        return self._generate_datasets_xml_out_path

    @property
    def output_dir(self) -> str:
        # if not os.path.isdir(self._nc_file_path):
        #     raise FileNotFoundError(f"The folder '{self._nc_file_path}' does not exist.")
        return self._output_dir

    def generate(self) -> str:
        """
        Generate a draft xml by using GenerateDatasetXml
        and move it to the working directory
        :return:
        """
        self.generate_raw_xml()
        if self.output_validate():
            self.mv_output_to_output_dir()
        return self.draft_dataset_output_path

    def output_validate(self):
        # todo: implment something here to verify if generate datasets xml have reasonable output
        return True

    @property
    def draft_dataset_output_path(self):
        if self._draft_dataset_output_path is None:
            self._draft_dataset_output_path = os.path.join(self.output_dir, self.DEFAULT_RAW_XML_NAME)
        return self._draft_dataset_output_path

    def mv_output_to_output_dir(self) -> None:
        try:
            shutil.copy(self.draft_output_log_path, self.draft_dataset_output_path)
            logging.debug(f"File copied from {self.draft_output_log_path} to {self.output_dir}")
        except FileNotFoundError:
            logging.error(f"Error: The file '{self.draft_output_log_path}' does not exist.")
        except PermissionError:
            logging.error(f"Error: Permission denied while copying to '{self.draft_output_log_path}'.")
        except Exception as e:
            logging.error(f"Error: {e}")

    def generate_raw_xml(self) -> int:
        """Use GenerateDatasetXml to generate the xml"""
        master, slave = pty.openpty()
        try:
            # Execute the command string
            result = subprocess.run(
                self.dataset_XML_generation_command,
                shell=True,
                stdin=slave,
                # stdout=subprocess.PIPE,
                # stderr=subprocess.PIPE,
                # Execute the command in the shell
                capture_output=True,  # Capture stdout and stderr
                text=True,  # Decode output as strings
                check=True  # Raise exception on non-zero exit
            )
            logging.debug("Command output:", result.stdout)
            print("Output:", result.stdout)
            return result.returncode
        except subprocess.CalledProcessError as e:
            logging.error(f"Error: Command failed with return code {e.returncode}")
            logging.error(f"Error output: {e.stderr}")
            print("Error output:", e.stderr)
            raise
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            raise
