import os
import unittest
from ..dataset_xml_container_generator import DatasetXmlContainerGenerator
from ..dataset_xml_container import DatasetXmlContainer, DatasetCatalogHeader, DatasetConfig
from ..dataset_modify_actions import HeaderDatasetModifyAction, ConfigDatasetModifyAction, GlobalDatasetModifyAction, \
    DataTypeDatasetModifyAction, DataTypeDatasetModifyActionFactory
from ..erddap_dataset_name_constants import DATASET_VARIABLE

from ..dataset_xml_container_generator import DatasetXmlContainerGenerator
from ..dataset_update_handler import DatasetXmlModifierHandler
from common import clean_folder


class TestDatasetUpdateHandler(unittest.TestCase):
    def setUp(self):
        self.current_folder_path = os.path.dirname(os.path.abspath(__file__))
        self.resource_path = os.path.join(self.current_folder_path, 'resource')
        self.output_path = os.path.join(self.current_folder_path, 'output')
        self.output_path_xml_path = os.path.join(self.output_path, 'output_xml.xml')
        self.dataset_draft_path = os.path.join(self.resource_path, 'dataset_draft.xml')
        self.dataset_dict = {
            "dataset_id": "expect_dataset_id",
        }
        self.dataset_header: DatasetCatalogHeader = {
            "type": "example_type",
            "datasetID": "expect_dataset_id",
            "active": True
        }
        self.dataset_config: DatasetConfig = {
            "accessibleViaFiles": True,
            "reloadEveryNMinutes": "123",
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
        self.test_global_config_modify_action = GlobalDatasetModifyAction()
        self.container_generator = DatasetXmlContainerGenerator(self.dataset_draft_path)
        self.data_container = self.container_generator.generate()

    def tearDown(self):
        clean_folder(self.output_path)

    def test_update_dataset_do_nothing(self):
        data_update_handler = DatasetXmlModifierHandler(self.data_container, self.output_path)
        try:
            data_update_handler.update_dataset()
        except Exception:
            self.fail()

    def test_update_header(self):
        update_header_dict = {
            "section": "dataset_header",
            "expected_value": "expect_dataset_id",
            "actual_value": "datasets_f93d_926a_4e63",
            "data_field_name": "datasetID",
        }
        self.data_container.action_list.set_action(update_header_dict)
        data_update_handler = DatasetXmlModifierHandler(self.data_container, self.output_path_xml_path)
        data_update_handler.update_dataset()
        data_update_handler.write()
        # Read the XML file as a string
        with open(self.output_path_xml_path, "r", encoding="utf-8") as file:
            xml_content = file.readlines()
            for line in xml_content:
                if "expect_dataset_id" in line:
                    break
            else:
                self.fail()

    def test_update_config(self):
        expected_data_value = "The expected data folder path value"
        update_config_dict = {
            "section": "dataset_config",
            "expected_value": expected_data_value,
            "actual_value": "datasets_f93d_926a_4e63",
            "data_field_name": "fileDir",
        }
        self.data_container.action_list.set_action(update_config_dict)
        data_update_handler = DatasetXmlModifierHandler(self.data_container, self.output_path_xml_path)
        data_update_handler.update_dataset()
        data_update_handler.write()
        # Read the XML file as a string
        with open(self.output_path_xml_path, "r", encoding="utf-8") as file:
            xml_content = file.readlines()
            for line in xml_content:
                if expected_data_value in line:
                    break
            else:
                self.fail()

    def test_remove_from_dataset_config(self):
        update_config_dict = {
            "section": "dataset_config",
            "expected_value": None,
            "actual_value": "datasets_f93d_926a_4e63",
            "data_field_name": "fileDir",
        }
        self.data_container.action_list.set_action(update_config_dict)
        data_update_handler = DatasetXmlModifierHandler(self.data_container, self.output_path_xml_path)
        data_update_handler.update_dataset()
        data_update_handler.write()
        # Read the XML file as a string
        with open(self.output_path_xml_path, "r", encoding="utf-8") as file:
            xml_content = file.readlines()
            for line in xml_content:
                if "fileDir" in line:
                    self.fail()
            else:
                self.assertTrue(True)

    def test_dataset_config_no_action(self):
        update_config_dict = {
            "section": "dataset_config",
            "expected_value": "test_value",
            "actual_value": "test_value",
            "data_field_name": "fileDir",
        }
        self.data_container.action_list.set_action(update_config_dict)
        data_update_handler = DatasetXmlModifierHandler(self.data_container, self.output_path_xml_path)
        data_update_handler.update_dataset()
        data_update_handler.write()
        # Read the XML file as a string
        with open(self.output_path_xml_path, "r", encoding="utf-8") as file:
            xml_content = file.readlines()
            for line in xml_content:
                # /datasets/ comes from the dataset_draft.xml
                if "/datasets/" in line:
                    break
            else:
                self.fail()

    def test_dataset_global_multiple_actions(self):
        update_config_dicts = [{
            "section": "dataset_global",
            "expected_value": "Trajectory_TEST",  # edit the fileDir value
            "actual_value": "Point",
            "data_field_name": "cdm_data_type",
        },
            {
                "section": "dataset_global",
                "expected_value": "example_value_for_add_a_filed",
                "actual_value": None,  # add new field
                "data_field_name": "example_field",
            },
            {
                "section": "dataset_global",
                "expected_value": None,  # remove the Conventions
                "actual_value": "test_value",
                "data_field_name": "Conventions",
            }
        ]
        for action in update_config_dicts:
            self.data_container.action_list.set_action(action)
        data_update_handler = DatasetXmlModifierHandler(self.data_container, self.output_path_xml_path)
        data_update_handler.update_dataset()
        data_update_handler.write()

        edit_file_dir = False
        add_new_field = False

        # Read the XML file as a string
        with open(self.output_path_xml_path, "r", encoding="utf-8") as file:
            xml_content = file.readlines()
            for line in xml_content:
                if "Trajectory_TEST" in line:
                    edit_file_dir = True
                if "<att name=\"example_field\">example_value_for_add_a_filed</att>" in line:
                    add_new_field = True
                if "Conventions" in line:
                    self.fail()
        self.assertTrue(edit_file_dir )
        self.assertTrue(add_new_field)


    def test_dataset_config_multiple_actions(self):
        update_config_dicts = [{
            "section": "dataset_config",
            "expected_value": "test_file_dir_value", # edit the fileDir value
            "actual_value": "test_value",
            "data_field_name": "fileDir",
                },
            {
                "section": "dataset_config",
                "expected_value": "example_value",
                "actual_value": None, # add new field
                "data_field_name": "example_field",
            },
            {
                "section": "dataset_config",
                "expected_value": None, # remove the Conventions
                "actual_value": "test_value",
                "data_field_name": "reloadEveryNMinutes",
            }
        ]
        for action_dict in update_config_dicts:
            self.data_container.action_list.set_action(action_dict)
        data_update_handler = DatasetXmlModifierHandler(self.data_container, self.output_path_xml_path)
        data_update_handler.update_dataset()
        data_update_handler.write()
        edit_file_dir = False
        add_new_field = False

        # Read the XML file as a string
        with open(self.output_path_xml_path, "r", encoding="utf-8") as file:
            xml_content = file.readlines()
            for line in xml_content:
                if "<fileDir>test_file_dir_value</fileDir>" in line:
                    edit_file_dir = True
                if "<example_field>example_value</example_field>" in line:
                    add_new_field = True
                if "<reloadEveryNMinutes>" in line:
                    self.fail()
        self.assertTrue(edit_file_dir and add_new_field)


    def test_update_data_variable_destination(self):
        data_dict = {
            "section": DATASET_VARIABLE,
            "data_field_name": "time",  # source
            'actual_value': {
                "destinationName": "time"
            },

            "expected_value": {
                "destinationName": "new_time",
            }
        }

        self.data_container.action_list.set_action(data_dict)
        data_update_handler = DatasetXmlModifierHandler(self.data_container, self.output_path_xml_path)
        data_update_handler.update_dataset()
        data_update_handler.write()
        # Read the XML file as a string
        with open(self.output_path_xml_path, "r", encoding="utf-8") as file:
            xml_content = file.readlines()
            for line in xml_content:
                if "<destinationName>new_time</destinationName>" in line:
                    break
            else:
                self.fail()

    def test_update_data_variable_dataType(self):
        data_dict = {
            "section": DATASET_VARIABLE,
            "data_field_name": "time",  # source
            'actual_value': {
                "dataType": "double"
            },

            "expected_value": {
                "dataType": "time_data_type",
            }
        }

        self.data_container.action_list.set_action(data_dict)
        data_update_handler = DatasetXmlModifierHandler(self.data_container, self.output_path_xml_path)
        data_update_handler.update_dataset()
        data_update_handler.write()
        # Read the XML file as a string
        with open(self.output_path_xml_path, "r", encoding="utf-8") as file:
            xml_content = file.readlines()
            for line in xml_content:
                if "<dataType>time_data_type</dataType>" in line:
                    break
            else:
                self.fail()

    def test_update_data_variable_add_data_variable(self):
        data_dict = {
            "section": DATASET_VARIABLE,
            "data_field_name": "new_data_variable",  # source
            'actual_value': None,
            "expected_value": {
                "destinationName": "new_data_variable",
                "dataType": "time_data_type",
                "addAttributes":[{
                    "name":"new_data_variable_att_name",
                    "value": "new_data_variable_value"
                }]
            }
        }

        self.data_container.action_list.set_action(data_dict)
        data_update_handler = DatasetXmlModifierHandler(self.data_container, self.output_path_xml_path)
        data_update_handler.update_dataset()
        data_update_handler.write()
        # Read the XML file as a string
        with open(self.output_path_xml_path, "r", encoding="utf-8") as file:
            xml_content = file.readlines()
            for line in xml_content:
                if "<att name=\"new_data_variable_att_name\">new_data_variable_value</att>" in line:
                    break
            else:
                self.fail()

    def test_update_data_variable_add_attribute(self):
        data_dict = {
            "section": DATASET_VARIABLE,
            "data_field_name": "time",  # source
            'actual_value': {
                "addAttributes":None
            },
            "expected_value": {
                "addAttributes":[{
                    "name":"new_data_variable_att_name",
                    "value": "new_data_variable_value"
                }]
            }
        }

        self.data_container.action_list.set_action(data_dict)
        data_update_handler = DatasetXmlModifierHandler(self.data_container, self.output_path_xml_path)
        data_update_handler.update_dataset()
        data_update_handler.write()
        # Read the XML file as a string
        with open(self.output_path_xml_path, "r", encoding="utf-8") as file:
            xml_content = file.readlines()
            for line in xml_content:
                if "<att name=\"new_data_variable_att_name\">new_data_variable_value</att>" in line:
                    break
            else:
                self.fail()

    def test_update_data_variable_remove_attribute(self):
        data_dict = {
            "section": DATASET_VARIABLE,
            "data_field_name": "time",  # source
            'actual_value': {
                "addAttributes": [{
                    "name": "colorBarMaximum",
                    "value": "1.63491398E9"
                }]
            },
            "expected_value": {
                "addAttributes":None
            }
        }

        self.data_container.action_list.set_action(data_dict)
        data_update_handler = DatasetXmlModifierHandler(self.data_container, self.output_path_xml_path)
        data_update_handler.update_dataset()
        data_update_handler.write()
        # Read the XML file as a string
        with open(self.output_path_xml_path, "r", encoding="utf-8") as file:
            xml_content = file.readlines()
            for line in xml_content:
                if "<att name=\"colorBarMaximum\" type=\"double\">1.63491398E9</att>" in line:
                    self.fail()

    def test_update_data_variable_edit_attribute(self):
        data_dict = {
            "section": DATASET_VARIABLE,
            "data_field_name": "time",  # source
            'actual_value': {
                "addAttributes": [{
                    "name": "colorBarMaximum",
                    "value": "1.63491398E9"
                }]
            },
            "expected_value": {
                "addAttributes": [{
                    "name": "colorBarMaximum",
                    "value": "1234"
                }]
            }
        }

        self.data_container.action_list.set_action(data_dict)
        data_update_handler = DatasetXmlModifierHandler(self.data_container, self.output_path_xml_path)
        data_update_handler.update_dataset()
        data_update_handler.write()
        # Read the XML file as a string
        with open(self.output_path_xml_path, "r", encoding="utf-8") as file:
            xml_content = file.readlines()
            for line in xml_content:
                if "<att name=\"colorBarMaximum\" type=\"double\">1234</att>" in line:
                    break
            else:
                self.fail()