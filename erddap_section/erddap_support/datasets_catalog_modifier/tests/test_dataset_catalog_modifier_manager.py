import os
import unittest
from common import clean_folder
from ..dataset_catalog_modifier_manager import DatasetCatalogModifyManagerGenerator


class TestDatasetCatalogManagerGenerator(unittest.TestCase):

    def setUp(self):
        self.current_folder_path = os.path.dirname(os.path.abspath(__file__))
        self.resource_path = os.path.join(self.current_folder_path, 'resource')
        self.output_path = os.path.join(self.current_folder_path, 'output')
        self.output_path_xml_path = os.path.join(self.output_path, 'output_xml.xml')
        self.dataset_draft_path = os.path.join(self.resource_path, 'dataset_draft.xml')
        self.config = {}
        self.deployment_dict = {}
        self.dataset_dict = {}

    def tearDown(self):
        ...

    def test_manager_generation(self):
        try:
            dataset_catalog_manager = DatasetCatalogModifyManagerGenerator(self.dataset_draft_path,
                                                                           self.output_path_xml_path,
                                                                           self.config, self.deployment_dict,
                                                                           self.dataset_dict).generate()
            print(dataset_catalog_manager)
        except Exception as error:
            self.fail(error)


class TestDatasetCatalogManager(unittest.TestCase):
    def setUp(self):
        self.current_folder_path = os.path.dirname(os.path.abspath(__file__))
        self.resource_path = os.path.join(self.current_folder_path, 'resource')
        self.output_path = os.path.join(self.current_folder_path, 'output')
        self.output_path_xml_path = os.path.join(self.output_path, 'output_xml.xml')
        self.dataset_draft_path = os.path.join(self.resource_path, 'dataset_draft.xml')
        self.config = {}
        self.deployment_dict = {}
        self.dataset_dict = {
            "datasetID": "dataset_id"
        }

    def tearDown(self):
        clean_folder(self.output_path)


    def check_line_exist_before_and_after(self, exam_str):
        count = 0
        # Make sure the ID Doesn't exist in the dataset xml before modification
        with open(self.dataset_draft_path, "r", encoding="utf-8") as file:
            xml_content = file.readlines()
            for line in xml_content:
                if exam_str in line:
                    count += 1
        self.assertEqual(count, 0)

        # Make sure the ID added to the file
        with open(self.output_path_xml_path, "r", encoding="utf-8") as file:
            xml_content = file.readlines()
            for line in xml_content:
                if exam_str in line:
                    break
            else:
                self.fail()

    def test_manager_modify_dataset_header(self):
        config = {}
        deployment_dict = {}
        dataset_dict = {
            "datasetID": "expected_dataset_id",
        }
        dataset_catalog_manager = DatasetCatalogModifyManagerGenerator(self.dataset_draft_path,
                                                                       self.output_path_xml_path,
                                                                       config, deployment_dict,
                                                                       dataset_dict).generate()
        dataset_catalog_manager.modify()
        self.check_line_exist_before_and_after( "datasetID=\"expected_dataset_id\"")

    def test_manager_default_modifies(self):
        config = {}
        deployment_dict = {}
        dataset_dict = {
            "datasetID": "expected_dataset_id",
        }
        dataset_catalog_manager = DatasetCatalogModifyManagerGenerator(self.dataset_draft_path,
                                                                       self.output_path_xml_path,
                                                                       config, deployment_dict,
                                                                       dataset_dict).generate()
        dataset_catalog_manager.modify()
        self.check_line_exist_before_and_after("<att name=\"cdm_trajectory_variables\">TRAJECTORY</att>")
        self.check_line_exist_before_and_after("<att name=\"Conventions\">CF-1.6, ACDD-1.3</att>")
        self.check_line_exist_before_and_after("<sourceName>trajectory</sourceName>")



