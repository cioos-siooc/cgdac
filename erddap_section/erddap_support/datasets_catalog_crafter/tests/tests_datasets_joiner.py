import unittest
from unittest.mock import patch, MagicMock
import os
from xml_monitor.datasets_catalog_crafter.datasets_joiner import DatasetCatalogJoiner
from xml_monitor.datasets_catalog_crafter.data_structure import ErddapData


class TestDatasetCatalogJoiner(unittest.TestCase):

    def setUp(self):
        # Create a mock DatasetsData instance
        self.erddap_data = ErddapData()
        self.individuals_datasets_dir = '/path/to/individuals_datasets'
        self.joiner = DatasetCatalogJoiner(self.individuals_datasets_dir, self.erddap_data)

    @patch('xml_monitor.datasets_catalog_crafter.datasets_joiner.join_datasets.os.path.isfile', return_value=True)
    @patch('xml_monitor.datasets_catalog_crafter.datasets_joiner.join_datasets.os.path.getmtime', return_value=100)
    @patch('xml_monitor.datasets_catalog_crafter.datasets_joiner.join_datasets.os.walk')
    def test_get_individual_xml(self, mock_walk, mock_getmtime, mock_isfile):
        """
        Test that get_individual_xml correctly retrieves and sorts XML files by modification time.
        """
        # Mock the file structure returned by os.walk
        mock_walk.return_value = [
            ('/path/to/individuals_datasets', [], ['file1.xml', 'file2.xml', 'file3.txt']),
        ]

        result = self.joiner.get_individual_xml()

        # Ensure only .xml files are returned, sorted by modification time
        self.assertEqual(result, [
            '/path/to/individuals_datasets/file1.xml',
            '/path/to/individuals_datasets/file2.xml'
        ])

        mock_isfile.assert_any_call('/path/to/individuals_datasets/file1.xml')
        mock_isfile.assert_any_call('/path/to/individuals_datasets/file2.xml')
        mock_walk.assert_called_once_with('/path/to/individuals_datasets')

    @patch('xml_monitor.datasets_catalog_crafter.datasets_joiner.processor.ProcessorLine.process')
    def test_process_invalid_file(self, mock_processor):
        """
        Test that the process method handles an invalid XML file.
        """
        # Mock an invalid file processing that raises an exception
        mock_processor.side_effect = Exception('Invalid XML')

        # Call the process method
        result = self.joiner.process('/path/to/invalid_file.xml')

        # Ensure the processor was called
        mock_processor.assert_called_once_with()

        # Ensure that the result is None due to the exception
        self.assertIsNone(result)

    @patch('xml_monitor.datasets_catalog_crafter.datasets_joiner.DatasetCatalogJoiner.join_files',
           return_value='<xml>joined_content</xml>')
    def test_join(self, mock_join_files):
        """
        Test that the join method correctly returns the joined XML content.
        """
        result = self.joiner.join()

        # Ensure the join_files method was called
        mock_join_files.assert_called_once()

        # Ensure the result is the joined content
        self.assertEqual(result, '<xml>joined_content</xml>')


if __name__ == '__main__':
    unittest.main()
