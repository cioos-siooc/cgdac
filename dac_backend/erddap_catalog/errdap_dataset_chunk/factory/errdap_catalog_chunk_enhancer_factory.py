import os
from .nc_reader import NetCDFMetaReader
from ..erddap_dataset_xml_adjuster import OceanGliderStandardDatasetXmlAdjuster
from .meta_dict_enhancer import NetCDFMetaFactory


class ErddapConfigAdjustFactory:
    """
    Prepare and create the ErddapGliderDatasetXmlRefiner which can modify the draft dataset XML
    """

    def __init__(self, nc_path, deployment_dict, dataset_id, output_path):
        self.deployment_dict = deployment_dict
        deployment_folder = deployment_dict["deployment_dir"]
        self.nc_path = nc_path
        self.deployment_folder = deployment_folder
        self.dataset_id = dataset_id
        self.output_path = output_path
        self._globaL_attrs = None
        self._erddap_variables = None

    def get_global_attrs(self):
        if self._globaL_attrs is None:
            nc_reader = NetCDFMetaReader(self.nc_path)
            self._globaL_attrs = nc_reader.global_attrs
            self._erddap_variables = nc_reader.variable_attrs
        return self._globaL_attrs

    def get_erddap_catalog_chunk_output_path(self):
        dir_path = self.output_path
        return dir_path

    def get_dataset_templates(self):
        return dict()

    # Isolate Django setting in a function which could help with the unit testing
    def get_nc_folder_name(self, file_type):
        return ""

    def get_erddap_server_nc_folder_path(self):
        # generate the path for nc file folder on ERDDAP server
        return self.nc_path

    def get_output_path(self):
        refined_out_xml_name = 'dataset.xml'
        return os.path.join(self.get_erddap_catalog_chunk_output_path(), refined_out_xml_name)

    def get_deployment_templates_folder(self):
        return self.deployment_folder

    def get_variables(self):
        if self._erddap_variables is None:
            nc_reader = NetCDFMetaReader(self.nc_path)
            self._globaL_attrs = nc_reader.global_attrs
            self._erddap_variables = nc_reader.variable_attrs
        return  self._erddap_variables

    def build(self, xml_str):
        erddap_meta = NetCDFMetaFactory(self.get_global_attrs(), self.get_deployment_templates_folder(), self.get_variables()).generate()
        return OceanGliderStandardDatasetXmlAdjuster(xml_str, self.dataset_id, self.get_erddap_server_nc_folder_path(),
                                                     erddap_meta,
                                                     self.get_output_path(), self.deployment_dict)
