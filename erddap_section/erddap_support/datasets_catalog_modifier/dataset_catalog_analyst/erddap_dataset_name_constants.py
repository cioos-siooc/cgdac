# This section defined what parts that a erddap dataset xml consist of
DATASET_HEADER = "dataset_header"
DATASET_CONFIG = "dataset_config"
DATASET_GLOBAL = "dataset_global"
DATASET_VARIABLE = "dataset_variable"

# Dataset Didct
CF_DEFAULT_DATASET_DICT = "cf_default_dataset_dict"

class ErddapSections:
    DATASET_HEADER =DATASET_HEADER
    DATASET_CONFIG = DATASET_CONFIG
    DATASET_GLOBAL = DATASET_GLOBAL
    DATASET_VARIABLE = DATASET_VARIABLE

#DATASET HEADER
DATASET_ID = "datasetID"

# DATASET CONFIG
DATASET_CONFIG_ACCESSIBLE_VIA_FILES = "accessibleViaFiles"
DATASET_CONFIG_FILE_DIR = "fileDir"
DATASET_CONFIG_UPDATE_EVERY_N_MILLIS = "updateEveryNMillis"
DATASET_CONFIG_FILE_NAME_REGEX = "fileNameRegex"
DATASET_CONFIG_PATH_REGEX = "pathRegex"

# DATASET GLOBAL
CONVENTIONS = "Conventions"



# ACTION LIST
DATA_SOURCE = "data_source"
DATA_ID = "data_id"
DATASET = "dataset"
DATA_CONTAINER = "data_container"

DATA_FIELD_NAME = "data_field_name"
SECTION = "section"
EXPECTED_VALUE = "expected_value"
ACTUAL_VALUE = "actual_value"

DATASET_DICT = "dataset_dict"

PLACE_HOLDER_STR = "nf2o34uhr"

class ActionDictConstants:
    DATA_SOURCE = DATA_SOURCE
    DATA_ID = DATA_ID
    DATA_FIELD_NAME = DATA_FIELD_NAME
    # data source name
    DATASET = DATASET
    DATA_CONTAINER = DATA_CONTAINER

    SECTION = SECTION
    EXPECTED_VALUE = EXPECTED_VALUE
    ACTUAL_VALUE = ACTUAL_VALUE
    DATASET_DICT = DATASET_DICT


# action list actions:
EDIT = "edit"
REMOVE = "remove"
ADD = "add"
NO_ACTION = "no_action"


DESTINATION_NAME = "destinationName"
DATA_TYPE = "dataType"
ADD_ATTRIBUTES = "addAttributes"


class ActionListActionsConstants:
    # apply for all sections
    EDIT = EDIT
    REMOVE = REMOVE
    ADD = ADD
    NO_ACTION = NO_ACTION

    # for data type section
    UPDATE_DESTINATION = "update_destination"
    UPDATE_DATATYPE = "update_data_type"
    UPDATE_ATT = "update_attribute"
    REMOVE_ATT = "remove_attribute"
    ADD_ATT = "add_attribute"

class CdmVariablesConstants:
    TRAJECTORY = "TRAJECTORY"
    TRAJECTORY_ID = "trajectory_id"




erddap_catalog_sections = {DATASET_HEADER: ["type", "datasetID", "active"],
                           DATASET_CONFIG: ["accessibleViaFiles",
                                            "updateEveryNMillis",
                                            "fileDir",
                                            "fileNameRegex",
                                            "recursive",
                                            "pathRegex",
                                            "metadataFrom",
                                            "standardizeWhat",
                                            "sortedColumnSourceName",
                                            "sortFilesBySourceNames",
                                            "fileTableInMemory"]
                           }
