import os
import unittest
from ..dataset_xml_container_generator import DatasetXmlContainerGenerator
from ..dataset_xml_container import DatasetXmlContainer, DatasetCatalogHeader, DatasetConfig
from ..dataset_modify_actions import HeaderDatasetModifyAction, ConfigDatasetModifyAction, GlobalDatasetModifyAction, \
    DataTypeDatasetModifyAction, BaseModifyActionFactory, DataTypeDatasetModifyActionFactory
from ..erddap_dataset_name_constants import ActionListActionsConstants


class TestHeaderModifyAction(unittest.TestCase):
    def setUp(self):
        self.test_header_modify_action = HeaderDatasetModifyAction()

    def test_set_action(self):
        test_action_dict = {
            "section": "dataset_header",
            "expected_value": "expect_dataset_id",
            "actual_value": "random_dataset_id",
            "data_field_name": "datasetID",
        }
        self.test_header_modify_action.set_action(test_action_dict)
        value_action = self.test_header_modify_action.action_flag
        self.assertEqual(ActionListActionsConstants.EDIT, value_action)


class TestConfigDatasetModifyAction(unittest.TestCase):
    def setUp(self):
        self.test_header_modify_action = ConfigDatasetModifyAction()

    def test_set_random_dict_as_action(self):
        test_action_dict = {
            "randon_section": "dataset_header",
            "randon_value": "expect_dataset_id",
            "randon_a_value": "random_dataset_id",
            "data_field_name": "datasetID",
        }
        with self.assertRaises(ValueError) as context:
            self.test_header_modify_action.set_action({
                self.test_header_modify_action.set_action(test_action_dict)
            })

    def test_variable_dict_has_extra_field(self):
        test_action_dict = {
            "section": "dataset_config",
            "expected_value": "expect_dataset_id",
            "actual_value": "random_dataset_id",
            "data_field_name": "datasetID",
            "extra_field": "random_value",
        }
        try:
            self.test_header_modify_action.set_action(test_action_dict)
        except TypeError as e:
            self.fail(f"set_action raised an exception unexpectedly: {e}")


class TestGlobalDatasetModifyAction(unittest.TestCase):
    def setUp(self):
        self.test_global_config_modify_action = GlobalDatasetModifyAction()

    def test_set_action_adding_variable_to_wrong_field(self):
        test_action_dict = {
            "section": "dataset_config",
            "expected_value": "expect_dataset_id",
            "actual_value": "random_dataset_id",
            "data_field_name": "datasetID"
        }
        with self.assertRaises(AssertionError) as context:
            self.test_global_config_modify_action.set_action(test_action_dict)

    def test_set_action_add_more_field(self):
        test_action_dict = {
            "section": "dataset_global",
            "expected_value": "expect_dataset_id",
            "actual_value": None,
            "data_field_name": "datasetID"
        }
        self.test_global_config_modify_action.set_action(test_action_dict)
        self.assertEqual(self.test_global_config_modify_action.action_flag, ActionListActionsConstants.ADD)

    def test_set_action_for_removing(self):
        test_action_dict = {
            "section": "dataset_global",
            "expected_value": None,
            "actual_value": "actual value",
            "data_field_name": "example_field_name"
        }
        self.test_global_config_modify_action.set_action(test_action_dict)
        self.assertEqual(self.test_global_config_modify_action.action_flag, ActionListActionsConstants.REMOVE)


class TestDataTypeDatasetModifyAction(unittest.TestCase):
    def setUp(self):
        self.test_data_type_modify_action = DataTypeDatasetModifyAction()

    def test_set_action_for_remove_variable(self):
        # REMOVE
        test_action_dict = {
            "section": DataTypeDatasetModifyAction.TYPE,
            "sourceName": "time",  # source
            "destinationName": None
        }
        self.test_data_type_modify_action.set_action(test_action_dict)
        self.assertEqual(self.test_global_config_modify_action.action_flag, ActionListActionsConstants.REMOVE)

    def test_set_action_for_update_destination_name(self):
        # UPDATE_DESTINATION
        test_action_dict = {
            "section": DataTypeDatasetModifyAction.TYPE,
            "sourceName": "time",  # source
            "destinationName": "new_time"
        }
        self.test_data_type_modify_action.set_action(test_action_dict)
        self.assertEqual(self.test_global_config_modify_action.action_flag, ActionListActionsConstants.REMOVE)

    def test_set_action_for_update_data_type(self):
        # UPDATE_DATATYPE
        test_action_dict = {
            "section": DataTypeDatasetModifyAction.TYPE,
            "sourceName": "time",  # source
            "dataType": "new_data_type"
        }
        self.test_data_type_modify_action.set_action(test_action_dict)
        self.assertEqual(self.test_global_config_modify_action.action_flag, ActionListActionsConstants.REMOVE)

    def test_add_new_attributes(self):
        # ADD_ATT
        test_action_dict = {
            "section": DataTypeDatasetModifyAction.TYPE,
            "sourceName": "time",
            "att_name": "new_att",  # source
            "value": {
                "type": "new_att_type",
                "value": "new_att_value"
            }
        }
        self.test_data_type_modify_action.set_action(test_action_dict)
        self.assertEqual(self.test_global_config_modify_action.action_flag, ActionListActionsConstants.REMOVE)

    def test_update_attributes(self):
        # UPDATE_ATT
        test_action_dict = {
            "section": DataTypeDatasetModifyAction.TYPE,
            "sourceName": "time",
            "att_name": "ioos_category",  # source
            "value": {
                "value": "new_ioos_category"
            }
        }
        self.test_data_type_modify_action.set_action(test_action_dict)
        self.assertEqual(self.test_global_config_modify_action.action_flag, ActionListActionsConstants.REMOVE)

    def test_remove_attributes(self):
        # REMOVE
        test_action_dict = {
            "section": DataTypeDatasetModifyAction.TYPE,
            "sourceName": "time",
            "att_name": "ioos_category"  # source
        }
        self.test_data_type_modify_action.set_action(test_action_dict)
        self.assertEqual(self.test_global_config_modify_action.action_flag, ActionListActionsConstants.REMOVE)

    def test_add_new_data_variable(self):
        # ADD
        test_action_dict = {
            "section": DataTypeDatasetModifyAction.TYPE,
            "sourceName": "new_value",
            "destinationName": "new_value",
            "att_name": "new_att",
            "dataType": "double",
            "attr": [{
                "type": "new_att_type",
                "value": "new_att_value"
            }]
        }
        self.test_data_type_modify_action.set_action(test_action_dict)
        self.assertEqual(self.test_global_config_modify_action.action_flag, ActionListActionsConstants.REMOVE)


