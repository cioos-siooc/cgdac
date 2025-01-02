import logging
from common import log_formatter

logger = logging.getLogger(__name__)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(log_formatter)
logger.addHandler(ch)
logger.setLevel(logging.INFO)

from .factory import IndividualCatalogCreatorFactory, CatalogCreatorFactory


class ErddapCatalogManager:
    def __init__(self, data_root: str, catalog_root: str, config: dict):
        """
        Initializes the ErddapCatalogManager with the provided data root,
        catalog root, and configuration.

        :param data_root: Root directory for the dataset files.
        :param catalog_root: Root directory for the ERDDAP catalog files.
        :param config: Configuration dictionary for catalog generation.
        """
        self.data_root = data_root
        self.erddap_catalog_root = catalog_root
        self.config = config

    def run(self):
        """
        Generates or updates individual dataset catalogs and the entire ERDDAP catalog.
        """
        try:
            logger.info("Starting ERDDAP catalog generation.")

            # Create individual catalogs
            # generate dataset xml for each individual datasets
            # todo: make sure i get good
            individual_creators = IndividualCatalogCreatorFactory(self.data_root, self.config).generate()
            for creator in individual_creators:
                try:
                    logger.info("Processing deployment: %s", creator.deployment_dict)
                    creator.create()
                except Exception as e:
                    logger.error("Failed to create catalog for deployment %s: %s",
                                 creator.deployment_dict, str(e), exc_info=True)

            # Create the complete ERDDAP catalog
            logger.info("Generating the complete ERDDAP catalog.")
            erddap_catalog_creator = CatalogCreatorFactory(self.data_root, self.erddap_catalog_root).generate()
            erddap_catalog_creator.create()

            logger.info("ERDDAP catalog generation completed successfully.")
        except Exception as e:
            logger.error("Error during ERDDAP catalog generation: %s", str(e), exc_info=True)


