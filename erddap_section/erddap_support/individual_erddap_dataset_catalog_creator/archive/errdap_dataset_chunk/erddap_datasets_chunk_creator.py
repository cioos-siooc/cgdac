import os.path
import logging
from .templates import check_dataset_yml_config_files
from .factory.draft_erddap_xml_creation import DraftDatasetXmlCreatorFactory
from .factory.errdap_catalog_chunk_enhancer_factory import ErddapConfigAdjustFactory
from erddap_catalog_chunk_editor import dataset_xml_parser


class ErddapCatalogChunkCreator:
    """
    Erddap Catalog Chunk would create dataset.xml chunk for the nc file
    """

    def __init__(self, deployment_dict, chosen_nc_file, dataset_id, config):
        """
        chosen_nc_file: it is the nc file that provide the nc files
        """
        self.deployment_dict = deployment_dict

        self.deployment_folder = deployment_dict["deployment_dir"]
        self.data_folder = deployment_dict["deployment_dir"]
        self.selected_nc_file = chosen_nc_file
        self.dataset_id = dataset_id
        self.config = config
        self.data_template_folder = os.path.join(self.deployment_folder, "yml_config")

    def init_template(self):
        try:
            check_dataset_yml_config_files(self.data_template_folder)
        except Exception as e:
            logging.error("Error when init template file for the dataset")

    def create_raw_dataset_xml_handler(self):
        # generate the draft xml by using GenerateDatasetsXml program on local or remote server
        return DraftDatasetXmlCreatorFactory(self.selected_nc_file, self.data_folder, dict()).run()

    def get_metadata_improve_suggestion_dict(self):
        return dict()

    def create(self):
        if  self.selected_nc_file:
            self.init_template()
            # generate the draft xml by using GenerateDatasetsXml program on local or remote server
            raw_dataset_xml_handler_builder = DraftDatasetXmlCreatorFactory(self.selected_nc_file, self.data_folder,
                                                                            self.config).run()

            erddap_config_xml_adjuster_builder = ErddapConfigAdjustFactory(self.selected_nc_file, self.deployment_dict,
                                                                           self.dataset_id, self.deployment_folder)
            draft_xml_path = raw_dataset_xml_handler_builder.generate()
            draft_xml_str = dataset_xml_parser(draft_xml_path)
            adjuster = erddap_config_xml_adjuster_builder.build(draft_xml_str)
            adjuster.adjust()
            erddap_config_path = adjuster.output_path
            return erddap_config_path