class TestBaseDatasetModifyActionFactory(unittest.TestCase):
    def setUp(self):
        self.factory = BaseModifyActionFactory()

    def test_setup_action_flag(self):
        test_edit_action_dict = {
            "section": "dataset_header",
            "expected_value": "expect_dataset_id",
            "actual_value": "random_dataset_id",
            "data_field_name": "datasetID",
        }

        test_add_action_dict = {
            "section": "dataset_global",
            "expected_value": "expect_dataset_id",
            "actual_value": None,
            "data_field_name": "datasetID"
        }

        test_remove_action_dict = {
            "section": DataTypeDatasetModifyAction.TYPE,
            "data_field_name": "time",  # source
            "actual_value": "new_time",
            "expected_value": None
        }
        test_no_action_action_dict ={
            "section": "dataset_header",
            "expected_value": "expect_dataset_id",
            "actual_value": "expect_dataset_id",
            "data_field_name": "datasetID",
        }

        self.assertEqual(self.factory.get_action_flag(test_edit_action_dict), ActionListActionsConstants.EDIT)
        self.assertEqual(self.factory.get_action_flag(test_add_action_dict), ActionListActionsConstants.ADD)
        self.assertEqual(self.factory.get_action_flag(test_remove_action_dict), ActionListActionsConstants.REMOVE)
        self.assertEqual(self.factory.get_action_flag(test_no_action_action_dict), ActionListActionsConstants.NO_ACTION)


