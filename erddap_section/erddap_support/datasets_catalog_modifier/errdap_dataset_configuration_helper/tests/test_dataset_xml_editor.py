import os
import unittest

from erddap_section.erddap_support.datasets_catalog_modifier.errdap_dataset_configuration_helper.dataset_xml_editor import \
    ERDDAPDatasetXMLEditor
from ..utils import read_xml_as_string
from common import clean_folder




class TestDatasetXMLEditor(unittest.TestCase):
    def setUp(self):
        self.current_folder_path = os.path.dirname(os.path.abspath(__file__))
        # Create temporary directories and files for testing
        self.output_dir = os.path.join(self.current_folder_path, "output")
        self.output_path_xml_path = os.path.join(self.output_dir, 'output_xml.xml')
        self.resource_dir = os.path.join(self.current_folder_path, "resource")
        self.test_draft_xml_path = os.path.join(self.resource_dir, "dataset_draft.xml")
        self.draft_xml_str = read_xml_as_string(self.test_draft_xml_path)
        self.editor = ERDDAPDatasetXMLEditor(self.draft_xml_str)

    def tearDown(self):
        clean_folder(self.output_dir)

    def test_get_header(self):
        header_dict = self.editor.get_header()
        self.assertIn('type', header_dict)
        self.assertIn('datasetID', header_dict)
        self.assertIn('active', header_dict)

    def test_set_dataset_id(self):
        # This test make sure we can use this function to assign new dataset ID
        new_dataset_id = "test_dataset_id"
        self.editor.set_header('datasetID', new_dataset_id)
        new_header_dict = self.editor.get_header()
        self.assertIn('datasetID', new_header_dict)
        self.assertEqual(new_dataset_id, new_header_dict['datasetID'])

    def test_get_unit(self):
        res = self.editor.get_unit()
        expect_value = {
            "lat": "degrees_north",
            "lon": "degrees_east",
        }
        self.assertEqual(res, expect_value)

    def test_get_units_in_comment(self):
        res = self.editor.get_unit(read_comments=True)
        expect_value = {
            "lat": "degrees_north",
            "lon": "degrees_east",
            "time": "seconds since 1970-01-01T00:00:00Z"
        }
        self.assertEqual(res, expect_value)

    def test_add_unit(self):
        self.editor.add_unit("lat", "some_thing_wrong")
        res = self.editor.get_unit()
        expect_value = {
            "lat": "some_thing_wrong",
            "lon": "degrees_east",
        }
        self.assertEqual(res, expect_value)

    def test_get_all_added_attr(self):
        expect_value = {'cdm_data_type': 'Point', 'Conventions': 'CF-1.10, COARDS, ACDD-1.3'}
        res = self.editor.get_all_global_attr()
        self.assertEqual(res, expect_value)

    def test_get_all_added_attr_in_comment(self):
        expect_value = {'cdm_data_type': 'Point',
                        'Conventions': 'CF-1.10, COARDS, ACDD-1.3',
                        "acknowledgment": "acknowledgment",
                        "cdm_dataType": "profile",
                        "wmo_id": "6801509"}
        res = self.editor.get_all_global_attr(read_comments=True)
        self.assertEqual(res, expect_value)

    def test_get_all_attr(self):
        res = self.editor.get_all_attr()
        except_value_keys = {"reloadEveryNMinutes": "10080",
                             "fileDir": '/datasets/'}
        self.assertEqual(res, except_value_keys)

    def test_get_element_by_tag_generator_with_comment(self):
        res = list(self.editor.get_element_by_tag_generator_with_comment("dataVariable"))
        self.assertEqual(3, len(res))

    def test_remove_added_attr(self):
        self.editor.remove_global_variable("Conventions")
        expect_value = {'cdm_data_type': 'Point'}
        res = self.editor.get_all_global_attr()
        self.assertEqual(res, expect_value)

    def test_remove_attr(self):
        self.editor.remove_dataset_config("fileDir")
        res = self.editor.get_all_attr()
        except_value_keys = {"reloadEveryNMinutes": "10080"}
        self.assertEqual(res, except_value_keys)

    def test_remove_data_variable(self):
        index, child = self.editor._find_data_variable_by_source_name("time")
        self.assertNotEqual(index, None)
        self.assertNotEqual(child, None)
        self.editor.remove_data_variable("time")
        index, child = self.editor._find_data_variable_by_source_name("time")
        self.assertEqual(index, None)
        self.assertEqual(child, None)


    def test_get_all_data_variables_without_comment(self):
       res =  self.editor.get_all_data_variables(read_comments=False)
       self.assertEqual(3, len(res))


    def test_get_all_data_variables_with_comment(self):
       res =  self.editor.get_all_data_variables(read_comments=True)
       self.assertEqual(3, len(res))

    def test_set_erddap_config_for_adding_value(self):
        tag = "test_config_field"
        value = "test_config_value"
        self.editor.set_erddap_config(tag, value)
        self.editor.write(self.output_path_xml_path)

        # Read the XML file as a string
        with open(self.output_path_xml_path, "r", encoding="utf-8") as file:
            xml_content = file.readlines()
            for line in xml_content:
                if "test_config_field" in line and "test_config_value" in line:
                    break
            else:
                self.fail()

    def test_set_erddap_config_for_update_value(self):
        tag = "reloadEveryNMinutes"
        value = "1234"
        self.editor.set_erddap_config(tag, value)
        self.editor.write(self.output_path_xml_path)

        # Read the XML file as a string
        with open(self.output_path_xml_path, "r", encoding="utf-8") as file:
            xml_content = file.readlines()
            for line in xml_content:
                if "<reloadEveryNMinutes>1234</reloadEveryNMinutes>" in line:
                    break
            else:
                self.fail()

    def test_set_added_global_variable(self):
        tag = "cdm_data_type"
        value = "test_value"
        self.editor.set_added_global_variable(tag, value)
        self.editor.write(self.output_path_xml_path)


        # Read the XML file as a string
        with open(self.output_path_xml_path, "r", encoding="utf-8") as file:
            xml_content = file.readlines()
            for line in xml_content:
                if "<att name=\"cdm_data_type\">test_value</att>" in line:
                    break
            else:
                self.fail()


    def test_add_global_variable(self):

        tag = "new_global_variable"
        value = "new_test_value"
        self.editor.set_added_global_variable(tag, value)
        self.editor.write(self.output_path_xml_path)


        # Read the XML file as a string
        with open(self.output_path_xml_path, "r", encoding="utf-8") as file:
            xml_content = file.readlines()
            for line in xml_content:
                if "<att name=\"new_global_variable\">new_test_value</att>" in line:
                    break
            else:
                self.fail()


    def test_edit_dataset_data_variable_destination_name(self):
        source_name = "time"
        value = "new_time"
        self.editor.edit_data_variable_destination_name(source_name, value)
        self.editor.write(self.output_path_xml_path)


        # Read the XML file as a string
        with open(self.output_path_xml_path, "r", encoding="utf-8") as file:
            xml_content = file.readlines()
            for line in xml_content:
                if "<destinationName>new_time</destinationName>" in line:
                    break
            else:
                self.fail()

    def test_edit_data_variable_data_type(self):
        source_name = "time"
        value = "new_data_type"
        self.editor.edit_data_variable_data_type(source_name, value)
        self.editor.write(self.output_path_xml_path)


        # Read the XML file as a string
        with open(self.output_path_xml_path, "r", encoding="utf-8") as file:
            xml_content = file.readlines()
            for line in xml_content:
                if "<dataType>new_data_type</dataType>" in line:
                    break
            else:
                self.fail()

    def test_remove_dataset_data_variable(self):
        source_name = "time"

        self.editor.remove_data_variable(source_name)
        self.editor.write(self.output_path_xml_path)


        # Read the XML file as a string
        with open(self.output_path_xml_path, "r", encoding="utf-8") as file:
            xml_content = file.readlines()
            for line in xml_content:
                if "<sourceName>time</sourceName>" in line:
                    self.fail()


    def test_set_dataset_data_variable_add_attribute(self):
        source_name = "lat"
        attr_tag = "units"
        new_attr_value = "new_lat_unit"
        self.editor.set_data_variable_add_attribute(source_name, attr_tag, new_attr_value)
        self.editor.write(self.output_path_xml_path)


        # Read the XML file as a string
        with open(self.output_path_xml_path, "r", encoding="utf-8") as file:
            updated_unit = False
            xml_content = file.readlines()
            for line in xml_content:
                if "<att name=\"units\">new_lat_unit</att>" in line:
                    updated_unit = True
                if "<att name=\"units\">degrees_north</att>" in line:
                    self.fail()
        self.assertTrue(updated_unit)


    def test_add_new_data_variable_add_attribute(self):
        source_name = "lat"
        attr_tag = "something_fancy"
        new_attr_value = "something_new"
        self.editor.set_data_variable_add_attribute(source_name, attr_tag, new_attr_value)
        self.editor.write(self.output_path_xml_path)


        # Read the XML file as a string
        with open(self.output_path_xml_path, "r", encoding="utf-8") as file:
            xml_content = file.readlines()
            for line in xml_content:
                if "<att name=\"something_fancy\">something_new</att>" in line:
                    break
            else:
                self.fail()

    def test_add_data_variable(self):
        source_name = "trajectory"
        destination_name = "trajectory"
        data_type = "string"
        attrs = [{
            "name": "units",
            "type": "string",
            "value": "unit_value"
        },
            {
                "name": "ioos_category",
                "type": "double",
                "value": "other"
            }
        ]
        self.editor.add_data_variable(source_name, destination_name, data_type, attrs)
        self.editor.write(self.output_path_xml_path)
        # Read the XML file as a string
        with open(self.output_path_xml_path, "r", encoding="utf-8") as file:
            xml_content = file.readlines()
            for line in xml_content:
                if "<sourceName>trajectory</sourceName>" in line:
                    break
            else:
                self.fail()
        print("")