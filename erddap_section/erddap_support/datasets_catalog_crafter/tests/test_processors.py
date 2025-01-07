import unittest
from unittest.mock import patch, MagicMock
import lxml.etree as ET
from erddap_section.erddap_support.datasets_catalog_crafter.datasets_joiner.processor import DatasetFormatFilterProcessor, ReplaceCredentialProcessor, DatasetIDFilterProcessor, ProcessorLine
from erddap_section.erddap_support.datasets_catalog_crafter.data_structure import ErddapData


class TestDatasetFormatFilterProcessor(unittest.TestCase):

    def test_process_valid_dataset(self):
        """
        Test that DatasetFormatFilterProcessor returns the tree for valid dataset XML.
        """
        xml_content = """<dataset datasetID="test_id"></dataset>"""
        tree = ET.ElementTree(ET.fromstring(xml_content))

        processor = DatasetFormatFilterProcessor()
        result = processor.process(tree)

        self.assertEqual(result, tree)

    def test_process_invalid_dataset(self):
        """
        Test that DatasetFormatFilterProcessor returns False for invalid dataset XML.
        """
        xml_content = """<not_dataset></not_dataset>"""
        tree = ET.ElementTree(ET.fromstring(xml_content))

        processor = DatasetFormatFilterProcessor()
        result = processor.process(tree)

        self.assertFalse(result)


class TestReplaceCredentialProcessor(unittest.TestCase):

    def test_replace_credential(self):
        """
        Test that ReplaceCredentialProcessor replaces credentials correctly.
        """
        xml_content = """
        <dataset datasetID="test_id">
            <connectionProperty name="user">old_user</connectionProperty>
        </dataset>
        """
        tree = ET.ElementTree(ET.fromstring(xml_content))
        extra_data = {"test_id": {"user": "new_user"}}
        dataset_data = ErddapData()
        dataset_data.datasets_connection_properties = extra_data
        processor = ReplaceCredentialProcessor()
        result = processor.process(tree, erddap_data=dataset_data)

        # Check that the user was updated
        user_prop = result.find(".//connectionProperty[@name='user']")
        self.assertEqual(user_prop.text, "new_user")

    def test_no_replace_credential(self):
        """
        Test that ReplaceCredentialProcessor does nothing when datasetID is not in extra data.
        """
        xml_content = """
        <dataset datasetID="test_id">
            <connectionProperty name="user">old_user</connectionProperty>
        </dataset>
        """
        tree = ET.ElementTree(ET.fromstring(xml_content))
        extra_data = {"another_id": {"name": "new_user"}}

        processor = ReplaceCredentialProcessor()
        datasets_data = ErddapData()
        datasets_data.datasets_connection_properties = extra_data
        result = processor.process(tree, erddap_data=datasets_data)

        # Check that the user was not updated
        user_prop = result.find(".//connectionProperty[@name='user']")
        self.assertEqual(user_prop.text, "old_user")


class TestDatasetIDFilterProcessor(unittest.TestCase):

    def test_dataset_id_filter_in_extra(self):
        """
        Test that DatasetIDFilterProcessor returns the tree when datasetID is in extra data.
        """
        xml_content = """<dataset datasetID="test_id"></dataset>"""
        tree = ET.ElementTree(ET.fromstring(xml_content))

        extra_data = ["test_id"]
        dataset_meta = ErddapData()
        dataset_meta.deactivate_list = extra_data
        processor = DatasetIDFilterProcessor()
        result = processor.process(tree, erddap_data=dataset_meta)

        self.assertIsNone(result)


    def test_dataset_id_filter_not_in_extra(self):
        """
        Test that DatasetIDFilterProcessor returns None when datasetID is not in extra data.
        """
        xml_content = """<dataset datasetID="test_id"></dataset>"""
        tree = ET.ElementTree(ET.fromstring(xml_content))
        extra_data = ["another_id"]
        dataset_meta = ErddapData()
        dataset_meta.deactivate_list = extra_data
        processor = DatasetIDFilterProcessor()
        result = processor.process(tree, erddap_data=dataset_meta)

        self.assertEqual(result, tree)


class TestProcessorLine(unittest.TestCase):

    @patch('erddap_section.erddap_support.datasets_catalog_crafter.datasets_joiner.processor.ET.parse')
    def test_tree_loading(self, mock_parse):
        """
        Test that ProcessorLine correctly loads the XML tree.
        """
        mock_tree = MagicMock()
        mock_parse.return_value = mock_tree

        processor_line = ProcessorLine("/path/to/file.xml", ErddapData())

        # Accessing the tree should load the XML
        tree = processor_line.tree
        mock_parse.assert_called_once_with("/path/to/file.xml", processor_line.parser)
        self.assertEqual(tree, mock_tree)

    @patch('erddap_section.erddap_support.datasets_catalog_crafter.datasets_joiner.processor.DatasetFormatFilterProcessor.process', return_value=None)
    def test_process(self, dataset_format_filter_process):
        """
        Test that ProcessorLine runs all processors and processes the tree.
        """
        mock_tree = MagicMock()
        datasets_data = ErddapData()
        processor_line = ProcessorLine("/path/to/file.xml", datasets_data)
        processor_line._tree = mock_tree  # Simulate the tree being loaded
        processor_line.processor_list[0].process = dataset_format_filter_process
        result = processor_line.process()


        # Ensure first processor were called, since one processor is failed, it won't keep going to next processor
        dataset_format_filter_process.assert_called_once_with(mock_tree, datasets_data)

        self.assertIsNone(result)  # Because both processors return None


if __name__ == '__main__':
    unittest.main()