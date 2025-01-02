"""
This class serves as the carrier of dataset XML information within this module.
It contains detailed information about a dataset XML and provides details on how to edit the dataset metadata.
"""

from typing import TypedDict, Optional, List
from typing import Dict, List
from .dataset_modify_actions import DatasetModifyActionList
from ..errdap_dataset_configuration_helper import dataset_xml_editor

edit_list = Dict[str, object]


class DatasetCatalogHeader(TypedDict):
    """
    one dataset header example:
    <dataset type="EDDTableFromNcFiles" datasetID="datasets_f93d_926a_4e63" active="true">
    """
    type: str  # Field "type" must be a string
    datasetID: str  # Field "datasetID" must be a string
    active: bool  # Field "active" must be a boolean


class DatasetConfig(TypedDict):
    """
    <accessibleViaFiles>True</accessibleViaFiles>
    <reloadEveryNMinutes>40320</reloadEveryNMinutes>
    <updateEveryNMillis>0</updateEveryNMillis>
    <fileDir>example_path</fileDir>
    <fileNameRegex>example_nc</fileNameRegex>
    <recursive>true</recursive>
    <pathRegex>.*</pathRegex>
    <metadataFrom>last</metadataFrom>
    <standardizeWhat>0</standardizeWhat>
    <sortedColumnSourceName>time</sortedColumnSourceName>
    <sortFilesBySourceNames>time</sortFilesBySourceNames>
    <fileTableInMemory>false</fileTableInMemory>
    """
    accessibleViaFiles: bool
    reloadEveryNMinutes: str
    updateEveryNMillis: str
    fileDir: str
    fileNameRegex: str
    recursive: str
    pathRegex: str
    metadataFrom: str
    standardizeWhat: str
    sortedColumnSourceName: str
    sortFilesBySourceNames: str
    fileTableInMemory: str


class AddAttributes(TypedDict):
    # Define the structure of the nested dictionary
    key: str
    value: str


class DataVariable(TypedDict):
    """
    example of a data variable dict
    {'addAttributes': {'_FillValue': {'name': '_FillValue', 'text': 'NaN', 'type': 'double'},
                   'calendar': {'name': 'calendar', 'text': 'gregorian'},
                    'long_name': {'name': 'long_name', 'text': 'Time'},
                   'observation_type': {'name': 'observation_type', 'text': 'measured'},
                   'standard_name': {'name': 'standard_name', 'text': 'time'},
                   'units': {'name': 'units', 'text': 'seconds since 1970-01-01T00:00:00Z'},
                   'valid_max': {'name': 'valid_max', 'text': '1.634913977799E9', 'type': 'double'},
                   'valid_min': {'name': 'valid_min', 'text': '1.634913918794E9', 'type': 'double'}},
    'dataType': 'double',
    'destinationName': 'time',
    'sourceName': 'time'
    }

     """
    sourceName: str
    destinationName: str
    dataType: str
    addAttributes: Optional[Dict[str, Dict[str, str]]]


DataVariableList = List[DataVariable]


class DatasetXmlContainer:
    def __init__(self, dataset_editor: dataset_xml_editor):
        self._dataset_header = None
        self._dataset_config = None
        self._dataset_global = None
        self._data_variable_list = None
        self.action_list = DatasetModifyActionList()
        self.dataset_editor = dataset_editor

    @property
    def dataset_header(self):
        return dict(self.dataset_editor.get_header())

    @property
    def dataset_config(self):
        return self.dataset_editor.get_all_attr()

    @property
    def dataset_global(self):
        return self.dataset_editor.get_all_global_attr(read_comments=True)

    @property
    def data_variable_list(self):
        return self.dataset_editor.get_all_data_variables(read_comments=True)
