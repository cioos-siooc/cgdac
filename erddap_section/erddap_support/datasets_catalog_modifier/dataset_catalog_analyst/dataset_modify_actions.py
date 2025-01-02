# This section defined what parts that an erddap dataset xml consist of
BASE = "base"

from typing import List
from typing import Union
from pydantic import BaseModel

from .erddap_dataset_name_constants import DATA_FIELD_NAME, SECTION, EXPECTED_VALUE, ACTUAL_VALUE, NO_ACTION, \
    ActionDictConstants
from .erddap_dataset_name_constants import DATASET_HEADER, DATASET_CONFIG, DATASET_GLOBAL, DATASET_VARIABLE
from .erddap_dataset_name_constants import ActionListActionsConstants, DESTINATION_NAME, DATA_TYPE, ADD_ATTRIBUTES
from .utils import pair_lists_by_key_with_unmatched


class ActionDict(BaseModel):
    data_field_name: str
    section: str
    expected_value: Union[str, None, int, float, dict]
    actual_value: Union[str, None, int, float, dict]


class BaseDatasetModifyAction:
    TYPE = BASE

    def __init__(self):
        self.data_field_name = None
        self.section = None
        self.expected_value = None
        self.value = None
        self._action = None

    def set_action(self, value_dict):
        ActionDict(**value_dict)
        self.data_field_name = value_dict[DATA_FIELD_NAME]
        self.section = value_dict[SECTION]
        self.expected_value = value_dict[EXPECTED_VALUE]
        self.value = value_dict[ACTUAL_VALUE]
        assert self.section == self.TYPE, "Must set value for correct modify action type. Type is {} input is {}".format(
            self.TYPE, value_dict)

    def __eq__(self, value):
        if type(value) == type(self):
            return self.is_same(value)
        elif type(value) == dict:
            data_field_name = value[DATA_FIELD_NAME]
            section = value[SECTION]
            expected_value = value[EXPECTED_VALUE]
            value = value[ACTUAL_VALUE]
            return (
                    self.data_field_name == data_field_name and
                    self.section == section and
                    self.expected_value == expected_value and
                    self.value == value
            )

    def _get_edit_action(self):
        return ActionListActionsConstants.EDIT

    def _get_action(self):
        if self.value == self.expected_value:
            # None means not doing anything
            return None
        elif self.value == None and self.expected_value != None:
            return ActionListActionsConstants.ADD
        elif self.value != self.expected_value and self.value != None and self.expected_value != None:
            return self._get_edit_action()
        elif self.expected_value == None and self.value != None:
            return ActionListActionsConstants.REMOVE
        else:
            raise Exception("Unknown action")

    @property
    def action_flag(self):
        if self._action is None:
            self._action = self._get_action()

        return self._action

    @action_flag.setter
    def action_flag(self, value):
        self._action = value

    def is_same(self, action):
        return (
                self.data_field_name == action.data_field_name and
                self.section == action.section and
                self.expected_value == action.expected_value and
                self.value == action.value
        )


class HeaderDatasetModifyAction(BaseDatasetModifyAction):
    TYPE = DATASET_HEADER


class ConfigDatasetModifyAction(BaseDatasetModifyAction):
    TYPE = DATASET_CONFIG


class GlobalDatasetModifyAction(BaseDatasetModifyAction):
    TYPE = DATASET_GLOBAL


class DataTypeDatasetModifyAction(BaseDatasetModifyAction):
    TYPE = DATASET_VARIABLE

    def _get_edit_action(self):
        data_variable_tags = [DESTINATION_NAME, DATA_TYPE, ADD_ATTRIBUTES]
        action_list = []
        for variable_tag in data_variable_tags:
            if self.expected_value[variable_tag] != self.value[variable_tag]:
                if variable_tag == DESTINATION_NAME:
                    action_list.append(ActionListActionsConstants.UPDATE_DESTINATION)
                elif variable_tag == DATA_TYPE:
                    action_list.append(ActionListActionsConstants.UPDATE_DATATYPE)
                elif variable_tag == ADD_ATTRIBUTES:
                    action_list.extend(self._get_data_variable_attribute_action())
        return action_list

    def _get_data_variable_attribute_action(self):
        action_list = []
        actual_attribute = self.value[ADD_ATTRIBUTES]
        expect_attribute = self.expected_value[ADD_ATTRIBUTES]
        for att in expect_attribute:
            if att in actual_attribute:
                ...
            else:
                action_list.append(ActionListActionsConstants.ADD_ATT)
        return []


