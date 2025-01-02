import unittest

from erddap_section.erddap_support.individual_erddap_dataset_catalog_creator.archive.factory import IndividualCatalogCreatorFactory


config = {
    "GENERATE_DATASETS_XML_PROGRAM_PATH": "/Users/xiangling/resource/cgdac/GenerateDatasetsXml/webapps/erddap/WEB-INF/GenerateDatasetsXml.sh",
    "XML_TEMP_FOLDER": "/Users/xiangling/resource/cgdac/xml_temp"
}

deployment_dict_example = [
    {
        "dataset_chunk_path": "/Users/xiangling/code/glider_dac/erddap_section/erddap_support/tests/output",
        "username": "example_name_of_user",
        "activate": True,
        "name": "test_dataset",
        "deployment_date": "20241012",
        "checksum": "asdasdasd",
        "completed": "true",
        "delayed_mode": "delayed",
        "selected_file": "path",
        "glider_name": "name_of_glider",
        "wmo_id": "1231",
        "deployment_dir": "/Users/xiangling/code/glider_dac/erddap_section/erddap_support/tests/resource/test_deployment"
    }
]


class TestIndividualCatalogCreatorFactory(unittest.TestCase):
 # Replace with the actual import path for Deployment
    def test_individual_catalog_creator_factory(self):
        res = IndividualCatalogCreatorFactory("/Users/xiangling/code/glider_dac/erddap_section/erddap_support/tests/resource", config, deployment_dict_example).generate()
        for r in res:
            r.create()

