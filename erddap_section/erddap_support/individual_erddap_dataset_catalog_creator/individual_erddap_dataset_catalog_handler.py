import os.path
import logging
from typing import Dict
from erddap_section.erddap_support.individual_erddap_dataset_catalog_creator.erddap_dataset_command_generate import ERDDAPGenerateDatasetsXMLCommandGenerator
from erddap_section.erddap_support.individual_erddap_dataset_catalog_creator.draft_dataset_xml_creator import DraftDatasetChunkCreator

logger = logging.getLogger(__name__)


def validate_dict_keys(dictionary: Dict[str, str], required_keys: list, dict_name: str) -> None:
    missing_keys = [key for key in required_keys if key not in dictionary]
    if missing_keys:
        raise ValueError(f"Missing keys in {dict_name}: {', '.join(missing_keys)}")


class IndividualErddapDatasetCatalogHandler:
    def __init__(self, config: Dict[str, str], deployment_dict: Dict[str, str],
                 erddap_dict: Dict[str, str], dataset_dict: Dict[str, str]) -> None:
        validate_dict_keys(config, ["generate_datasets_xml_command_path", "dataset_config_root"], "config")
        validate_dict_keys(deployment_dict, ["user"], "deployment_dict")
        validate_dict_keys(dataset_dict, ["dataset_id"], "dataset_dict")
        self.config = config
        self.deployment_dict = deployment_dict
        self.erddap_dict = erddap_dict
        self.dataset_dict = dataset_dict

    def generate_datasets_xml_command_path(self) -> str:
        return self.config["generate_datasets_xml_command_path"]

    def generate_generation_command(self) -> str:
        logger.debug("Generating command for datasets XML")
        command_generator = ERDDAPGenerateDatasetsXMLCommandGenerator(self.generate_datasets_xml_command_path(),
                                                                      self.deployment_dict, self.dataset_dict, self.erddap_dict)
        command = command_generator.generate()
        logger.debug(f"Generated command: {command}")
        return command

    @property
    def output(self) -> str:
        path_components = [
            self.config["dataset_config_root"],
            self.deployment_dict["user"],
            self.dataset_dict["dataset_id"]
        ]
        output_path = os.path.join(*path_components)
        # Ensure the output directory exists
        try:
            if not os.path.exists(output_path):
                os.makedirs(output_path, exist_ok=True)
                logger.info(f"Created output directory: {output_path}")
        except Exception as e:
            raise e
        return output_path

    def generate_draft_dataset_xml(self) -> str:
        logger.info("Starting draft dataset XML generation")
        creator = DraftDatasetChunkCreator(self.generate_generation_command(),
                                           self.dataset_dict,
                                           self.erddap_dict,
                                           self.output)
        try:
            output_path = creator.generate()
            logger.info(f"Draft dataset XML generated successfully at {self.output}")
        except Exception as e:
            logger.error(f"Failed to generate draft dataset XML: {e}")
            raise
        return output_path
