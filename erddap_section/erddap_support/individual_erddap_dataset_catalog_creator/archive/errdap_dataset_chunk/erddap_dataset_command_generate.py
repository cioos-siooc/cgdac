"""This module craft command for GenerateDatasetsXml.sh"""

import os
from .utils import add_str, add_nothing_str, str_wrapper

empty_str = ""


class ERDDAP1GenerateDatasetsXmlCommandGenerator:
    """Generate command"""
    EDD_TYPE = "EDDTableFromNcFiles"
    RELOAD_EVERY_N_MINUTES = 40320

    def __init__(self, generate_datasets_xml_command_path, nc_file_name, dataset_title, output_path):
        self.program_path = generate_datasets_xml_command_path
        self.file_name = nc_file_name
        self.testing_mission = None
        self.output_path = output_path
        self.dataset_title = dataset_title
        self._data_dir = None

    @property
    def data_dir(self):
        if self._data_dir is None:
            self._data_dir = os.path.dirname(self.file_name)
        return self._data_dir

    def generate(self, info_url, institution, summary):
        command_list = [self.program_path, self.EDD_TYPE, self.data_dir, ".*\.nc", self.file_name, None,
                        self.RELOAD_EVERY_N_MINUTES, None,
                        None, None, None, None, None, info_url, institution, summary, self.dataset_title]
        command = ""
        for key, item in enumerate(command_list):
            if item is None:
                command = add_nothing_str(command)
            else:
                if key != 0:
                    item = str_wrapper(item)
                command = add_str(command, item)

        command = add_str(command, ">")
        command = add_str(command, self.output_path)
        return command


class ERDDAP2GenerateDatasetsXmlCommandGenerator(ERDDAP1GenerateDatasetsXmlCommandGenerator):
    """Generate prompt free command for erddap GenerateDatasetsXml.sh script
    GenerateDatasetsXml is a command line program that can generate a rough
    draft of the dataset XML for almost any type of dataset.
    """

    @property
    def starting_directory(self):
        if self._data_dir is None:
            self._data_dir = os.path.dirname(self.file_name)
        return self._data_dir

    def generate(self, file_name_regex=None, info_url=None, institution=None, summary=None):
        "Generate prompt free Generate dataset command"
        """
        example for erddap2 gernerate dataset script
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
        file_name_regex = file_name_regex
        # None in here means use default
        command_list = [self.program_path,
                        self.EDD_TYPE,
                        self.starting_directory,
                        file_name_regex,  # File name regex
                        self.file_name,
                        None,  # DimensionsCSV
                        self.RELOAD_EVERY_N_MINUTES,
                        None,  # PreExtractRegex
                        None,  # PostExtractRegex
                        None,  # ExtractRegex
                        None,  # Column name for extract
                        None,  # Sorted column source name
                        None,  # Sort files by sourceNames
                        info_url,
                        institution,
                        summary,
                        self.dataset_title,
                        None,  # standardizeWhat
                        None  # cacheFromUrl
                        ]
        command = "cd {} && ".format(os.path.dirname(self.program_path))
        for key, item in enumerate(command_list):
            if item is None:
                command = add_nothing_str(command)
            else:
                if key != 0:
                    item = str_wrapper(item)
                command = add_str(command, item)
        return command


class ERDDAPGenerateDatasetsXmlParameterGenerator:
    """Generate prompt free command for erddap GenerateDatasetsXml.sh script
    GenerateDatasetsXml is a command line program that can generate a rough
    draft of the dataset XML for almost any type of dataset.
    """
    """Generate command"""
    EDD_TYPE = "EDDTableFromNcFiles"
    RELOAD_EVERY_N_MINUTES = 40320

    def __init__(self, generate_datasets_xml_command_path, nc_file_name, dataset_title, output_path, extra=None):
        self.program_path = generate_datasets_xml_command_path
        self.file_name = nc_file_name
        self.testing_mission = None
        self.output_path = output_path
        self.dataset_title = dataset_title
        self._data_dir = None

    @property
    def starting_directory(self):
        if self._data_dir is None:
            self._data_dir = os.path.dirname(self.file_name)
        return self._data_dir

    def generate(self, file_name_regex=None, info_url=None, institution=None, summary=None):
        " Generate prompt free Generate dataset command"
        """
        example for erddap2 gernerate dataset script
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
        file_name_regex = file_name_regex
        # None in here means use default
        parameter_list = [self.EDD_TYPE,
                          self.starting_directory,
                          file_name_regex,  # File name regex
                          self.file_name,
                          None,  # DimensionsCSV
                          self.RELOAD_EVERY_N_MINUTES,
                          None,  # PreExtractRegex
                          None,  # PostExtractRegex
                          None,  # ExtractRegex
                          None,  # Column name for extract
                          None,  # Sorted column source name
                          None,  # Sort files by sourceNames
                          info_url,
                          institution,
                          summary,
                          self.dataset_title,
                          None,  # standardizeWhat
                          None  # cacheFromUrl
                          ]
        command = "cd {} && ".format(os.path.dirname(self.program_path))
        for key, item in enumerate(parameter_list):
            if item is None:
                command = add_nothing_str(command)
            else:
                if key != 0:
                    item = str_wrapper(item)
                command = add_str(command, item)
        return command
