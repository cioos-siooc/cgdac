from .dataset_xml_container import DatasetXmlContainer
from .erddap_dataset_name_constants import ActionDictConstants
from .rules import HeaderMappingList, ConfigMappingList
from .erddap_dataset_name_constants import (DATASET_HEADER,
                                            DATASET_CONFIG,
                                            DATASET_VARIABLE,
                                            DATASET_GLOBAL,
                                            DATASET_ID,
                                            DATASET_CONFIG_UPDATE_EVERY_N_MILLIS,
                                            DATASET_CONFIG_FILE_NAME_REGEX,
                                            DATASET_CONFIG_FILE_DIR,
                                            CF_DEFAULT_DATASET_DICT,
                                            CONVENTIONS,
                                            CdmVariablesConstants,
                                            ErddapSections)


class FormatErrors(Exception):
    pass


class CFVariableError(FormatErrors):
    def __init__(self, num):
        super().__init__(num)


class CFCdnDataTypeError(FormatErrors):
    ...


class BaseReviewer:
    SECTION = None

    def __init__(self, dataset_xml_container: DatasetXmlContainer):
        self.data_container = dataset_xml_container

    def review(self):
        raise NotImplementedError


class BaseStaticValueReviewer(BaseReviewer):
    MAPPING_LIST = None

    def __init__(self, dataset_xml_container: DatasetXmlContainer, deployment_dict, dataset_dict):
        super().__init__(dataset_xml_container)
        self.deployment_dict = deployment_dict
        self.dataset_dict = dataset_dict

    def _review(self):
        feedback_list = []
        for key, value in self.MAPPING_LIST.items():
            expect_value_source = getattr(self, value[ActionDictConstants.DATASET][ActionDictConstants.DATA_SOURCE])
            expect_value = expect_value_source.get(value[ActionDictConstants.DATASET][ActionDictConstants.DATA_ID])

            dataset_value_source = getattr(self.data_container,
                                           value[ActionDictConstants.DATA_CONTAINER][ActionDictConstants.DATA_SOURCE])
            dataset_value = dataset_value_source.get(
                value[ActionDictConstants.DATA_CONTAINER][ActionDictConstants.DATA_ID], None)
            if expect_value != dataset_value:
                feedback_list.append({
                    ActionDictConstants.DATA_FIELD_NAME: key,
                    ActionDictConstants.SECTION: value[ActionDictConstants.DATA_CONTAINER][
                        ActionDictConstants.DATA_SOURCE],
                    ActionDictConstants.EXPECTED_VALUE: expect_value,
                    ActionDictConstants.ACTUAL_VALUE: dataset_value
                })
        return feedback_list

    def review(self):
        return self._review()


class HeaderReviewer(BaseStaticValueReviewer):
    MAPPING_LIST = HeaderMappingList.BASE_COMPARING_MAPPING_LIST


class DatasetConfigReviewer(BaseStaticValueReviewer):
    MAPPING_LIST = ConfigMappingList.BASE_COMPARING_MAPPING_LIST


class BaseDynamicValueReviewer(BaseReviewer):

    def review(self):
        value = self._review()
        return value

    def _review(self):
        """
        return value in dictionary format, which are the data relevant to a specific dataset format requirement
        that we want to look into it. the result will be used for analyse and provide suggestion later
        """
        raise NotImplementedError



class TrajectoryVariableReviewer(BaseDynamicValueReviewer):
    SECTION = ErddapSections.DATASET_VARIABLE

    def _review(self):
        data_variable = self.data_container.data_variable_list
        result = {
            "variable_list": [],
        }
        for value in data_variable:
            if value["sourceName"].lower() == "trajectory":
                result["variable_list"].append(value)
        return result


class TrajectoryCFRoleVariableReviewer(BaseDynamicValueReviewer):
    SECTION = ErddapSections.DATASET_VARIABLE

    """
    requirement:
    The "Conventions" global attribute should include "CF-1.6" and "ACDD-1.3"
    To uniquely identify the trajectories, a variable must have the attribute "cf_role=trajectory_id".
    ERDDAP automatically generates the "featureType" attribute, so you don't need to add it manually.
    Include the "cdm_trajectory_variables" global attribute, listing variables that contain information
    about each trajectory, such as ship_id, ship_type, and ship_owner.
    This list MUST include the cf_role=trajectory_id variable.
    """

    def _review(self):
        data_variable = self.data_container.data_variable_list
        cf_role_variable_list = {
            "variable_list": [],
        }
        for value in data_variable:
            addAttributes = value["addAttributes"]
            if "cf_role" in addAttributes:
                cf_role_variable_list["variable_list"].append(value)

        return cf_role_variable_list


class TrajectoryCdmTrajectoryVariableReviewer(BaseDynamicValueReviewer):
    """
    Include the "cdm_trajectory_variables" global attribute, listing variables that contain information
    about each trajectory, such as ship_id, ship_type, and ship_owner.
    """
    SECTION = ErddapSections.DATASET_GLOBAL

    def _review(self):
        dataset_global = self.data_container.dataset_global

        variable_dict = {}
        variable_dict["cdm_data_type"] = dataset_global.get("cdm_data_type")
        variable_dict["cdm_trajectory_variables"] = dataset_global.get("cdm_trajectory_variables")
        return variable_dict
    #
    # def _analyse(self, value):
    #     errors = []
    #     if value["cdm_data_type"] != "Trajectory":
    #         errors.append(CFCdnDataTypeError())
    #     if not value["cdm_trajectory_variables"] or "Trajectory" not in value["cdm_trajectory_variables"]:
    #         errors.append(CFCdnDataTypeError())
    #     return errors

class MetadataConventionReviewer(BaseDynamicValueReviewer):
    SECTION = ErddapSections.DATASET_GLOBAL

    def _review(self):
        dataset_global = self.data_container.dataset_global

        variable_dict = {}
        variable_dict["Conventions"] = dataset_global.get("Conventions")
        return variable_dict