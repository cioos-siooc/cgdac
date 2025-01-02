import os
import unittest
from ..dataset_xml_container_generator import DatasetXmlContainerGenerator
from ..dataset_xml_container import DatasetXmlContainer, DatasetCatalogHeader, DatasetConfig


class TestDatasetXMLContainerGenerator(unittest.TestCase):
    def setUp(self):
        self.current_folder_path = os.path.dirname(os.path.abspath(__file__))
        self.resource_path = os.path.join(self.current_folder_path,'resource')
        self.dataset_xml_path = os.path.join(self.resource_path,'dataset_draft.xml')
        self.dataset_dict = {
            "dataset_id": "expect_dataset_id",
        }
        self.dataset_header:DatasetCatalogHeader = {
            "type": "example_type",
            "datasetID": "expect_dataset_id",
            "active": True
        }
        self.dataset_config:DatasetConfig = {
            "accessibleViaFiles": True,
            "reloadEveryNMinutes":"123",
            "updateEveryNMillis": "123",
            "fileDir": "123",
            "fileNameRegex": "qwe",
            "recursive": "example",
            "pathRegex": "example",
            "metadataFrom": "example",
            "standardizeWhat": "example",
            "sortedColumnSourceName": "example",
            "sortFilesBySourceNames": "example",
            "fileTableInMemory": "example",
        }
        self.data_variable_list = []
        self.data_container = DatasetXmlContainer(self.dataset_header, self.dataset_config, {} ,self.data_variable_list, None)

    def tearDown(self):
        ...

    def test_generate_dataset_xml_container_generation(self):
        res = DatasetXmlContainerGenerator(self.dataset_xml_path).generate()
        print(res)


