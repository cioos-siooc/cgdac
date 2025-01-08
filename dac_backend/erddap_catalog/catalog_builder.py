from glider_dac.app import app
from erddap_section import BasicCatalogBuilder


def create_catalog_builder():
    builder = BasicCatalogBuilder(app.config["INDIVIDUAL_DATASET_FOLDER"], app.config["ERDDAP_DATASETS_XML"])
    return builder
