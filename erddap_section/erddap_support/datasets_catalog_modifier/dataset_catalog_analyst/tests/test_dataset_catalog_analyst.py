import os
import unittest
from ..dataset_xml_container import DatasetXmlContainer, DatasetCatalogHeader, DatasetConfig
from ..dataset_catalog_analyst import  DATASET_ID,  DatasetHeaderAnalyst, DatasetConfigAnalyst

from ..erddap_dataset_name_constants import DATASET_HEADER, DATASET_CONFIG, DATASET_CONFIG_FILE_DIR, DATASET_CONFIG_FILE_NAME_REGEX, DATASET_CONFIG_UPDATE_EVERY_N_MILLIS, ActionDictConstants


class TestDatasetXMLContainerGenerator(unittest.TestCase):
    def setUp(self):
        self.current_folder_path = os.path.dirname(os.path.abspath(__file__))
        self.resource_path = os.path.join(self.current_folder_path, 'resource')
        self.deployment_dict = {}
        self.dataset_dict = {
            DATASET_ID: "expect_dataset_id",
            DATASET_CONFIG_FILE_DIR: "expect_dataset_folder"
        }
        self.dataset_header: DatasetCatalogHeader = {
            "type": "actual_dataset_type",
            DATASET_ID: "actual_dataset_id",
            "active": True
        }
        self.dataset_config: DatasetConfig = {
            "accessibleViaFiles": True,
            "reloadEveryNMinutes": "test_reload_number",
            DATASET_CONFIG_UPDATE_EVERY_N_MILLIS: "test_update_number",
            DATASET_CONFIG_FILE_DIR: "/test/path",
            DATASET_CONFIG_FILE_NAME_REGEX: "qwe",
            "recursive": "example",
            "pathRegex": "example",
            "metadataFrom": "example",
            "standardizeWhat": "example",
            "sortedColumnSourceName": "example",
            "sortFilesBySourceNames": "example",
            "fileTableInMemory": "example",
        }
        self.data_variable_list = []
        self.data_container = DatasetXmlContainer(self.dataset_header, self.dataset_config, {},self.data_variable_list, None)
        self.header_analyst = DatasetHeaderAnalyst(self.data_container, self.deployment_dict, self.dataset_dict)
        self.dataset_config_analyst = DatasetConfigAnalyst(self.data_container, self.deployment_dict, self.dataset_dict)

    def tearDown(self):
        ...

    def test_data_compare_generator(self):
        comparing_mapping_list = {
            DATASET_ID: {
                ActionDictConstants.DATASET: {ActionDictConstants.DATA_SOURCE: ActionDictConstants.DATASET_DICT,
                          ActionDictConstants.DATA_ID: DATASET_ID},
                ActionDictConstants.DATA_CONTAINER: {ActionDictConstants.DATA_SOURCE: DATASET_HEADER,
                                 ActionDictConstants.DATA_ID: DATASET_ID}
            },
        }
        generator = self.analyst.data_compare_generator(comparing_mapping_list)
        expect_value = {ActionDictConstants.ACTUAL_VALUE: 'actual_dataset_id',
                        ActionDictConstants.DATA_FIELD_NAME: DATASET_ID,
                        ActionDictConstants.EXPECTED_VALUE: 'expect_dataset_id',
                        ActionDictConstants.SECTION: DATASET_HEADER}
        res = list(generator)
        self.assertEqual([expect_value], res)

    def test_data_compare_generator_with_multiple_keys(self):
        comparing_mapping_list = {
            DATASET_CONFIG_FILE_DIR: {
                ActionDictConstants.DATASET: {ActionDictConstants.DATA_SOURCE: ActionDictConstants.DATASET_DICT,
                          ActionDictConstants.DATA_ID: DATASET_CONFIG_FILE_DIR},
                ActionDictConstants.DATA_CONTAINER: {ActionDictConstants.DATA_SOURCE: DATASET_CONFIG,
                                 ActionDictConstants.DATA_ID: DATASET_CONFIG_FILE_DIR}
            },
            DATASET_CONFIG_UPDATE_EVERY_N_MILLIS: {
                ActionDictConstants.DATASET: {ActionDictConstants.DATA_SOURCE: ActionDictConstants.DATASET_DICT,
                          ActionDictConstants.DATA_ID: DATASET_CONFIG_UPDATE_EVERY_N_MILLIS},
                ActionDictConstants.DATA_CONTAINER: {ActionDictConstants.DATA_SOURCE: DATASET_CONFIG,
                                 ActionDictConstants.DATA_ID: DATASET_CONFIG_UPDATE_EVERY_N_MILLIS}
            }
        }
        generator = self.analyst.data_compare_generator(comparing_mapping_list)
        expect_value = {ActionDictConstants.ACTUAL_VALUE: 'actual_dataset_id',
                        ActionDictConstants.DATA_FIELD_NAME: DATASET_ID,
                        ActionDictConstants.EXPECTED_VALUE: 'expect_dataset_id',
                        ActionDictConstants.SECTION: DATASET_HEADER}
        res = list(generator)
        self.assertTrue(len(res) == 2)

    def test_review_header(self):
        self.header_analyst = DatasetHeaderAnalyst(self.data_container, self.deployment_dict, self.dataset_dict)
        self.header_analyst.analyse()
        data_container = self.analyst.get_data_xml_container()
        expect_value = {ActionDictConstants.ACTUAL_VALUE: 'actual_dataset_id',
                        ActionDictConstants.DATA_FIELD_NAME: DATASET_ID,
                        ActionDictConstants.EXPECTED_VALUE: 'expect_dataset_id',
                        ActionDictConstants.SECTION: DATASET_HEADER
                        }
        self.assertTrue(expect_value in data_container.action_list)

    def test_review_dataset_header(self):
        """
        This function also test that when there are no expect value provided
        """
        self.dataset_config_analyst.analyse()
        data_container = self.analyst.get_data_xml_container()
        expect_value = {ActionDictConstants.ACTUAL_VALUE: "/test/path",
                        ActionDictConstants.DATA_FIELD_NAME: DATASET_CONFIG_FILE_DIR,
                        ActionDictConstants.EXPECTED_VALUE: "expect_dataset_folder",
                        ActionDictConstants.SECTION: DATASET_CONFIG
                        }
        self.assertTrue(expect_value in data_container.action_list)