"""
Dataset Catalog Analyst.
This class can generate a catalog dataset.
It analyzes the dataset XML and determines the necessary modifications before
integrating it into the ERDDAP dataset catalog.


For basic usage, for example, if the draft dataset is missing the cdm_data_type,
the analyst should be able to suggest adding a cdm_data_type value.
Additionally, they should recommend adding cf_role="trajectory_id" to a constant
data variable and suggest some cdm_trajectory_variables.


For more advance usage, if user wish to have a OG 1.0 compliant dataset, it should be
able to suggest for the data variable renaming. for example
"""
from typing import TypedDict, Dict
from .dataset_xml_container import DatasetXmlContainer
from .erddap_dataset_name_constants import (DATASET_HEADER,
                                            DATASET_CONFIG,
                                            DATASET_VARIABLE)


class DatasetMapping(TypedDict):
    data_source: str
    data_id: str


class ComparingMapping(TypedDict):
    dataset: DatasetMapping
    data_container: DatasetMapping


ComparingMappingList = Dict[str, ComparingMapping]


class BaseAnalyst:
    SECTION = None
    REVIEWER_POSITION_INDEX = 0
    ADVISOR_POSITION_INDEX = 1

    def __init__(self, dataset_xml_container: DatasetXmlContainer, deployment_dict, dataset_dict):
        self.dataset_xml_container = dataset_xml_container
        self.deployment_dict = deployment_dict
        self.dataset_dict = dataset_dict
        self.reviewer_advisor = []

    def analyse(self):
        return list(self.analyse_generator())

    def analyse_generator(self):
        for value in self.reviewer_advisor:
            reviewer = value[self.REVIEWER_POSITION_INDEX]
            advisor = value[self.ADVISOR_POSITION_INDEX]
            feedback = reviewer.review()
            yield advisor.suggest(feedback)

    def add_reviewer_and_advisor(self, reviewer, advisor):
        self.reviewer_advisor.append((reviewer, advisor))


class BaseStaticDatasetCatalogAnalyst(BaseAnalyst):
    def __init__(self, dataset_xml_container: DatasetXmlContainer, deployment_dict, dataset_dict):
        super().__init__(dataset_xml_container, deployment_dict, dataset_dict)

    def analyse(self):
        """
         When we want the dataset to adhere to static standards,
         there is no need to review the value. Since we do not offer customization options,
         we can simply set the value to comply with the standard, such as the dataset ID.
        """
        feedback = None
        advisor = self.reviewer_advisor[self.REVIEWER_POSITION_INDEX][self.ADVISOR_POSITION_INDEX]
        action_list_dict = advisor.suggest(feedback)
        return action_list_dict


class DatasetHeaderAnalyst(BaseStaticDatasetCatalogAnalyst):
    SECTION = DATASET_HEADER


class DatasetConfigAnalyst(BaseStaticDatasetCatalogAnalyst):
    SECTION = DATASET_CONFIG


class BaseDynamicDatasetCatalogAnalyst(BaseAnalyst):
    ...


class DatasetDataVariableAnalyst(BaseStaticDatasetCatalogAnalyst):
    SECTION = DATASET_VARIABLE

    def analyse(self):
        return list(self.analyse_generator())


    def analyse_generator(self):

        for value in self.reviewer_advisor:
            reviewer = value[self.REVIEWER_POSITION_INDEX]
            advisor = value[self.ADVISOR_POSITION_INDEX]
            feedback = reviewer.review()
            yield advisor.suggest(feedback)