class BaseModifyActionFactory:
    ACTION_CLASS = None

    def generate(self, value):
        action = self.ACTION_CLASS()
        action.set_action(value)
        action_flag = self.get_action_flag(value)
        action.action_flag = action_flag
        return [action]

    def get_action_flag(self, action_dict):
        actual_value = action_dict[ACTUAL_VALUE]
        expected_value = action_dict[EXPECTED_VALUE]

        if actual_value == expected_value:
            return NO_ACTION  # No action required

        if actual_value is None:
            return ActionListActionsConstants.ADD if expected_value is not None else Exception("Unknown action")

        if expected_value is None:
            return ActionListActionsConstants.REMOVE

        return self._get_edit_action_flag(actual_value,
                                          expected_value) if actual_value != expected_value else Exception(
            "Unknown action")

    def _get_edit_action_flag(self, actual_value, expected_value):
        return ActionListActionsConstants.EDIT


class HeaderDatasetModifyActionFactory(BaseModifyActionFactory):
    ACTION_CLASS = HeaderDatasetModifyAction


class ConfigDatasetModifyActionFactory(BaseModifyActionFactory):
    ACTION_CLASS = ConfigDatasetModifyAction


class GlobalDatasetModifyActionFactory(BaseModifyActionFactory):
    ACTION_CLASS = GlobalDatasetModifyAction


class DataTypeDatasetModifyActionFactory(BaseModifyActionFactory):
    ACTION_CLASS = DataTypeDatasetModifyAction

    def generate(self, value):
        value = self.analyse_value(value)
        if type(value) == dict:
            return super().generate(value)
        else:
            value_list = []
            for v in value:
                value_list.extend(super().generate(v))
            return value_list

    def _get_edit_action_flag(self, actual_value, expected_value):
        data_variable_tags = [DESTINATION_NAME, DATA_TYPE, ADD_ATTRIBUTES]
        for variable_tag in data_variable_tags:
            if variable_tag in actual_value and variable_tag in expected_value and actual_value[variable_tag] != \
                    expected_value[variable_tag]:
                if variable_tag == DESTINATION_NAME:
                    return ActionListActionsConstants.UPDATE_DESTINATION
                if variable_tag == DATA_TYPE:
                    return ActionListActionsConstants.UPDATE_DATATYPE
                if variable_tag == ADD_ATTRIBUTES:
                    return self._get_edit_action_data_variable_attribute_action_flag(actual_value, expected_value)

    def _get_edit_action_data_variable_attribute_action_flag(self, actual_value, expected_value):
        actual_value_add_attributes = actual_value[ADD_ATTRIBUTES]
        expected_value_add_attributes = expected_value[ADD_ATTRIBUTES]
        if expected_value_add_attributes == None:
            return ActionListActionsConstants.REMOVE_ATT
        elif actual_value_add_attributes == None:
            return ActionListActionsConstants.ADD_ATT
        elif actual_value_add_attributes != expected_value_add_attributes:
            return ActionListActionsConstants.UPDATE_ATT
        else:
            return ActionListActionsConstants.NO_ACTION

    def analyse_attribute(self, actual_value, expected_value, value):
        value_list = []
        if actual_value is not None and expected_value is not None:
            actual_add_attributes = actual_value
            expected_add_attributes = expected_value
            if actual_add_attributes != expected_add_attributes:
                att_dict_pair = pair_lists_by_key_with_unmatched(expected_add_attributes, actual_add_attributes, "name")

                for expected_add_attribute, actual_add_attribute in att_dict_pair:
                    new_value = {
                        DATA_FIELD_NAME: value[DATA_FIELD_NAME],
                        SECTION: value[SECTION],
                        ACTUAL_VALUE: value[ACTUAL_VALUE],
                    }
                    if expected_add_attribute != actual_add_attribute:
                        new_value[EXPECTED_VALUE] = {
                            ADD_ATTRIBUTES: expected_add_attribute
                        }
                        value_list.append(new_value)
        elif actual_value is not None and expected_value is None:
            for actual_add_attribute in actual_value:
                new_value = {
                    DATA_FIELD_NAME: value[DATA_FIELD_NAME],
                    SECTION: value[SECTION],
                    ACTUAL_VALUE: {
                        "addAttributes":
                            actual_add_attribute
                    },
                    EXPECTED_VALUE: {
                        "addAttributes":
                            None
                    }
                }
                value_list.append(new_value)
        elif actual_value is None and expected_value is not None:
            for expected_attribute in expected_value:
                new_value = {
                    DATA_FIELD_NAME: value[DATA_FIELD_NAME],
                    SECTION: value[SECTION],
                    ACTUAL_VALUE: {
                        "addAttributes":
                            actual_value
                    },
                    EXPECTED_VALUE: {
                        "addAttributes":
                            expected_attribute
                    }
                }
                value_list.append(new_value)

        return value_list

    def analyse_value(self, value):
        # actual value dict and expected value dict may have many difference which means
        # it required many different action to reach the expected state.
        # ideally each action object can only do one action
        # this function is used to split the value dict into different action dicts
        actual_value = value[ACTUAL_VALUE]
        expected_value = value[EXPECTED_VALUE]

        if None in (actual_value, expected_value):
            return value
        else:
            value_list = []
            if ADD_ATTRIBUTES in actual_value and ADD_ATTRIBUTES in expected_value:
                actual_add_attributes = actual_value[ADD_ATTRIBUTES]
                expected_add_attributes = expected_value[ADD_ATTRIBUTES]
                value_list.extend(self.analyse_attribute(actual_add_attributes, expected_add_attributes, value))

            data_variable_tags = [DESTINATION_NAME, DATA_TYPE]

            for variable_tag in data_variable_tags:
                new_value = {
                    DATA_FIELD_NAME: value[DATA_FIELD_NAME],
                    SECTION: value[SECTION],
                    ACTUAL_VALUE: value[ACTUAL_VALUE],
                }
                if variable_tag in actual_value and variable_tag in expected_value:
                    if actual_value[variable_tag] != expected_value[variable_tag]:
                        new_value[EXPECTED_VALUE] = {
                            variable_tag: expected_value[variable_tag]
                        }
                        value_list.append(new_value)
            return value_list


