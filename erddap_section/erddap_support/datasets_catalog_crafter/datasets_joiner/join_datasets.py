import os
import logging

import lxml.etree as ET
from typing import Optional, List

from .processor import ProcessorLine
from ..constants import XML_EXTENSION
from ..data_structure import ErddapData

logger = logging.getLogger(__name__)


class DatasetCatalogJoiner:
    """
    This class is responsible for processing and combining individual dataset XML files
    into a single XML string. It ensures the uniqueness of dataset IDs, validates XML structure,
    and formats each dataset using a specified processor.

    Attributes:
        processor: A processing class responsible for handling individual XML files.
        sort_dataset: if or not to sort the dataset by modified time
    """
    processor = ProcessorLine
    sort_dataset = True

    def __init__(self, individuals_datasets_folder_path: str, erddap_data: ErddapData):
        """
        Initialize the DatasetJoiner with the directories.
        
        Args:
            individuals_datasets (str): Path to the datasets directory.
            output_dir (str): Path to the output directory.
        """
        self.datasets_dir = individuals_datasets_folder_path
        self.erddap_data = erddap_data

    def join_files(self) -> str:
        """
        Join XML files from the datasets directory into the combined file,
        ensuring no duplicate dataset IDs and validating XML.
        """
        content = ""
        for file_path in self.get_individual_xml():
            ret = self.process(file_path)
            if ret:
                root = ret.getroot()
                xml_str = ET.tostring(root, pretty_print=True, encoding='unicode', xml_declaration=False)
                content += xml_str
            else:
                logger.warning("bad {}".format(file_path))
        return content

    def get_individual_xml(self) -> List[str]:
        """
        Recursively retrieves all xml files from the given directory and its subdirectories,
        and sorts them by their modification time in ascending order (oldest to newest).

        Args:
            Directory (str): The path of the directory to search for files.

        Returns:
            List[str]: A list of XML file paths sorted by modification time.
        """

        # Initialize an empty list to store file paths
        files = []

        # Walk through the directory and its subdirectories recursively
        for root, _, filenames in os.walk(self.datasets_dir):
            for filename in filenames:
                # Build the full path for each file
                file_path = os.path.join(root, filename)

                # Check if it's a file and add to the list
                if os.path.isfile(file_path) and file_path.endswith(XML_EXTENSION):
                    files.append(file_path)

        # Sort the files by modification time
        if self.sort_dataset:
            files_sorted_by_mtime = sorted(files, key=lambda f: os.path.getmtime(f))
        else:
            files_sorted_by_mtime = files
        return files_sorted_by_mtime

    def process(self, file_path: str) -> Optional[ET.ElementTree]:
        """
        Processes the XML file and returns an ElementTree object if successful.

        Args:
            file_path (Path): The path of the XML file to process.

        Returns:
            Optional[ET.ElementTree]: The processed XML tree, or None if invalid.
        """
        processor = self.processor(file_path, self.erddap_data)
        try:
            tree = processor.process()
            return tree
        except ET.XMLSyntaxError as e:
            logger.error(f"XML Syntax Error in {file_path}: {e}")
        except OSError as e:
            logger.error(f"File I/O error in {file_path}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error processing {file_path}: {e}")
        return None

    def join(self) -> str:
        """
        Shortcut for join_files to return the combined XML string.

        Returns:
            str: Concatenated XML content.
        """
        ret = self.join_files()
        return ret
