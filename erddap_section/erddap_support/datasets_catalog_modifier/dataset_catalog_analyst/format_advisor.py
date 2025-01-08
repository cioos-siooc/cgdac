from typing import List, Optional

from .dataset_xml_container import DatasetXmlContainer
from .erddap_dataset_name_constants import ErddapSections, ActionDictConstants, CdmVariablesConstants
from .dataset_modify_actions import ActionDict, get_new_action_dict
from .erddap_dataset_name_constants import ActionListActionsConstants, DESTINATION_NAME, DATA_TYPE, ADD_ATTRIBUTES, \
    PLACE_HOLDER_STR


class BaseFormatAdvisor:
    SECTION = None

    def __init__(self, dataset_xml_container: DatasetXmlContainer, deployment_dict, dataset_dict):
        self.dataset_xml_container = dataset_xml_container
        self.deployment_dict = deployment_dict
        self.dataset_dict = dataset_dict

    def analyse(self, review_value) -> Optional[List[ActionDict]]:
        return None

    def suggest(self, feedback=None):
        suggestion = self.analyse(feedback)
        if suggestion is None:
            return feedback
        else:
            return suggestion

    def need_suggestion(self):
        ...

    def can_be_fixed(self):
        return True

    def create_action_dict(self, data_file, section, expected_value, actual_value) -> ActionDict:
        action_dict = get_new_action_dict()
        action_dict[ActionDictConstants.DATA_FIELD_NAME] = data_file
        action_dict[ActionDictConstants.SECTION] = section
        action_dict[ActionDictConstants.EXPECTED_VALUE] = expected_value
        action_dict[ActionDictConstants.ACTUAL_VALUE] = actual_value
        return action_dict


class HeaderFormatAdvisor(BaseFormatAdvisor):
    SECTION = ErddapSections.DATASET_HEADER


class ConfigFormatAdvisor(BaseFormatAdvisor):
    SECTION = ErddapSections.DATASET_CONFIG


class BaseGlobalFormatAdvisor(BaseFormatAdvisor):
    SECTION = ErddapSections.DATASET_GLOBAL

    def add_or_edit_global_action_dict(self, data_field_name, expected_value) -> ActionDict:
        return self.create_action_dict(data_field_name, ErddapSections.DATASET_GLOBAL, expected_value, None)


class BaseDataVariableFormatAdvisor(BaseFormatAdvisor):
    SECTION = ErddapSections.DATASET_VARIABLE

    def add_or_edit_variable_attribute(self, data_variable_name, expected_att_name, expected_att_value) -> ActionDict:
        expected_value = {
            ADD_ATTRIBUTES: [{
                "name": expected_att_name,
                "value": expected_att_value
            }]
        }
        actual_value = {
            ADD_ATTRIBUTES: None
        }

        return self.create_action_dict(data_variable_name, ErddapSections.DATASET_VARIABLE, expected_value,
                                       actual_value)

    def remove_data_variable_attribute(self, data_variable_name, remove_attribute_name, remove_attribute_value):
        expected_value = {
            ADD_ATTRIBUTES: None
        }
        actual_value = {
            ADD_ATTRIBUTES: [{
                "name": remove_attribute_name,
                "value": remove_attribute_value
            }]
        }
        return self.create_action_dict(data_variable_name, ErddapSections.DATASET_VARIABLE, expected_value,
                                       actual_value)

    def add_or_edit_data_variable(self, source_name, destination_name, data_type, add_attributes_dict):
        expected_value = {
            "sourceName": source_name,
            "destinationName": destination_name,
            "dataType": data_type,
            ADD_ATTRIBUTES: add_attributes_dict
        }
        actual_value = None

        return self.create_action_dict(source_name, ErddapSections.DATASET_VARIABLE, expected_value,
                                       actual_value)


