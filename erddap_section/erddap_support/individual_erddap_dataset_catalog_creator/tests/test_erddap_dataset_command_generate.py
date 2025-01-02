import unittest
from unittest.mock import patch

from erddap_section.erddap_support.individual_erddap_dataset_catalog_creator.erddap_dataset_command_generate import (
    ERDDAPGenerateDatasetsXMLCommandGenerator
)

from unittest.mock import patch

# Mock the helper functions
def mock_add_nothing_str(command):
    return command + " nothing"

def mock_add_str(command, item):
    return f"{command} {item}"

def mock_str_wrapper(item):
    return f"'{item}'"


class TestERDDAPGenerateDatasetsXMLCommandGenerator(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.generate_datasets_xml_command_path = "path/to/command"
        cls.dataset_dict = {
            "title": "Test Title",
            "data_dir": "/data",
            "file_name": "data_file.nc"
        }
        cls.deployment_dict = {
            "info_url": "http://example.com",
            "institution": "Test Institution",
            "summary": "Test Summary",
       }
        cls.generator = ERDDAPGenerateDatasetsXMLCommandGenerator(
            cls.generate_datasets_xml_command_path, cls.deployment_dict, cls.dataset_dict
        )

    def test_info_url(self):
        self.assertEqual(self.generator.info_url(), "http://example.com")

    def test_institution(self):
        self.assertEqual(self.generator.institution(), "Test Institution")

    def test_summary(self):
        self.assertEqual(self.generator.summary(), "Test Summary")

    def test_title(self):
        self.assertEqual(self.generator.title(), "Test Title")

    def test_data_dir(self):
        self.assertEqual(self.generator.data_dir(), "/data")

    def test_file_name(self):
        self.assertEqual(self.generator.file_name(), "data_file.nc")

    def test_lazy_loading(self):
        # Ensure properties are not loaded until accessed
        self.assertIsNone(self.generator._info_url)
        self.generator.info_url()
        self.assertEqual(self.generator._info_url, "http://example.com")

    def test_generate_command(self):
        with patch("erddap_section.erddap_support.individual_erddap_dataset_catalog_creator.erddap_dataset_command_generate.add_str", mock_add_str), \
             patch("erddap_section.erddap_support.individual_erddap_dataset_catalog_creator.erddap_dataset_command_generate.add_nothing_str", mock_add_nothing_str), \
             patch("erddap_section.erddap_support.individual_erddap_dataset_catalog_creator.erddap_dataset_command_generate.str_wrapper", mock_str_wrapper):
            command = self.generator.generate()
            expected = (
                "path/to/command 'EDDTableFromNcFiles' '/data' '.*\\.nc' 'data_file.nc' nothing 40320 nothing "
                "nothing nothing nothing nothing nothing 'http://example.com' 'Test Institution' 'Test Summary' 'Test Title'"
            )
            self.assertEqual(command, expected)

    def test_generate_command_with_missing_key(self):
        # Test missing keys in dataset_dict
        dataset_dict = {
            "infoUrl": "http://example.com",
            "institution": "Test Institution",
            "summary": "Test Summary",
            # Missing title and data_dir
        }
        generator = ERDDAPGenerateDatasetsXMLCommandGenerator(
            self.generate_datasets_xml_command_path, self.deployment_dict, dataset_dict
        )
        with self.assertRaises(KeyError):
            generator.data_dir()

    def test_full_workflow(self):
        with patch("erddap_section.erddap_support.individual_erddap_dataset_catalog_creator.erddap_dataset_command_generate.add_str", mock_add_str), \
             patch("erddap_section.erddap_support.individual_erddap_dataset_catalog_creator.erddap_dataset_command_generate.add_nothing_str", mock_add_nothing_str), \
             patch("erddap_section.erddap_support.individual_erddap_dataset_catalog_creator.erddap_dataset_command_generate.str_wrapper", mock_str_wrapper):
            command = self.generator.generate()
            self.assertIn("path/to/command", command)
            self.assertIn("EDDTableFromNcFiles", command)
            self.assertIn("/data", command)
            self.assertIn("data_file.nc", command)
            self.assertIn("http://example.com", command)

    def test_generate_with_invalid_path(self):
        generator = ERDDAPGenerateDatasetsXMLCommandGenerator(
            "invalid/path/to/command", self.deployment_dict, self.dataset_dict
        )
        with self.assertRaises(Exception):
            generator.generate()

    def test_none_handling(self):
        # Test None values in dataset_dict
        dataset_dict = {
            "infoUrl": None,
            "institution": None,
            "summary": None,
            "title": None,
            "data_dir": None,
            "file_name": None
        }
        generator = ERDDAPGenerateDatasetsXMLCommandGenerator(
            self.generate_datasets_xml_command_path, self.deployment_dict, dataset_dict
        )
        with patch("erddap_section.erddap_support.individual_erddap_dataset_catalog_creator.erddap_dataset_command_generate.add_str", mock_add_str), \
             patch("erddap_section.erddap_support.individual_erddap_dataset_catalog_creator.erddap_dataset_command_generate.add_nothing_str", mock_add_nothing_str), \
             patch("erddap_section.erddap_support.individual_erddap_dataset_catalog_creator.erddap_dataset_command_generate.str_wrapper", mock_str_wrapper):
            command = generator.generate()
            self.assertIn("nothing", command)

    def test_missing_dataset_dict(self):
        # Test if dataset_dict is completely missing or invalid
        with self.assertRaises(KeyError):
            generator = ERDDAPGenerateDatasetsXMLCommandGenerator(
                self.generate_datasets_xml_command_path, self.deployment_dict, {}
            )
            generator.data_dir()


if __name__ == "__main__":
    unittest.main()