class DatasetModifyActionList:
    ACTION_FACTORY_CLASSES = [
        HeaderDatasetModifyActionFactory,
        ConfigDatasetModifyActionFactory,
        GlobalDatasetModifyActionFactory,
        DataTypeDatasetModifyActionFactory
    ]

    def __init__(self):
        self.actions: List[BaseDatasetModifyAction] = []
        self.action_archive = []

    def pop_first(self):
        value = self.actions.pop(0)
        self.action_archive.append(value)
        return value


    def __bool__(self):
        # Return True if the list is not empty
        return bool(self.actions)

    def __len__(self):
        # Optional: define length to support len(my_list)
        return len(self.actions)

    def _set_section(self, value):
        if SECTION in value:
            for action_factory_class in self.ACTION_FACTORY_CLASSES:
                section = value[SECTION]
                if action_factory_class.ACTION_CLASS.TYPE == section:
                    factory = action_factory_class()
                    actions = factory.generate(value)
                    self.actions.extend(actions)
                    break
            else:
                raise Exception("Unexpected section {}.".format(section))
        else:
            raise Exception("Value must contain a section The value provided is {}.".format(value))

    def set_action(self, value):
        if isinstance(value, list):
            for v in value:
                self._set_section(v)
        else:
            self._set_section(value)

    def __contains__(self, item):
        # Define how 'in' works
        return any(item == action for action in self.actions)

    def __iter__(self):
        return iter(self.actions)


def get_new_action_dict() -> ActionDict:
    action_dict = {
        ActionDictConstants.DATA_FIELD_NAME: None,
        ActionDictConstants.SECTION: None,
        ActionDictConstants.EXPECTED_VALUE: None,
        ActionDictConstants.ACTUAL_VALUE: None,
    }
    return action_dict
