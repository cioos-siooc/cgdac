"""
Dataset Catalog Analyst.
This class can generate a catalog dataset.
It analyzes the dataset XML and determines the necessary modifications before
integrating it into the ERDDAP dataset catalog.

For basic usage, for example, if the draft dataset is missing the cdm_data_type,
the analyst should be able to suggest adding a cdm_data_type value.
Additionally, they should recommend adding cf_role="trajectory_id" to a constant
data variable and suggest some cdm_trajectory_variables.

For more advance usage, and for example if user wish to have a OG 1.0 compliant dataset, it should be
able to suggest for the data variable renaming. For example Dissolved oxygen -> DOXY

Able to define some constant variable if it is not already exist in the original dataset.
for example TRAJECTORY, WMO_IDENTIFIER and etc
"""
from .dataset_catalog_analyst import BaseAnalyst
from .dataset_update_handler import DatasetXmlModifierHandler
from .dataset_xml_container_generator import DatasetXmlContainerGenerator
from .dataset_catalog_analyst_factory import AnalystFactory