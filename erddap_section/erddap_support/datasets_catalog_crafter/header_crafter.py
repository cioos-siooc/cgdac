import os
import logging
from .base import BaseTemplateCrafter
from .data_structure import ErddapData
from .constants import FILE_PATH_SUFFIX, HEADER_TEMPLATE
from dataclasses import asdict
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class HeaderCrafter(BaseTemplateCrafter):
    """
    The HeaderCrafter class is responsible for generating and customizing the header section of ERDDAP datasets.xml.
    The header defines the behavior and appearance of ERDDAP before section of the actual datasets configurations.
    This class allows users to craft specific customizations for how ERDDAP presents and behaves by manipulating the
    header configuration based on the provided datasets data.
    """

    def __init__(self, erddap_data: ErddapData):
        super().__init__()
        self.datasets_config = erddap_data.dataset_config
        self._config_dict: Optional[Dict[str, Any]] = None

    @property
    def config_dict(self) -> Dict[str, Any]:
        """
        Lazily initialize and cache the configuration dictionary.
        Converts file paths and reads their contents into the dict.

        Returns:
            Dict[str, Any]: The configuration dictionary.
        """
        if self._config_dict is None:
            config_dict = asdict(self.datasets_config)
            self._config_dict = self.convert_path(config_dict)
        return self._config_dict

    def get_header_str(self) -> str:
        """
        Renders the header template using the configuration dictionary.

        Returns:
            str: The rendered header string.
        """
        return self.render(HEADER_TEMPLATE, self.config_dict)

    def convert_path(self, config_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Converts any file paths in the config dictionary by reading file contents
        for keys that end with 'Path'. The 'Path' suffix is removed from the key name.

        Args:
            config_dict (Dict[str, Any]): The configuration dictionary.

        Returns:
            Dict[str, Any]: The updated configuration dictionary.
        """
        updated_dict = config_dict.copy()  # Copy to avoid modifying the dict while iterating

        for key_name, value in config_dict.items():
            if key_name.endswith(FILE_PATH_SUFFIX) and value and os.path.isfile(value):

                new_key = key_name[:-len(FILE_PATH_SUFFIX)]  # Remove the "Path" suffix
                try:
                    with open(value, 'r', encoding='utf-8') as f:
                        updated_dict[new_key] = f.read()
                except OSError as e:
                    # Log or handle file reading errors

                    logger.error(f"Error reading file for {key_name}: {e}")

        return updated_dict