class TestDataTypeDatasetModifyActionFactory(unittest.TestCase):
    def setUp(self):
        self.factory = DataTypeDatasetModifyActionFactory()

    def test_set_action_for_remove_variable_action_flag(self):
        # REMOVE
        test_action_dict = {
            "section": DataTypeDatasetModifyAction.TYPE,
            "data_field_name": "time",  # source
            'actual_value': 'time_value',
            "expected_value": None
        }

        self.assertEqual(self.factory.get_action_flag(test_action_dict), ActionListActionsConstants.REMOVE)

    def test_set_action_for_update_destination_name_action_flag(self):
        # UPDATE_DESTINATION
        test_action_dict = {
            "section": DataTypeDatasetModifyAction.TYPE,
            "data_field_name": "time",  # source
            'actual_value': {
                "sourceName": "time",
                "destinationName": "time",
                "dataType": "double",
                "addAttributes":[
                    {
                        "name": "colorBarMaximum",
                        "type": "double",
                        "value": "1.63491398E9"
                    },
                    {
                        "name": "ioos_category",
                        "value": "Time"
                    }
                ]
            },
            "expected_value": {
                "sourceName": "time",
                "destinationName": "new_time",
                "dataType": "double",
                "addAttributes":[
                    {
                        "name": "colorBarMaximum",
                        "type": "double",
                        "value": "1.63491398E9"
                    },
                    {
                        "name": "ioos_category",
                        "value": "Time"
                    }
                ]
            }
        }
        action_flag = self.factory.get_action_flag(test_action_dict)
        self.assertEqual(action_flag, ActionListActionsConstants.UPDATE_DESTINATION)


    def test_set_action_for_update_data_type_action_flag(self):
        # UPDATE_DATATYPE
        test_action_dict = {
            "section": DataTypeDatasetModifyAction.TYPE,
            "data_field_name": "time",  # source
            'actual_value': {
                "sourceName": "time",
                "dataType": "double",
            },

            "expected_value": {
                "sourceName": "time",
                "dataType": "string"
            }
        }
        action_flag = self.factory.get_action_flag(test_action_dict)
        self.assertEqual(action_flag, ActionListActionsConstants.UPDATE_DATATYPE)


    def test_add_new_attributes_action_flag(self):
       # ADD_ATT
       test_action_dict = {
           "section": DataTypeDatasetModifyAction.TYPE,
           "data_field_name": "time",  # source
           'actual_value': {
               "sourceName": "time",
               "addAttributes": None,
           },

           "expected_value": {
               "sourceName": "time",
               "addAttributes": [
                   {
                       "name": "colorBarMaximum",
                       "type": "double",
                       "value": "1.63491398E9"
                   }
               ]
           }
       }
       action_flag = self.factory.get_action_flag(test_action_dict)
       self.assertEqual(action_flag, ActionListActionsConstants.ADD_ATT)


    def test_update_attributes_action_flag(self):
        # UPDATE_ATT
        test_action_dict = {
            "section": DataTypeDatasetModifyAction.TYPE,
            "data_field_name": "time",  # source
            'actual_value': {
                "sourceName": "time",
                "addAttributes": {
                    "name": "colorBarMaximum",
                    "type": "double",
                    "value": "123"
                },
            },

            "expected_value": {
                "sourceName": "time",
                "addAttributes": [
                    {
                        "name": "colorBarMaximum",
                        "type": "double",
                        "value": "1.63491398E9"
                    }
                ]
            }
        }
        action_flag = self.factory.get_action_flag(test_action_dict)
        self.assertEqual(action_flag, ActionListActionsConstants.UPDATE_ATT)

    def test_remove_attributes_action_flag(self):
        # REMOVE
        test_action_dict = {
            "section": DataTypeDatasetModifyAction.TYPE,
            "data_field_name": "time",  # source
            'actual_value': {
                "sourceName": "time",
                "addAttributes": [
                    {
                        "name": "colorBarMaximum",
                        "type": "double",
                        "value": "1.63491398E9"
                    }
                ],
            },

            "expected_value": {
                "sourceName": "time",
                "addAttributes": None
            }
        }
        action_flag = self.factory.get_action_flag(test_action_dict)
        self.assertEqual(action_flag, ActionListActionsConstants.REMOVE_ATT)


    def test_add_new_data_variable_action_flag(self):
        # ADD
        test_action_dict = {
            "section": DataTypeDatasetModifyAction.TYPE,
            "data_field_name": "time",  # source
            "destinationName": "time",
            "dataType": "double",
            'actual_value': None,
            "expected_value": {
                "sourceName": "time",
                "addAttributes": [
                    {
                        "name": "colorBarMaximum",
                        "type": "double",
                        "value": "1.63491398E9"
                    }
                ],
            }
        }
        action_flag = self.factory.get_action_flag(test_action_dict)
        self.assertEqual(action_flag, ActionListActionsConstants.ADD)

    def test_generate(self):
        test_action_dict = {
            "section": DataTypeDatasetModifyAction.TYPE,
            "data_field_name": "time",  # source
            'actual_value': {
                "sourceName": "time",
                "destinationName": "time",
                "dataType": "double",
                "addAttributes": [
                    {
                        "name": "colorBarMaximum",
                        "type": "double",
                        "value": "1.63491398E9"
                    },
                    {
                        "name": "ioos_category",
                        "value": "Time"
                    }
                ]
            },
            "expected_value": {
                "sourceName": "time",
                "destinationName": "new_time",
                "dataType": "double",
                "addAttributes": [
                    {
                        "name": "colorBarMaximum",
                        "type": "double",
                        "value": "1.63491398E9"
                    },
                    {
                        "name": "ioos_category",
                        "value": "Time"
                    }
                ]
            }
        }
        value_list = self.factory.generate(test_action_dict)


    def test_generate_add_action(self):
        test_action_dict = {
            "section": DataTypeDatasetModifyAction.TYPE,
            "data_field_name": "time",  # source
            'actual_value': None,
            "expected_value": {
                "sourceName": "time",
                "destinationName": "new_time",
                "dataType": "double",
                "addAttributes": [
                    {
                        "name": "colorBarMaximum",
                        "type": "double",
                        "value": "1.63491398E9"
                    },
                    {
                        "name": "ioos_category",
                        "value": "Time"
                    }
                ]
            }
        }
        value_list = self.factory.generate(test_action_dict)
        self.assertEqual(1, len(value_list))
        self.assertEqual(ActionListActionsConstants.ADD, value_list[0].action_flag)

    def test_generate_remove_action(self):
        # remove data variable
        test_action_dict = {
            "section": DataTypeDatasetModifyAction.TYPE,
            "data_field_name": "time",  # source
            'actual_value': {
                "sourceName": "time",
                "destinationName": "time",
                "dataType": "double",
                "addAttributes": [
                    {
                        "name": "colorBarMaximum",
                        "type": "double",
                        "value": "1.63491398E9"
                    },
                    {
                        "name": "ioos_category",
                        "value": "Time"
                    }
                ]
            },
            "expected_value": None
        }
        value_list = self.factory.generate(test_action_dict)
        self.assertEqual(1, len(value_list))
        self.assertEqual(ActionListActionsConstants.REMOVE, value_list[0].action_flag)
