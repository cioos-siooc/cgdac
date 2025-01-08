from .dataset_xml_container import DatasetXmlContainer
from .format_reviewer import HeaderReviewer, DatasetConfigReviewer, TrajectoryVariableReviewer, \
    TrajectoryCFRoleVariableReviewer, TrajectoryCdmTrajectoryVariableReviewer, MetadataConventionReviewer
from .format_advisor import HeaderFormatAdvisor, ConfigFormatAdvisor, TrajectoryVariableAdvisor, CFRoleAdvisor, \
    TrajectoryCDMTrajectoryVariableAdvisor, MetadataConventionAdvisor
from .dataset_catalog_analyst import DatasetHeaderAnalyst, DatasetConfigAnalyst


class HeaderAnalystFactory:
    def __init__(self, dataset_xml_container: DatasetXmlContainer, deployment_dict, dataset_dict):
        self.dataset_xml_container = dataset_xml_container
        self.deployment_dict = deployment_dict
        self.dataset_dict = dataset_dict

    def generate(self):
        header_advisor = HeaderFormatAdvisor(self.dataset_xml_container, self.deployment_dict, self.dataset_dict)
        header_reviewer = HeaderReviewer(self.dataset_xml_container, self.deployment_dict, self.dataset_dict)
        analyst = DatasetHeaderAnalyst(self.dataset_xml_container, self.deployment_dict, self.dataset_dict)
        analyst.add_reviewer_and_advisor(header_reviewer, header_advisor)
        return analyst


class ConfigAnalystFactory:
    def __init__(self, dataset_xml_container: DatasetXmlContainer, deployment_dict, dataset_dict):
        self.dataset_xml_container = dataset_xml_container
        self.deployment_dict = deployment_dict
        self.dataset_dict = dataset_dict

    def generate(self):
        header_advisor = ConfigFormatAdvisor(self.dataset_xml_container, self.deployment_dict, self.dataset_dict)
        header_reviewer = DatasetConfigReviewer(self.dataset_xml_container, self.deployment_dict, self.dataset_dict)
        analyst = DatasetConfigAnalyst(self.dataset_xml_container, self.deployment_dict, self.dataset_dict)
        analyst.add_reviewer_and_advisor(header_reviewer, header_advisor)
        return analyst


class GlobalAnalystFactory:
    def __init__(self, dataset_xml_container: DatasetXmlContainer, deployment_dict, dataset_dict):
        self.dataset_xml_container = dataset_xml_container
        self.deployment_dict = deployment_dict
        self.dataset_dict = dataset_dict

    def generate(self):
        meta_convention_reviewer = MetadataConventionReviewer(self.dataset_xml_container)
        meta_convention_advisor = MetadataConventionAdvisor(self.dataset_xml_container, self.deployment_dict,
                                                            self.dataset_dict)

        cdm_variable_reviewer = TrajectoryCdmTrajectoryVariableReviewer(self.dataset_xml_container)
        cdm_variable_advisor = TrajectoryCDMTrajectoryVariableAdvisor(self.dataset_xml_container, self.deployment_dict,
                                                                      self.dataset_dict)

        analyst = DatasetConfigAnalyst(self.dataset_xml_container, self.deployment_dict, self.dataset_dict)

        analyst.add_reviewer_and_advisor(cdm_variable_reviewer, cdm_variable_advisor)
        analyst.add_reviewer_and_advisor(meta_convention_reviewer, meta_convention_advisor)
        return analyst


class DataVariableAnalystFactory:
    def __init__(self, dataset_xml_container: DatasetXmlContainer, deployment_dict, dataset_dict):
        self.dataset_xml_container = dataset_xml_container
        self.deployment_dict = deployment_dict
        self.dataset_dict = dataset_dict

    def generate(self):
        trajectory_reviewer = TrajectoryVariableReviewer(self.dataset_xml_container)
        trajectory_advisor = TrajectoryVariableAdvisor(self.dataset_xml_container, self.deployment_dict,
                                                       self.dataset_dict)

        cf_role_reviewer = TrajectoryCFRoleVariableReviewer(self.dataset_xml_container)
        cf_role_advisor = CFRoleAdvisor(self.dataset_xml_container, self.deployment_dict, self.dataset_dict)

        analyst = DatasetConfigAnalyst(self.dataset_xml_container, self.deployment_dict, self.dataset_dict)
        analyst.add_reviewer_and_advisor(trajectory_reviewer, trajectory_advisor)
        analyst.add_reviewer_and_advisor(cf_role_reviewer, cf_role_advisor)

        return analyst


class AnalystFactory:
    def __init__(self, dataset_xml_container: DatasetXmlContainer, deployment_dict, dataset_dict):
        self.dataset_xml_container = dataset_xml_container
        self.deployment_dict = deployment_dict
        self.dataset_dict = dataset_dict
        self.analyst_list = None

    def generate(self):
        header_analyst = HeaderAnalystFactory(self.dataset_xml_container, self.deployment_dict, self.dataset_dict).generate()
        config_analyst = ConfigAnalystFactory(self.dataset_xml_container, self.deployment_dict, self.dataset_dict).generate()
        global_analyst = GlobalAnalystFactory(self.dataset_xml_container, self.deployment_dict, self.dataset_dict).generate()
        data_variable_analyst = DataVariableAnalystFactory(self.dataset_xml_container, self.deployment_dict,
                                                           self.dataset_dict).generate()
        self.analyst_list = [header_analyst, config_analyst, data_variable_analyst, global_analyst]
        return self.analyst_list
