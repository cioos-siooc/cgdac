"""
This module contain the processor classes that we want to apply to each datasets
"""

import lxml.etree as ET
import logging
from typing import Optional
from ..data_structure import ErddapData

logger = logging.getLogger(__name__)


class BaseProcessor:
    """
    Abstract base class for processors. Each processor should implement the
    `process` method, which applies a transformation or validation to the given XML tree.
    """
    dataset_name = ""

    def process(self, tree: ET, **kwargs) -> Optional[ET.ElementTree]:
        """
        Process the given XML tree. This method must be implemented by subclasses.

        Args:
            tree (ET.ElementTree): The XML tree to process.
            **kwargs: Additional arguments that might be required by subclasses.

        Returns:
            ET.ElementTree: The processed XML tree.
        """
        raise NotImplementedError


class DatasetFormatFilterProcessor(BaseProcessor):
    dataset_name = ""

    def process(self, tree: ET, erddap_data: ErddapData = None) -> Optional[ET.ElementTree]:
        try:
            # Parse the XML file
            root = tree.getroot()
            # Check if the root tag is 'dataset'
            if root.tag == 'dataset':
                return tree
            else:
                logger.warning("Invalid dataset xml format.")
                return False
        except ET.XMLSyntaxError as e:
            logger.error(f"XML Syntax Error: {e}")
            return False


class ReplaceCredentialProcessor(BaseProcessor):
    dataset_name = "datasets_connection_properties"

    def process(self, tree: ET, erddap_data: ErddapData = None) -> ET.ElementTree:
        root = tree.getroot()
        dataset_id = root.get('datasetID')
        if erddap_data:
            datasets_connection_properties = erddap_data.datasets_connection_properties
            if dataset_id in datasets_connection_properties:
                # Find all connectionProperty elements
                connection_properties = root.findall('connectionProperty')

                # Iterate over them and check for the matching name attribute
                for prop in connection_properties:
                    name = prop.get('name')
                    if name in datasets_connection_properties[dataset_id]:
                        prop.text = datasets_connection_properties[dataset_id][name]
        return tree


class DatasetIDFilterProcessor(BaseProcessor):
    dataset_name = "deactivate_list"

    def process(self, tree: ET, erddap_data: ErddapData = None) -> ET:
        root = tree.getroot()
        dataset_id = root.get('datasetID')
        if erddap_data:
            if dataset_id in erddap_data.deactivate_list:
                return None
            else:
                return tree


processors = [DatasetFormatFilterProcessor, ReplaceCredentialProcessor, DatasetIDFilterProcessor]


class ProcessorLine:
    """
        The ProcessorLine class orchestrates the processing of XML datasets by applying a sequence of processors.
        It parses an XML file, passes it through a series of processors, and modifies the dataset accordingly.

        Attributes:
            parser (ET.XMLParser): XML parser with blank text removal.
            processor_list (List[BaseProcessor]): List of processors to apply to the dataset. Each processor
                implements the 'process()' method, which transforms or validates the XML tree.

        Args:
            file_path (str): The path to the XML file to be processed.
            erddap_data (ErddapData): Data passed to processors, such as configuration or connection properties.

        Usage:
            To extend the processing, implement a subclass of `BaseProcessor` and override the `process()` method
            to define custom processing logic. Then, add the new processor to the `processor_list`.

            Example:
                class MyCustomProcessor(BaseProcessor):
                    def process(self, tree: ET.ElementTree, erddap_data: ErddapData = None) -> Optional[ET.ElementTree]:
                        # Custom processing logic
                        return tree

                # Add the new processor to the processor list
                processors.append(MyCustomProcessor)
        """
    parser = ET.XMLParser(remove_blank_text=True)
    processor_list = processors

    def __init__(self, file_path: str, erddap_data: ErddapData):
        self.file_path = file_path
        self._tree = None
        self.datasets_data = erddap_data

    @property
    def tree(self):
        if self._tree is None:
            tree = ET.parse(self.file_path, self.parser)
            self._tree = tree
        return self._tree

    def process(self):
        tree = self.tree
        for processor in self.processor_list:
            if tree:
                try:
                    tree = processor().process(tree, self.datasets_data)
                    if not tree:
                        logger.warning(f"Processor {processor.__name__} returned None, skipping further processing.")
                except Exception as e:
                    logger.error(f"Error during processing in {processor.__name__}: {e}")
                    return None
            else:
                logger.warning("Processing chain aborted due to previous errors.")
                return None
        return tree
