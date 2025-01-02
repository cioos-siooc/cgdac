import unittest
from unittest.mock import MagicMock, patch
from typing import Dict
import os
from erddap_section.erddap_support.individual_erddap_dataset_catalog_creator.individual_erddap_dataset_catalog_handler import \
    IndividualErddapDatasetCatalogHandler


# Mock for validate_dict_keys function
def mock_validate_dict_keys(dictionary: Dict[str, str], required_keys: list, dict_name: str) -> None:
    missing_keys = [key for key in required_keys if key not in dictionary]
    if missing_keys:
        raise ValueError(f"Missing keys in {dict_name}: {', '.join(missing_keys)}")


class TestIndividualErddapDatasetCatalogHandler(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = {
            "generate_datasets_xml_command_path": "/path/to/generate_datasets_xml_command",
            "dataset_config_root": "/path/to/dataset_config"
        }
        cls.deployment_dict = {
            "user": "test_user"
        }
        cls.erddap_dict = {
            "some_erddap_key": "some_value"
        }
        cls.dataset_dict = {
            "dataset_id": "test_dataset"
        }

    def setUp(self):
        # Patch validate_dict_keys to avoid key validation errors in the tests
        patcher = patch('erddap_section.erddap_support.individual_erddap_dataset_catalog_creator.individual_erddap_dataset_catalog_handler.validate_dict_keys', mock_validate_dict_keys)
        self.addCleanup(patcher.stop)
        self.mock_validate_dict_keys = patcher.start()

        # Initialize the handler
        self.handler = IndividualErddapDatasetCatalogHandler(
            self.config,
            self.deployment_dict,
            self.erddap_dict,
            self.dataset_dict
        )

    @patch('erddap_section.erddap_support.individual_erddap_dataset_catalog_creator.individual_erddap_dataset_catalog_handler.os.makedirs')
    def test_output_property(self, mock_makedirs):
        mock_instance = MagicMock()
        mock_instance.generate.return_value = None
        mock_makedirs.return_value = mock_instance

        expected_output = os.path.join(
            self.config["dataset_config_root"],
            self.deployment_dict["user"],
            self.dataset_dict["dataset_id"]
        )
        self.assertEqual(self.handler.output, expected_output)



    @patch('erddap_section.erddap_support.individual_erddap_dataset_catalog_creator.individual_erddap_dataset_catalog_handler.ERDDAPGenerateDatasetsXMLCommandGenerator')
    @patch('erddap_section.erddap_support.individual_erddap_dataset_catalog_creator.individual_erddap_dataset_catalog_handler.DraftDatasetChunkCreator')
    @patch('erddap_section.erddap_support.individual_erddap_dataset_catalog_creator.individual_erddap_dataset_catalog_handler.os.makedirs')
    def test_generate_draft_dataset_xml_success(self, mock_command_generator, mock_creator, mock_makedirs):
        # Mock DraftDatasetChunkCreator behavior
        mock_instance = MagicMock()
        mock_instance.generate.return_value = "/path/to/generated/draft.xml"
        mock_creator.return_value = mock_instance


        # Mock command generator behavior
        command_generator_mock_instance = MagicMock()
        command_generator_mock_instance.generate.return_value = "mocked command"
        mock_command_generator.return_value = command_generator_mock_instance


        # mock the mkdirs
        mkdirs_mock_instance = MagicMock()
        mkdirs_mock_instance.generate.return_value = None
        mock_makedirs.return_value = mkdirs_mock_instance

        # Call the method
        output = self.handler.generate_draft_dataset_xml()

        # Assert correct calls
        mock_creator.assert_called_once_with(
            self.handler.generate_generation_command(),
            self.dataset_dict,
            self.erddap_dict,
            self.handler.output
        )
        mock_instance.generate.assert_called_once()
        self.assertEqual(output, "/path/to/generated/draft.xml")

    @patch('erddap_section.erddap_support.individual_erddap_dataset_catalog_creator.individual_erddap_dataset_catalog_handler.os.makedirs')
    @patch('erddap_section.erddap_support.individual_erddap_dataset_catalog_creator.individual_erddap_dataset_catalog_handler.DraftDatasetChunkCreator')
    @patch('erddap_section.erddap_support.individual_erddap_dataset_catalog_creator.individual_erddap_dataset_catalog_handler.ERDDAPGenerateDatasetsXMLCommandGenerator')
    def test_generate_draft_dataset_xml_failure(self, mock_command_generator, mock_creator, mock_makedirs):
        # Mock DraftDatasetChunkCreator to raise an exception
        mock_instance = MagicMock()
        mock_instance.generate.side_effect = RuntimeError("Generation failed")
        mock_creator.return_value = mock_instance

        command_generator_mock_instance = MagicMock()
        command_generator_mock_instance.generate.return_value = "test_command"
        mock_command_generator.return_value = command_generator_mock_instance


        mkdir_mock_instance = MagicMock()
        mkdir_mock_instance.generate.return_value = None
        mock_makedirs.return_value = mkdir_mock_instance


        # Call the method and assert the exception
        with self.assertRaises(RuntimeError):
            self.handler.generate_draft_dataset_xml()

        # Assert correct calls
        mock_creator.assert_called_once_with(
            self.handler.generate_generation_command(),
            self.dataset_dict,
            self.erddap_dict,
            self.handler.output
        )
        mock_instance.generate.assert_called_once()

    def test_missing_required_keys(self):
        # Missing keys in config
        invalid_config = {"dataset_config_root": "/path/to/dataset_config"}
        with self.assertRaises(ValueError):
            IndividualErddapDatasetCatalogHandler(
                invalid_config,
                self.deployment_dict,
                self.erddap_dict,
                self.dataset_dict
            )

        # Missing keys in deployment_dict
        invalid_deployment_dict = {}
        with self.assertRaises(ValueError):
            IndividualErddapDatasetCatalogHandler(
                self.config,
                invalid_deployment_dict,
                self.erddap_dict,
                self.dataset_dict
            )

        # Missing keys in dataset_dict
        invalid_dataset_dict = {}
        with self.assertRaises(ValueError):
            IndividualErddapDatasetCatalogHandler(
                self.config,
                self.deployment_dict,
                self.erddap_dict,
                invalid_dataset_dict
            )


if __name__ == "__main__":
    unittest.main()