class TrajectoryVariableAdvisor(BaseDataVariableFormatAdvisor):
    def analyse(self, review_value) -> Optional[List[ActionDict]]:
        action_dict_list = []
        if len(review_value["variable_list"]) == 0:
            action_dict_list.extend(self.add_trajectory())
        return action_dict_list

    def add_trajectory(self) -> list:
        add_attributes_dict = [{"name": "cf_role", "value": CdmVariablesConstants.TRAJECTORY_ID}]
        add_trajectory_action = self.add_or_edit_data_variable(CdmVariablesConstants.TRAJECTORY.lower(),
                                                               CdmVariablesConstants.TRAJECTORY.lower(), "string",
                                                               add_attributes_dict)
        return [add_trajectory_action]


class CFRoleAdvisor(BaseDataVariableFormatAdvisor):
    def analyse(self, cf_role_variable_list) -> Optional[List[ActionDict]]:
        action_dict_list = []
        if len(cf_role_variable_list["variable_list"]) == 0:
            action_dict_list.extend(self.add_cf_variable())
        elif len(cf_role_variable_list["variable_list"]) == 1:
            v = cf_role_variable_list["variable_list"][0]
            cf_role_value = v["addAttributes"]["cf_role"]
            if not (v["sourceName"] == CdmVariablesConstants.TRAJECTORY.lower() and cf_role_value["text"] == "trajectory_id"):
                action_dict_list.extend(self.remove_cf_variable(cf_role_variable_list["variable_list"]))
                action_dict_list.extend(self.add_cf_variable())
        elif len(cf_role_variable_list["variable_list"]) > 1:
            action_dict_list.extend(self.remove_cf_variable(cf_role_variable_list["variable_list"]))
            action_dict_list.extend(self.add_cf_variable())
        return action_dict_list

    def add_cf_variable(self) -> Optional[List[ActionDict]]:
        remove_action = self.add_or_edit_variable_attribute(CdmVariablesConstants.TRAJECTORY.upper(), "cf_role", "trajectory_id")
        return [remove_action]

    def remove_cf_variable(self, cf_role_variable_list) -> Optional[List[ActionDict]]:
        remove_action_list = []
        for key, v in enumerate(cf_role_variable_list):
            name = v["sourceName"]
            data_variable_attributes_name = 'cf_role'
            data_variable_attributes_value = v[ADD_ATTRIBUTES][data_variable_attributes_name]['text']
            remove_action_list.append(
                self.remove_data_variable_attribute(name, 'cf_role', data_variable_attributes_value))
        return remove_action_list


class TrajectoryCDMTrajectoryVariableAdvisor(BaseGlobalFormatAdvisor):
    """
    This advisor has pre-requirement, it needs trajectory variable available.
    """

    def analyse(self, value) -> Optional[List[ActionDict]]:
        action_dict_list = []
        if "cdm_data_type" not in value or value["cdm_data_type"] != "Trajectory":
            action_dict_list.extend(self.fix_cdm_data_type())
        if "cdm_trajectory_variables" not in value or not value["cdm_trajectory_variables"] or "TRAJECTORY" not in \
                value["cdm_trajectory_variables"]:
            action_dict_list.extend(self.fix_cdm_trajectory_variables())
        return action_dict_list

    def fix_cdm_data_type(self) -> List[ActionDict]:
        action_dict = self.add_or_edit_global_action_dict("cdm_data_type", "Trajectory")
        return [action_dict]

    def fix_cdm_trajectory_variables(self) -> List[ActionDict]:
        action_dict = self.add_or_edit_global_action_dict("cdm_trajectory_variables", "TRAJECTORY")
        return [action_dict]


class MetadataConventionAdvisor(BaseGlobalFormatAdvisor):
    def analyse(self, value) -> Optional[List[ActionDict]]:
        action_dict = []
        if "Conventions" not in value or value["Conventions"] != 'CF-1.6, ACDD-1.3':
            action_dict.extend(self.fix_metadata_conventions())
        return action_dict

    def fix_metadata_conventions(self) -> List[ActionDict]:
        action_dict = self.add_or_edit_global_action_dict("Conventions", 'CF-1.6, ACDD-1.3')
        return [action_dict]
