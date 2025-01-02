import unittest
from unittest.mock import patch, mock_open, MagicMock
import os

from xml_monitor.datasets_catalog_crafter.dataset_crafter import DatasetsCrafter
from xml_monitor.datasets_catalog_crafter.data_structure import ErddapData


class TestDatasetsCrafter(unittest.TestCase):

    def setUp(self):
        self.datasets_data = ErddapData()
        self.individuals_datasets = '/path/to/individuals'
        self.output_dir = '/path/to/output'
        self.crafter = DatasetsCrafter(self.individuals_datasets, self.output_dir, self.datasets_data)

    @patch('xml_monitor.datasets_catalog_crafter.dataset_crafter.DatasetCatalogJoiner.join', return_value='joined datasets string')
    def test_get_join_datasets_str(self, mock_join):
        result = self.crafter._get_join_datasets_str()
        mock_join.assert_called_once()  # Ensure that join is called
        self.assertEqual(result, 'joined datasets string')

    @patch('xml_monitor.datasets_catalog_crafter.dataset_crafter.HeaderCrafter.get_header_str', return_value='header string')
    def test_get_header(self, mock_header):
        result = self.crafter._get_header()
        mock_header.assert_called_once()  # Ensure that get_header_str is called
        self.assertEqual(result, 'header string')

    @patch('xml_monitor.datasets_catalog_crafter.dataset_crafter.BaseTemplateCrafter.render', return_value='final datasets string')
    @patch('xml_monitor.datasets_catalog_crafter.dataset_crafter.DatasetsCrafter._get_join_datasets_str', return_value='joined datasets string')
    @patch('xml_monitor.datasets_catalog_crafter.dataset_crafter.DatasetsCrafter._get_header', return_value='header string')
    def test_get_datasets_str(self, mock_header, mock_join, mock_render):
        result = self.crafter._get_datasets_str()
        mock_header.assert_called_once()  # Ensure header is fetched
        mock_join.assert_called_once()    # Ensure datasets are joined
        mock_render.assert_called_once_with('datasets.xml', {
            'header': 'header string',
            'body': 'joined datasets string'
        })
        self.assertEqual(result, 'final datasets string')

    def test_datasets_path(self):
        expected_path = os.path.join(self.output_dir, 'datasets.xml')
        self.assertEqual(self.crafter.datasets_path, expected_path)

    @patch('os.path.isfile', return_value=True)
    @patch('shutil.move')
    def test_backup_dataset(self, mock_move, mock_isfile):
        self.crafter._backup_dataset()
        mock_isfile.assert_called_once_with(self.crafter.datasets_path)  # Ensure isfile is called
        backup_path = os.path.join(self.output_dir, 'datasets.xml.bak')
        mock_move.assert_called_once_with(self.crafter.datasets_path, backup_path)

    @patch('os.path.isfile', return_value=False)
    @patch('shutil.move')
    def test_backup_dataset_no_existing_file(self, mock_move, mock_isfile):
        self.crafter._backup_dataset()
        mock_isfile.assert_called_once_with(self.crafter.datasets_path)  # Ensure isfile is called
        mock_move.assert_not_called()  # Move should not be called if file doesn't exist

    @patch('builtins.open', new_callable=mock_open)
    def test_write(self, mock_file):
        datasets_xml_str = 'datasets xml content'
        self.crafter._write(datasets_xml_str)
        mock_file.assert_called_once_with(self.crafter.datasets_path, 'w')  # Ensure file is opened for writing
        mock_file().write.assert_called_once_with(datasets_xml_str)




if __name__ == '__main__':
    unittest.main()