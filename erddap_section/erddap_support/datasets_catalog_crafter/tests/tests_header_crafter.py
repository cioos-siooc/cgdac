import unittest

from unittest.mock import patch, mock_open
from erddap_section.erddap_support.datasets_catalog_crafter import header_crafter

from erddap_section.erddap_support.datasets_catalog_crafter.data_structure import ErddapData, Config

from dataclasses import asdict


class TestHeaderCrafter(unittest.TestCase):

    def setUp(self):
        """
        Set up the datasets_data and mock datasets_config for each test.
        """
        self.mock_datasets_config = Config()
        self.mock_datasets_config.standardPrivacyPolicyPath = '/path/to/data.txt'
        self.mock_datasets_config.standardLicense = 'otherValue'
        datasets_data = ErddapData(dataset_config=self.mock_datasets_config)
        self.header_crafter = header_crafter.HeaderCrafter(datasets_data)

    @patch('erddap_section.erddap_support.datasets_catalog_crafter.header_crafter.os.path.isfile', return_value=True)
    @patch('builtins.open', new_callable=mock_open, read_data='file content')
    def test_convert_path_with_valid_file(self, mock_file, mock_isfile):
        """
        Test that convert_path reads the file and replaces the 'Path' key correctly.
        """
        # Call convert_path directly with mock config
        updated_config = self.header_crafter.convert_path(asdict(self.mock_datasets_config))

        # Check if the 'data' key was created and the content was read from the file
        self.assertEqual(updated_config['standardPrivacyPolicy'], 'file content')

        # Ensure that the new key 'data' was created and 'dataPath' is still present
        self.assertIn('standardPrivacyPolicy', updated_config)
        self.assertIn('standardPrivacyPolicyPath', updated_config)

        # Check if open was called with the correct file path
        mock_file.assert_called_once_with('/path/to/data.txt', 'r', encoding='utf-8')

    @patch('erddap_section.erddap_support.datasets_catalog_crafter.header_crafter.os.path.isfile', return_value=False)
    def test_convert_path_with_invalid_file(self, mock_isfile):
        """
        Test that convert_path skips files that do not exist.
        """
        updated_config = self.header_crafter.convert_path(asdict(self.mock_datasets_config))

        # Ensure the 'data' key was not added since the file does not exist
        self.assertNotIn('data', updated_config)

    @patch('erddap_section.erddap_support.datasets_catalog_crafter.header_crafter.os.path.isfile', return_value=True)
    @patch('builtins.open', mock_open())
    def test_convert_path_file_read_error(self, mock_isfile):
        """
        Test that convert_path handles file read errors properly.
        """
        with patch('erddap_section.erddap_support.datasets_catalog_crafter.header_crafter.open', mock_open()) as mock_file:
            # Make open raise an OSError to simulate a file read error
            mock_file.side_effect = OSError("File read error")

            updated_config = self.header_crafter.convert_path(asdict(self.mock_datasets_config))

            # Ensure the 'data' key was not added since an error occurred
            self.assertNotIn('data', updated_config)

    @patch('erddap_section.erddap_support.datasets_catalog_crafter.header_crafter.os.path.isfile', return_value=True)
    @patch('builtins.open', new_callable=mock_open, read_data='header content')
    def test_get_header_str(self, mock_file, mock_isfile):
        """
        Test get_header_str to ensure it renders the template with the correct config.
        """
        with patch.object(self.header_crafter, 'render', return_value='Rendered Header'):
            header_str = self.header_crafter.get_header_str()

            # Ensure the render method was called with the correct template and config
            self.header_crafter.render.assert_called_once_with('header.xml', self.header_crafter.config_dict)

            # Ensure the returned header string is the expected output
            self.assertEqual(header_str, 'Rendered Header')

    def test_config_dict_lazy_initialization(self):
        """
        Test that config_dict is initialized lazily and cached after the first access.
        """
        # Initially _config_dict should be None
        self.assertIsNone(self.header_crafter._config_dict)

        # Accessing config_dict should initialize it
        _ = self.header_crafter.config_dict

        # Now _config_dict should no longer be None
        self.assertIsNotNone(self.header_crafter._config_dict)


if __name__ == '__main__':
    unittest.main()
