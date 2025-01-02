from .erddap_dataset_name_constants import ActionDictConstants
from .erddap_dataset_name_constants import (DATASET_HEADER,
                                            DATASET_CONFIG,
                                            DATASET_VARIABLE,
                                            DATASET_GLOBAL,
                                            DATASET_ID,
                                            DATASET_CONFIG_UPDATE_EVERY_N_MILLIS,
                                            DATASET_CONFIG_FILE_NAME_REGEX,
                                            DATASET_CONFIG_FILE_DIR,
                                            CF_DEFAULT_DATASET_DICT,
                                            CONVENTIONS)

class HeaderMappingList:
    BASE_COMPARING_MAPPING_LIST = {
            DATASET_ID: {
                ActionDictConstants.DATASET: {
                    ActionDictConstants.DATA_SOURCE: ActionDictConstants.DATASET_DICT,
                    ActionDictConstants.DATA_ID: DATASET_ID
                },
                ActionDictConstants.DATA_CONTAINER: {
                    ActionDictConstants.DATA_SOURCE: DATASET_HEADER,
                    ActionDictConstants.DATA_ID: DATASET_ID
                }
            },
        }

class ConfigMappingList:
    BASE_COMPARING_MAPPING_LIST = {
            DATASET_CONFIG_FILE_DIR: {
                ActionDictConstants.DATASET: {ActionDictConstants.DATA_SOURCE: ActionDictConstants.DATASET_DICT,
                          ActionDictConstants.DATA_ID: DATASET_CONFIG_FILE_DIR},
                ActionDictConstants.DATA_CONTAINER: {ActionDictConstants.DATA_SOURCE: DATASET_CONFIG,
                                 ActionDictConstants.DATA_ID: DATASET_CONFIG_FILE_DIR}
            },
            DATASET_CONFIG_UPDATE_EVERY_N_MILLIS: {
                ActionDictConstants.DATASET: {ActionDictConstants.DATA_SOURCE: ActionDictConstants.DATASET_DICT,
                          ActionDictConstants.DATA_ID: DATASET_CONFIG_UPDATE_EVERY_N_MILLIS},
                ActionDictConstants.DATA_CONTAINER: {ActionDictConstants.DATA_SOURCE: DATASET_CONFIG,
                                 ActionDictConstants.DATA_ID: DATASET_CONFIG_UPDATE_EVERY_N_MILLIS}
            },
            DATASET_CONFIG_FILE_NAME_REGEX: {
                ActionDictConstants.DATASET: {ActionDictConstants.DATA_SOURCE: ActionDictConstants.DATASET_DICT,
                          ActionDictConstants.DATA_ID: DATASET_CONFIG_FILE_NAME_REGEX},
                ActionDictConstants.DATA_CONTAINER: {ActionDictConstants.DATA_SOURCE: DATASET_CONFIG,
                                 ActionDictConstants.DATA_ID: DATASET_CONFIG_FILE_NAME_REGEX}
            }
        }