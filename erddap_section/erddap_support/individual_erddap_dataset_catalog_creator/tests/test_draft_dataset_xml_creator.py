import os
import subprocess
import tempfile
import unittest
from unittest.mock import patch, MagicMock
from erddap_section.erddap_support.individual_erddap_dataset_catalog_creator.draft_dataset_xml_creator import \
    DraftDatasetChunkCreator

class TestDraftDatasetChunkCreator(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.program_command = "EDDTableFromNcFiles /datasets/dataset2 .*\.nc test_dataset.nc nothing nothing nothing nothing nothing nothing nothing nothing nothing nothing nothing nothing nothing nothing"
        cls.dataset_dict = {
            "nc_file_path": "/path/to/nc/file.nc"
        }
        cls.erddap_dict = {
            "erddap_big_parents_path": "/path/to/erddap"
        }
        cls.output_dir = "/path/to/output"
        cls.creator = DraftDatasetChunkCreator(
            cls.program_command, cls.dataset_dict, cls.erddap_dict, cls.output_dir
        )

    @patch("os.path.isdir")
    def test_nc_file_path(self, mock_isdir):
        # Mock the directory check
        mock_isdir.return_value = True
        self.assertEqual(self.creator.nc_file_path, "/path/to/nc/file.nc")

    def test_draft_output_log_path(self):
        expected_path = "/path/to/erddap/logs/GenerateDatasetsXml.out"
        self.assertEqual(self.creator.draft_output_log_path, expected_path)

    @patch("os.path.isdir")
    def test_output_dir_exists(self, mock_isdir):
        mock_isdir.return_value = True
        self.assertEqual(self.creator.output_dir, "/path/to/output")

    @patch("os.path.isdir")
    def test_output_dir_not_exists(self, mock_isdir):
        mock_isdir.return_value = False
        with self.assertRaises(FileNotFoundError):
            _ = self.creator.output_dir

    @patch("subprocess.run")
    def test_generate_raw_xml_success(self, mock_run):
        # Mock subprocess.run to simulate successful command execution
        mock_run.return_value = MagicMock(returncode=0, stdout="Success")
        result_code = self.creator.generate_raw_xml()
        self.assertEqual(result_code, 0)

    @patch("subprocess.run")
    def test_generate_raw_xml_failure(self, mock_run):
        # Mock subprocess.run to simulate a failure
        mock_run.side_effect = subprocess.CalledProcessError(
            returncode=1, cmd=self.program_command, stderr="Command failed"
        )
        with self.assertRaises(subprocess.CalledProcessError):
            self.creator.generate_raw_xml()

    @patch("shutil.copy")
    @patch("os.path.isdir")
    def test_mv_output_to_output_dir_success(self, mock_isdir, mock_copy):
        # Mock the necessary functions
        mock_isdir.return_value = True
        self.creator.mv_output_to_output_dir()
        mock_copy.assert_called_once_with(
            "/path/to/erddap/logs/GenerateDatasetsXml.out", "/path/to/output"
        )

    @patch("shutil.copy")
    @patch("os.path.isdir")
    def test_mv_output_to_output_dir_file_not_found(self, mock_isdir, mock_copy):
        mock_isdir.return_value = True
        mock_copy.side_effect = FileNotFoundError


