import os
import unittest
from ..dataset_catalog_analyst import DATASET_ID, DatasetHeaderAnalyst, DatasetConfigAnalyst
from ..format_reviewer import BaseStaticValueReviewer, HeaderReviewer
from ..erddap_dataset_name_constants import DATASET_HEADER, DATASET_CONFIG, DATASET_CONFIG_FILE_DIR, \
    DATASET_CONFIG_FILE_NAME_REGEX, DATASET_CONFIG_UPDATE_EVERY_N_MILLIS, ActionDictConstants
from ..dataset_xml_container import DatasetXmlContainer, DatasetCatalogHeader, DatasetConfig
from ..dataset_xml_container_generator import DatasetXmlContainerGenerator
from ..format_reviewer import TrajectoryCFRoleVariableReviewer, TrajectoryCdmTrajectoryVariableReviewer


class TestStaticValueReviewer(unittest.TestCase):
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

        self.data_container = DatasetXmlContainer(self.dataset_header, self.dataset_config, {}, self.data_variable_list,
                                                  None)

        # self.header_analyst = DatasetHeaderAnalyst(self.data_container, self.deployment_dict, self.dataset_dict)
        # self.dataset_config_analyst = DatasetConfigAnalyst(self.data_container, self.deployment_dict, self.dataset_dict)

    def tearDown(self):
        ...

    def test_data_compare_generator(self):
        reviewer = BaseStaticValueReviewer(self.data_container, self.deployment_dict, self.dataset_dict)
        reviewer.MAPPING_LIST = {
            DATASET_ID: {
                ActionDictConstants.DATASET: {ActionDictConstants.DATA_SOURCE: ActionDictConstants.DATASET_DICT,
                                              ActionDictConstants.DATA_ID: DATASET_ID},
                ActionDictConstants.DATA_CONTAINER: {ActionDictConstants.DATA_SOURCE: DATASET_HEADER,
                                                     ActionDictConstants.DATA_ID: DATASET_ID}
            },
        }
        feedback_list = reviewer._review()
        expect_value = {ActionDictConstants.ACTUAL_VALUE: 'actual_dataset_id',
                        ActionDictConstants.DATA_FIELD_NAME: DATASET_ID,
                        ActionDictConstants.EXPECTED_VALUE: 'expect_dataset_id',
                        ActionDictConstants.SECTION: DATASET_HEADER}

        self.assertEqual([expect_value], feedback_list)

    def test_data_compare_generator_with_multiple_keys(self):
        reviewer = BaseStaticValueReviewer(self.data_container, self.deployment_dict, self.dataset_dict)
        reviewer.MAPPING_LIST = {
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

        feedback_list = reviewer._review()
        expect_value = {ActionDictConstants.ACTUAL_VALUE: 'actual_dataset_id',
                        ActionDictConstants.DATA_FIELD_NAME: DATASET_ID,
                        ActionDictConstants.EXPECTED_VALUE: 'expect_dataset_id',
                        ActionDictConstants.SECTION: DATASET_HEADER}

        self.assertTrue(len(feedback_list) == 2)


class TestTrajectoryFormatReviewer(unittest.TestCase):
    def setUp(self):
        self.current_folder_path = os.path.dirname(os.path.abspath(__file__))
        self.resource_path = os.path.join(self.current_folder_path, 'resource')

    def tearDown(self):
        ...

    def test_cf_role_checker_with_no_cf_role(self):
        self.dataset_draft_path = os.path.join(self.resource_path, "dataset_draft.xml")
        data_container = DatasetXmlContainerGenerator(self.dataset_draft_path).generate()
        checker = TrajectoryCFRoleVariableReviewer(data_container)
        res = checker.review()
        print(res)

    def test_cf_role_checker_with_one_data_variable_has_cf_role(self):
        self.dataset_draft_path = os.path.join(self.resource_path, "dataset_draft_with_cf_role.xml")
        data_container = DatasetXmlContainerGenerator(self.dataset_draft_path).generate()
        checker = TrajectoryCFRoleVariableReviewer(data_container)
        res = checker.review()
        print(res)

    def test_cf_role_checker_with_multiple_cf_role(self):
        self.dataset_draft_path = os.path.join(self.resource_path, "dataset_draft_with_multiple_cf_role_variable.xml")
        data_container = DatasetXmlContainerGenerator(self.dataset_draft_path).generate()
        checker = TrajectoryCFRoleVariableReviewer(data_container)
        res = checker.review()
        print(res)

    def test_trajectory_cdm_trajectory_variable(self):
        self.dataset_draft_path = os.path.join(self.resource_path, "dataset_draft.xml")
        data_container = DatasetXmlContainerGenerator(self.dataset_draft_path).generate()
        checker = TrajectoryCdmTrajectoryVariableReviewer(data_container)
        res = checker.review()
        print(res)
