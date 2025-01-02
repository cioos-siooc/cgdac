"""This module craft command for GenerateDatasetsXml.sh"""

import os
from unittest.mock import patch

from .utils import add_str, add_nothing_str, str_wrapper

empty_str = ""

class ERDDAPGenerateDatasetsXMLCommandGenerator:
    """Generate command"""
    """
    example for erddap gernerate dataset script variables
        Which EDDType (default="EDDTableFromNcFiles")
        ?
        Starting directory (default="")
        ? 
        File name regex (e.g., ".*\.nc") (default="")
        ?
        Full file name of one file (or leave empty to use first matching fileName) (default="")
        ?
        DimensionsCSV (or "" for default) (default="")
        ?
        ReloadEveryNMinutes (e.g., 10080) (default="")
        ?
        PreExtractRegex (default="")
        ?
        PostExtractRegex (default="")
        ?
        ExtractRegex (default="")
        ?
        Column name for extract (default="")
        ?
        Sorted column source name (default="")
        ?
        Sort files by sourceNames (default="")
        ?
        infoUrl (default="")
        ?
        institution (default="")
        ?
        summary (default="")
        ?
        title (default="")
        ?
        standardizeWhat (-1 to get the class' default) (default="")
        ?
        cacheFromUrl (default=“”)
        ?
    """
    BASH = "bash"
    EDD_TYPE = "EDDTableFromNcFiles"
    RELOAD_EVERY_N_MINUTES = 40320
    NC_FILE_FORMAT = "nothing"

    def __init__(self, generate_datasets_xml_command_path, deployment_dict, dataset_dict, erddap_dict):
        self._generate_datasets_xml_command_path = generate_datasets_xml_command_path
        self.deployment_dict = deployment_dict
        self.dataset_dict = dataset_dict
        self.erddap_dict = erddap_dict

        self._info_url = None
        self._institution = None
        self._summary = None
        self._title = None
        self._data_dir = None
        self._file_name = None

    @property
    def generate_datasets_xml_command_path(self):
        if os.path.exists(self._generate_datasets_xml_command_path):
            return self._generate_datasets_xml_command_path
        raise FileNotFoundError(f"The specified path does not exist: {self._generate_datasets_xml_command_path}")

    @property
    def info_url(self):
        if self._info_url is None:
            self._info_url = self.deployment_dict.get("info_url",None)
        return self._info_url

    @property
    def institution(self):
        if self._institution is None:
            self._institution = self.deployment_dict.get("institution",None)
        return self._institution

    @property
    def summary(self):
        if self._summary is None:
            self._summary = self.deployment_dict.get("summary",None)
        return self._summary

    @property
    def title(self):
        if self._title is None:
            self._title = self.dataset_dict.get("title",None)
        return self._title

    @property
    def data_dir(self):
        if self._data_dir is None:
            user = self.deployment_dict["user"]
            dataset_id = self.dataset_dict["dataset_id"]
            data_root = self.erddap_dict["data_root"]
            self._data_dir = os.path.join(data_root, user, dataset_id)
        return self._data_dir

    @property
    def file_name(self):
        if self._file_name is None:
            file_name = self.dataset_dict.get("file_name",None)
            if not file_name:
                return None
            self._file_name = os.path.join(self.data_dir, file_name)
        return self._file_name


    def generate(self):
        bash_command_format = "{} {} '{}'"
        command_list = [self.EDD_TYPE, self.data_dir, self.NC_FILE_FORMAT, self.file_name, None,
                        self.RELOAD_EVERY_N_MINUTES, None,
                        None, None, None, None, None, self.info_url, self.institution, self.summary, self.title, None, None]
        parameter_str = ''
        for key, item in enumerate(command_list):
            if item is None:
                parameter_str = add_nothing_str(parameter_str)
            else:
                if key != 0:
                    item = item
                parameter_str = add_str(parameter_str, item)

        bash_command = bash_command_format.format(self.BASH, self.generate_datasets_xml_command_path,parameter_str)
        return bash_command