import os
import unittest
from ..dataset_xml_container import DatasetCatalogHeader, DatasetConfig
from ..dataset_catalog_analyst import DatasetDataVariableAnalyst
from ..dataset_xml_container_generator import DatasetXmlContainerGenerator
from ..dataset_update_handler import DatasetXmlModifierHandler
from ..format_reviewer import TrajectoryCFRoleVariableReviewer, TrajectoryVariableReviewer, TrajectoryCdmTrajectoryVariableReviewer, MetadataConventionReviewer
from ..format_advisor import CFRoleAdvisor, TrajectoryVariableAdvisor, TrajectoryCDMTrajectoryVariableAdvisor, MetadataConventionAdvisor
from common import clean_folder
from erddap_section.erddap_support.datasets_catalog_modifier.errdap_dataset_configuration_helper import \
    ERDDAPDatasetXMLEditor, read_xml_as_string


class IntegrationTest(unittest.TestCase):
    def setUp(self):
        self.current_folder_path = os.path.dirname(os.path.abspath(__file__))
        self.resource_path = os.path.join(self.current_folder_path, 'resource')
        self.output_path = os.path.join(self.current_folder_path, 'output')
        self.output_path_xml_path = os.path.join(self.output_path, 'output_xml.xml')
        self.dataset_draft_path = os.path.join(self.resource_path, 'dataset_draft.xml')
        self.dataset_dict = {
            "dataset_id": "expect_dataset_id",
        }
        self.deployment_dict = {}

        self.dataset_header: DatasetCatalogHeader = {
            "type": "example_type",
            "datasetID": "expect_dataset_id",
            "active": True
        }
        self.dataset_config: DatasetConfig = {
            "accessibleViaFiles": True,
            "reloadEveryNMinutes": "123",
            "updateEveryNMillis": "123",
            "fileDir": "123",
            "fileNameRegex": "qwe",
            "recursive": "example",
            "pathRegex": "example",
            "metadataFrom": "example",
            "standardizeWhat": "example",
            "sortedColumnSourceName": "example",
            "sortFilesBySourceNames": "example",
            "fileTableInMemory": "example",
        }

    def tearDown(self):
        clean_folder(self.output_path)

    def setup_resource_xml1(self):
        draft_xml_str = read_xml_as_string(self.dataset_draft_path)
        editor = ERDDAPDatasetXMLEditor(draft_xml_str)
        return editor

    def test_modify_dataset_cf_role_data_variable_with_multiple_cf_role(self):
        dataset_draft_path = os.path.join(self.output_path, "dataset_draft_with_trajectory_with_multiple_cf_roles.xml")
        test_xml_editor = self.setup_resource_xml1()
        test_xml_editor.set_data_variable_add_attribute("time", "cf_role", "trajectory_id")
        test_xml_editor.set_data_variable_add_attribute("lat", "cf_role", "trajectory_id")
        test_xml_editor.set_data_variable_add_attribute("lon", "cf_role", "trajectory_id")
        test_xml_editor.write(dataset_draft_path)

        counter = 0
        with open(dataset_draft_path, "r", encoding="utf-8") as file:
            xml_content = file.readlines()
            for line in xml_content:
                if "cf_role" in line:
                    counter += 1
        self.assertEqual(counter, 3)

        data_container = DatasetXmlContainerGenerator(dataset_draft_path).generate()
        reviewer = TrajectoryCFRoleVariableReviewer(data_container)
        advisor = CFRoleAdvisor(data_container, self.deployment_dict, self.dataset_header)
        data_variable_analyst = DatasetDataVariableAnalyst(data_container, self.deployment_dict, self.dataset_dict)
        data_variable_analyst.add_reviewer_and_advisor(reviewer, advisor)
        action_list = data_variable_analyst.analyse()
        data_container.action_list.set_action(action_list)
        data_update_handler = DatasetXmlModifierHandler(data_container, self.output_path_xml_path)
        data_update_handler.update_dataset()
        data_update_handler.write()

        counter = 0
        with open(self.output_path_xml_path, "r", encoding="utf-8") as file:
            xml_content = file.readlines()
            for line in xml_content:
                if "cf_role" in line:
                    counter += 1
        self.assertEqual(counter, 1)

    def test_modify_dataset_cf_role_data_variable_with_multiple_cf_role(self):

        dataset_draft_path = os.path.join(self.resource_path,
                                          "dataset_draft_with_trajectory_with_multiple_cf_roles.xml")
        data_container = DatasetXmlContainerGenerator(dataset_draft_path).generate()
        reviewer = TrajectoryCFRoleVariableReviewer(data_container)
        advisor = CFRoleAdvisor(data_container, self.deployment_dict, self.dataset_header)
        data_variable_analyst = DatasetDataVariableAnalyst(data_container, self.deployment_dict, self.dataset_dict)
        data_variable_analyst.add_reviewer_and_advisor(reviewer, advisor)
        action_list = data_variable_analyst.analyse()
        data_container.action_list.set_action(action_list)
        data_update_handler = DatasetXmlModifierHandler(data_container, self.output_path_xml_path)
        data_update_handler.update_dataset()
        data_update_handler.write()

        counter = 0
        with open(self.output_path_xml_path, "r", encoding="utf-8") as file:
            xml_content = file.readlines()
            for line in xml_content:
                if "cf_role" in line:
                    counter += 1
        self.assertEqual(counter, 1)

    def test_modify_dataset_cf_role_data_variable_with_multiple_cf_role_with_incorrect_value(self):
        dataset_draft_path = os.path.join(self.resource_path,
                                          "dataset_draft_with_trajectory_with_multiple_cf_roles_with_incorrect_value.xml")
        data_container = DatasetXmlContainerGenerator(dataset_draft_path).generate()
        reviewer = TrajectoryCFRoleVariableReviewer(data_container)
        advisor = CFRoleAdvisor(data_container, self.deployment_dict, self.dataset_header)
        data_variable_analyst = DatasetDataVariableAnalyst(data_container, self.deployment_dict, self.dataset_dict)
        data_variable_analyst.add_reviewer_and_advisor(reviewer, advisor)
        action_list = data_variable_analyst.analyse()
        data_container.action_list.set_action(action_list)
        data_update_handler = DatasetXmlModifierHandler(data_container, self.output_path_xml_path)
        data_update_handler.update_dataset()
        data_update_handler.write()

        counter = 0
        with open(self.output_path_xml_path, "r", encoding="utf-8") as file:
            xml_content = file.readlines()
            for line in xml_content:
                if "cf_role" in line:
                    counter += 1
        self.assertEqual(counter, 1)

    def test_modify_dataset_cf_role_data_variable_with_no_cf_role_variable(self):
        dataset_draft_path = os.path.join(self.output_path, "dataset_draft_with_trajectory.xml")

        test_xml_editor = self.setup_resource_xml1()
        test_xml_editor.add_data_variable("TRAJECTORY", "TRAJECTORY", "string",
                                          [{"name": "value_name", "value": "value_value"}])
        test_xml_editor.write(dataset_draft_path)

        counter = 0
        with open(dataset_draft_path, "r", encoding="utf-8") as file:
            xml_content = file.readlines()
            for line in xml_content:
                if "cf_role" in line:
                    counter += 1
        self.assertEqual(counter, 0)

        data_container = DatasetXmlContainerGenerator(dataset_draft_path).generate()
        reviewer = TrajectoryCFRoleVariableReviewer(data_container)
        advisor = CFRoleAdvisor(data_container, self.deployment_dict, self.dataset_header)
        data_variable_analyst = DatasetDataVariableAnalyst(data_container, self.deployment_dict, self.dataset_dict)
        data_variable_analyst.add_reviewer_and_advisor(reviewer, advisor)
        action_list = data_variable_analyst.analyse()
        data_container.action_list.set_action(action_list)
        data_update_handler = DatasetXmlModifierHandler(data_container, self.output_path_xml_path)
        data_update_handler.update_dataset()
        data_update_handler.write()

        with open(self.output_path_xml_path, "r", encoding="utf-8") as file:
            xml_content = file.readlines()
            for line in xml_content:
                if "cf_role" in line:
                    break
            else:
                self.fail()

    def test_modify_dataset_cf_role_data_variable_with_no_cf_role_variable_with_no_trajectory_variable(self):
        dataset_draft_path = os.path.join(self.resource_path, "dataset_draft.xml")
        container_generator =  DatasetXmlContainerGenerator(dataset_draft_path)
        data_container =container_generator.generate()
        trajectory_reviewer = TrajectoryVariableReviewer(data_container)
        trajectory_advisor = TrajectoryVariableAdvisor(data_container, self.deployment_dict, self.dataset_header)
        cf_role_reviewer = TrajectoryCFRoleVariableReviewer(data_container)
        cf_role_advisor = CFRoleAdvisor(data_container, self.deployment_dict, self.dataset_header)
        data_variable_analyst = DatasetDataVariableAnalyst(data_container, self.deployment_dict, self.dataset_dict)
        data_variable_analyst.add_reviewer_and_advisor(trajectory_reviewer, trajectory_advisor)
        data_variable_analyst.add_reviewer_and_advisor(cf_role_reviewer, cf_role_advisor)
        data_update_handler = DatasetXmlModifierHandler(data_container, self.output_path_xml_path)
        for action_list in data_variable_analyst.analyse_generator():
            data_container.action_list.set_action(action_list)
            data_update_handler.update_dataset()
        data_update_handler.write()

        counter = 0
        with open(self.output_path_xml_path, "r", encoding="utf-8") as file:
            xml_content = file.readlines()
            for line in xml_content:
                if "<sourceName>trajectory</sourceName>" in line:
                    counter += 1
        self.assertEqual(counter, 1)
        with open(self.output_path_xml_path, "r", encoding="utf-8") as file:
            xml_content = file.readlines()
            for line in xml_content:
                if "cf_role" in line:
                    break
            else:
                self.fail()

        self.assertEqual(len(data_container.action_list.action_archive), 1)

    def test_add_trajectory_cf_role_and_cdm_variable(self):
        dataset_draft_path = os.path.join(self.resource_path, "dataset_draft2.xml")
        container_generator = DatasetXmlContainerGenerator(dataset_draft_path)
        data_container = container_generator.generate()
        trajectory_reviewer = TrajectoryVariableReviewer(data_container)
        trajectory_advisor = TrajectoryVariableAdvisor(data_container, self.deployment_dict, self.dataset_header)
        cdm_variable_reviewer = TrajectoryCdmTrajectoryVariableReviewer(data_container)
        cdm_variable_advisor = TrajectoryCDMTrajectoryVariableAdvisor(data_container, self.deployment_dict, self.dataset_header)
        cf_role_reviewer = TrajectoryCFRoleVariableReviewer(data_container)
        cf_role_advisor = CFRoleAdvisor(data_container, self.deployment_dict, self.dataset_header)
        meta_convention_reviewer = MetadataConventionReviewer(data_container)
        meta_convention_advisor = MetadataConventionAdvisor(data_container, self.deployment_dict, self.dataset_header)
        data_variable_analyst = DatasetDataVariableAnalyst(data_container, self.deployment_dict, self.dataset_dict)
        data_variable_analyst.add_reviewer_and_advisor(trajectory_reviewer, trajectory_advisor)
        data_variable_analyst.add_reviewer_and_advisor(cdm_variable_reviewer, cdm_variable_advisor)
        data_variable_analyst.add_reviewer_and_advisor(cf_role_reviewer, cf_role_advisor)
        data_variable_analyst.add_reviewer_and_advisor(meta_convention_reviewer, meta_convention_advisor)
        data_update_handler = DatasetXmlModifierHandler(data_container, self.output_path_xml_path)
        for action_list in data_variable_analyst.analyse_generator():
            data_container.action_list.set_action(action_list)
            data_update_handler.update_dataset()
        data_update_handler.write()

        counter = 0
        with open(self.output_path_xml_path, "r", encoding="utf-8") as file:
            xml_content = file.readlines()
            for line in xml_content:
                if "<sourceName>trajectory</sourceName>" in line:
                    counter += 1
        self.assertEqual(counter, 1)
        with open(self.output_path_xml_path, "r", encoding="utf-8") as file:
            xml_content = file.readlines()
            for line in xml_content:
                if "cf_role" in line:
                    break
            else:
                self.fail()

        with open(self.output_path_xml_path, "r", encoding="utf-8") as file:
            xml_content = file.readlines()
            for line in xml_content:
                if "CF-1.6" in line:
                    break
            else:
                self.fail()

        self.assertEqual(len(data_container.action_list.action_archive), 4)
