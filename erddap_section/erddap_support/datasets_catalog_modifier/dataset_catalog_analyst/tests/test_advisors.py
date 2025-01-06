import os
import unittest
from ..erddap_dataset_name_constants import DATASET_CONFIG_FILE_DIR, \
    DATASET_CONFIG_FILE_NAME_REGEX, DATASET_CONFIG_UPDATE_EVERY_N_MILLIS, ErddapSections, DATASET_ID
from ..dataset_xml_container import DatasetXmlContainer, DatasetCatalogHeader, DatasetConfig
from ..dataset_xml_container_generator import DatasetXmlContainerGenerator

from ..format_advisor import TrajectoryCDMTrajectoryVariableAdvisor, CFRoleAdvisor


class TestMetadataConventionAdvisor(unittest.TestCase):
    def setUp(self):
        self.current_folder_path = os.path.dirname(os.path.abspath(__file__))
        self.resource_path = os.path.join(self.current_folder_path, 'resource')
        self.draft_dataset_xml_path = os.path.join(self.resource_path, 'dataset_draft.xml')
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

        self.data_container = DatasetXmlContainerGenerator(self.draft_dataset_xml_path).generate()

        self.advisor = CFRoleAdvisor(self.data_container, self.deployment_dict,
                                     self.dataset_dict)

    def test_analyse_with_no_cf_role_variable(self):
        input_value = {'variable_list': []}
        # expected  add
        expected_value = [
            {
                'actual_value': {
                    "addAttributes": None
                },
                'data_field_name': 'TRAJECTORY',
                'expected_value': {
                    "addAttributes": [
                        {
                            "name": "cf_role",
                            "value": "trajectory_id"
                        }
                    ]
                },
                'section': ErddapSections.DATASET_VARIABLE
            }
        ]
        result = self.advisor.suggest(input_value)
        self.assertEqual(expected_value, result)

    def test_analyse_with_multiple_cf_role_variable(self):
        input_value = {'variable_list': [{'sourceName': 'lat', 'destinationName': 'latitude', 'dataType': 'double',
                                          'addAttributes': {'references': {'name': 'references', 'text': 'WGS84'},
                                                            'cf_role': {'name': 'cf_role', 'text': 'trajectory_id'}}},
                                         {'sourceName': 'lon', 'destinationName': 'longitude', 'dataType': 'double',
                                          'addAttributes': {'ioos_category': {'name': 'ioos_category',
                                                                              'text': 'Location'},
                                                            'missing_value': {'name': 'missing_value', 'type': 'double',
                                                                              'text': 'NaN'},
                                                            'references': {'name': 'references', 'text': 'WGS84'},
                                                            'cf_role': {'name': 'cf_role', 'text': 'trajectory_id'}}}]}
        # expected removes and add
        expected_value = [
            {
                'actual_value': {
                    "addAttributes": [
                        {
                            "name": "cf_role",
                            "value": "trajectory_id"
                        }
                    ]
                },
                'data_field_name': 'lat',
                'expected_value': {
                    "addAttributes": None
                },
                'section': ErddapSections.DATASET_VARIABLE
            },
            {
                'actual_value': {
                    "addAttributes": [
                        {
                            "name": "cf_role",
                            "value": "trajectory_id"
                        }
                    ]
                },
                'data_field_name': 'lon',
                'expected_value': {
                    "addAttributes": None
                },
                'section': ErddapSections.DATASET_VARIABLE
            },
            {
                'actual_value': {
                    "addAttributes": None
                },
                'data_field_name': 'TRAJECTORY',
                'expected_value': {
                    "addAttributes": [
                        {
                            "name": "cf_role",
                            "value": "trajectory_id"
                        }
                    ]
                },
                'section': ErddapSections.DATASET_VARIABLE
            }
        ]
        result = self.advisor.suggest(input_value)
        self.assertEqual(expected_value, result)

    def test_analyse_with_one_cf_role_variable_on_correct_data_variable_but_wrong_value(self):
        input_value = {'variable_list': [
            {'sourceName': 'TRAJECTORY',
             'destinationName': 'TRAJECTORY', 'dataType': 'double',
             'addAttributes': {'missing_value': {'name': 'missing_value', 'type': 'double', 'text': 'NaN'},
                               'references': {'name': 'references', 'text': 'WGS84'},
                               'cf_role': {'name': 'cf_role', 'text': 'wrong_value'}}}]}
        # expected  removes and then add
        expected_value = [
            {
                'actual_value': {
                    "addAttributes": [
                        {
                            "name": "cf_role",
                            "value": "wrong_value"
                        }
                    ]
                },
                'data_field_name': 'TRAJECTORY',
                'expected_value': {
                    "addAttributes": None
                },
                'section': ErddapSections.DATASET_VARIABLE
            },
            {
                'actual_value': {
                    "addAttributes": None
                },
                'data_field_name': 'TRAJECTORY',
                'expected_value': {
                    "addAttributes": [
                        {
                            "name": "cf_role",
                            "value": "trajectory_id"
                        }
                    ]
                },
                'section': ErddapSections.DATASET_VARIABLE
            }
        ]
        result = self.advisor.suggest(input_value)
        self.assertEqual(expected_value, result)

    def test_analyse_with_cf_role_on_wrong_data_variable(self):
        # expected  remove and then add
        input_value = {'variable_list': [
            {'sourceName': 'lat',
             'destinationName': 'latitude', 'dataType': 'double',
             'addAttributes': {'missing_value': {'name': 'missing_value', 'type': 'double', 'text': 'NaN'},
                               'references': {'name': 'references', 'text': 'WGS84'},
                               'cf_role': {'name': 'cf_role', 'text': 'trajectory_id'}}}]}
        expected_value = [
            {
                'actual_value': {
                    "addAttributes": [
                        {
                            "name": "cf_role",
                            "value": "trajectory_id"
                        }
                    ]
                },
                'data_field_name': 'lat',
                'expected_value': {
                    "addAttributes": None
                },
                'section': ErddapSections.DATASET_VARIABLE
            },
            {
                'actual_value': {
                    "addAttributes": None
                },
                'data_field_name': 'TRAJECTORY',
                'expected_value': {
                    "addAttributes": [
                        {
                            "name": "cf_role",
                            "value": "trajectory_id"
                        }
                    ]
                },
                'section': ErddapSections.DATASET_VARIABLE
            }
        ]
        result = self.advisor.suggest(input_value)
        self.assertEqual(expected_value, result)


