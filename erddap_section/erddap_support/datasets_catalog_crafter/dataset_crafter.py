import os
import shutil
import logging

from .datasets_joiner import DatasetCatalogJoiner
from .base import BaseTemplateCrafter
from .header_crafter import HeaderCrafter

from .constants import DATASETS_NAME, BAK_EXTENSION
from .data_structure import ErddapData, UpdateMessages
from lxml import etree as ET

logger = logging.getLogger(__name__)


class DatasetsCrafter(BaseTemplateCrafter):
    dataset_catalog_joiner_class = DatasetCatalogJoiner
    dataset_header_maker_class = HeaderCrafter

    def __init__(self, individuals_datasets: str, output_dir: str, erddap_data: ErddapData):
        """
        Initializes the DatasetsCrafter class.

        Args:
            individuals_datasets (str): Path to the directory containing individual datasets.
            output_dir (str): Directory where the datasets.xml will be saved.
            erddap_data (ErddapData): The ERDDAP data passed to the module.
        """
        super().__init__()
        self.individuals_datasets_dir = individuals_datasets
        self.output_dir = output_dir
        self._datasets_xml_path = None
        self.erddap_data = erddap_data
        self._dataset_catalog_joiner = None
        self._dataset_header_maker = None

    def _get_join_datasets_str(self) -> str:
        """
        Joins individual datasets into a single string representation of the datasets.

        Returns:
            str: The joined datasets as a string.
        """
        self._dataset_catalog_joiner = self.dataset_catalog_joiner_class(self.individuals_datasets_dir,
                                                                         self.erddap_data)
        datasets_str = self._dataset_catalog_joiner.join()
        return datasets_str

    def _get_header(self) -> str:
        """
        Generates the header for the datasets XML.

        Returns:
            str: The header as a string.
        """
        self._dataset_header_maker = self.dataset_header_maker_class(self.erddap_data)
        header_str = self._dataset_header_maker.get_header_str()
        return header_str

    def _get_datasets_str(self) -> str:
        """
        Combines the header and joined datasets to form the complete datasets XML string.

        Returns:
            str: The full datasets XML content as a string.
        """
        datasets_join_str = self._get_join_datasets_str()
        header_str = self._get_header()
        datasets_str = self.render('datasets.xml', {
            'header': header_str,
            'body': datasets_join_str
        })
        return datasets_str

    @property
    def datasets_path(self) -> str:
        """
        Provides the path to the datasets.xml file, generating it if necessary.

        Returns:
            str: The full path to the datasets.xml file.
        """
        if self._datasets_xml_path is None:
            self._datasets_xml_path = os.path.join(self.output_dir, DATASETS_NAME)
        return self._datasets_xml_path

    def _backup_dataset(self) -> None:
        """
        Backup the existing datasets.xml file if it exists.
        Moves the datasets.xml file to datasets.xml.bak.
        """
        backup_path = os.path.join(self.output_dir, f"{DATASETS_NAME}{BAK_EXTENSION}")

        if os.path.isfile(self.datasets_path):
            try:
                shutil.move(self.datasets_path, backup_path)
                logger.debug(f"Backup successful: {self.datasets_path} -> {backup_path}")
            except Exception as e:
                logger.error(f"Failed to backup the dataset file: {e}")

    def _write(self, datasets_xml_str) -> None:
        """
        Writes the datasets XML string to the datasets.xml file.

        Args:
            datasets_xml_str (str): The datasets XML content to be written.
        """
        try:
            with open(self.datasets_path, 'w') as outfile:
                outfile.write(datasets_xml_str)
            logger.info(f"datasets.xml successfully written to {self.datasets_path}")
        except Exception as e:
            logger.error(f"Failed to write datasets.xml: {e}")
            raise

    def get_update_message(self) -> UpdateMessages:
        """
        Creates and returns an update message object.

        Returns:
            UpdateMessages: An object containing update messages.
        """
        return UpdateMessages()

    @staticmethod
    def _validate_xml(xml_str):
        try:
            # Parse the XML string
            parser = ET.XMLParser(remove_blank_text=True)
            root = ET.fromstring(xml_str.encode('utf-8'), parser)
            logger.debug("The XML is well-formed and valid.")
            return True
        except ET.XMLSyntaxError as e:
            logger.error(f"XML Syntax Error: {e}")
            return False

    def build(self) -> UpdateMessages:
        """
        Constructs the datasets.xml by combining datasets and header, backing up any existing file,
        and writing the new datasets.xml file. Returns update messages.

        Returns:
            UpdateMessages: Update messages after building the datasets.xml.
        """
        datasets_str = self._get_datasets_str()
        if self._validate_xml(datasets_str):
            self._backup_dataset()
            self._write(datasets_str)
        return self.get_update_message()
