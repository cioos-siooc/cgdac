from datasets_catalog_modifier import DatasetCatalogModifyManagerGenerator
from individual_erddap_dataset_catalog_creator import IndividualErddapDatasetCatalogHandler


class ErddapCatalogDirector:
    def __init__(self, config, deployment_dict, erddap_dict, dataset_dict):
        self.nc_path = None
        self.config = config
        self.deployment_dict = deployment_dict
        self.erddap_dict = erddap_dict
        self.dataset_dict = dataset_dict

    def generate_individual_dataset_catalog(self):
        draft_dataset_path = IndividualErddapDatasetCatalogHandler(self.config, self.deployment_dict,
                                                                   self.erddap_dict,
                                                                   self.dataset_dict).generate_draft_dataset_xml()
        return draft_dataset_path

    def get_dataset_xml_output_path(self):
        return ""

    def generate_dataset_catalog(self):
        draft_dataset_path = self.generate_individual_dataset_catalog()
        catalog_manager = DatasetCatalogModifyManagerGenerator(draft_dataset_path, self.get_dataset_xml_output_path(),
                                                               self.config, self.deployment_dict, self.dataset_dict).generate()
        catalog_manager.generate_dataset_catalog()