class TestTrajectoryCDMTrajectoryVariableAdvisor(unittest.TestCase):
    def setUp(self):
        self.current_folder_path = os.path.dirname(os.path.abspath(__file__))
        self.resource_path = os.path.join(self.current_folder_path, 'resource')
        self.draft_dataset_xml_path = os.path.join(self.resource_path, 'dataset_draft.xml')
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

        self.data_container = DatasetXmlContainerGenerator(self.draft_dataset_xml_path).generate()

        self.advisor = TrajectoryCDMTrajectoryVariableAdvisor(self.data_container, self.deployment_dict,
                                                              self.dataset_dict)

    def tearDown(self):
        ...

    def test_analyse_with_need_to_fix(self):
        input_value = {'cdm_data_type': 'Point', 'cdm_trajectory_variables': None}
        expected_value = [
            {
                'actual_value': None,
                'data_field_name': 'cdm_data_type',
                'expected_value': 'Trajectory',
                'section': 'dataset_global'},
            {
                'actual_value': None,
                'data_field_name': 'cdm_trajectory_variables',
                'expected_value': 'TRAJECTORY',
                'section': 'dataset_global'}
        ]
        result = self.advisor.suggest(input_value)
        self.assertEqual(expected_value, result)

    def test_analyse_with_missing_field(self):
        input_value = {'cdm_data_type': 'Point'}
        expected_value = [
            {
                'actual_value': None,
                'data_field_name': 'cdm_data_type',
                'expected_value': 'Trajectory',
                'section': 'dataset_global'},
            {
                'actual_value': None,
                'data_field_name': 'cdm_trajectory_variables',
                'expected_value': 'TRAJECTORY',
                'section': 'dataset_global'}
        ]
        result = self.advisor.suggest(input_value)
        self.assertEqual(expected_value, result)

    def test_analyse_with_fix_cdm_data_type_only(self):
        input_value = {'cdm_data_type': 'Point', 'cdm_trajectory_variables': 'TRAJECTORY'}
        expected_value = [
            {
                'actual_value': None,
                'data_field_name': 'cdm_data_type',
                'expected_value': 'Trajectory',
                'section': 'dataset_global'}
        ]
        result = self.advisor.suggest(input_value)
        self.assertEqual(expected_value, result)

    def test_analyse_with_no_fixing(self):
        input_value = {'cdm_data_type': 'Trajectory', 'cdm_trajectory_variables': 'TRAJECTORY'}
        expected_value = []
        result = self.advisor.suggest(input_value)
        self.assertEqual(expected_value, result)
