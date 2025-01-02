"""
The purpose of this module is taking the data xml container, draft dataset xml, output path as variable
generate an updated version of dataset xml and write it to the given path.
"""
from .dataset_xml_container import DatasetXmlContainer
from .erddap_dataset_name_constants import ErddapSections, ActionListActionsConstants


class DatasetXmlModifierHandler:
    def __init__(self, dataset_xml_container: DatasetXmlContainer, output_path: str):
        self.dataset_xml_container = dataset_xml_container
        self.output_path = output_path
        self.editor = self.dataset_xml_container.dataset_editor

    def write(self):
        self.editor.write(self.output_path)

    def update_dataset(self):
        while self.dataset_xml_container.action_list:
            action = self.dataset_xml_container.action_list.pop_first()
            if action.action_flag != ActionListActionsConstants.NO_ACTION:
                if action.section == ErddapSections.DATASET_VARIABLE:
                    if action.action_flag == ActionListActionsConstants.REMOVE:
                        source_name = action.data_field_name
                        self.editor.remove_dataset_variable(source_name)
                    elif action.action_flag == ActionListActionsConstants.ADD:
                        source_name = action.data_field_name
                        destination_name = action.expected_value["destinationName"]
                        data_type = action.expected_value["dataType"]
                        add_attributes_dict = action.expected_value["addAttributes"]
                        self.editor.add_data_variable(source_name, destination_name, data_type, add_attributes_dict)
                    elif action.action_flag == ActionListActionsConstants.UPDATE_DATATYPE:
                        source_name = action.data_field_name
                        new_datat_type = action.expected_value["dataType"]
                        self.editor.edit_data_variable_data_type(source_name, new_datat_type)
                    elif action.action_flag == ActionListActionsConstants.UPDATE_DESTINATION:
                        source_name = action.data_field_name
                        destination_name = action.expected_value["destinationName"]
                        self.editor.edit_data_variable_destination_name(source_name, destination_name)
                    elif action.action_flag in (
                    ActionListActionsConstants.ADD_ATT, ActionListActionsConstants.UPDATE_ATT):
                        source_name = action.data_field_name
                        attr_name = action.expected_value["addAttributes"]["name"]
                        new_attr_text = action.expected_value["addAttributes"]["value"]
                        self.editor.set_data_variable_add_attribute(source_name, attr_name, new_attr_text)
                    elif action.action_flag == ActionListActionsConstants.REMOVE_ATT:
                        source_name = action.data_field_name
                        attr_name = action.value["addAttributes"]["name"]
                        self.editor.remove_data_variable_add_attribute(source_name, attr_name)
                    else:
                        raise Exception("No other action allowed for the {}".format(action.section))
                else:
                    key = action.data_field_name
                    target_value = action.expected_value
                    if action.section == ErddapSections.DATASET_HEADER:
                        if action.action_flag == ActionListActionsConstants.EDIT:
                            self.editor.set_header(key, target_value)
                        elif action.action_flag != ActionListActionsConstants.NO_ACTION:
                            raise Exception("No other action allowed for the {}".format(action.section))
                    elif action.section == ErddapSections.DATASET_CONFIG:
                        if action.action_flag in (ActionListActionsConstants.EDIT, ActionListActionsConstants.ADD):
                            self.editor.set_erddap_config(key, target_value)
                        elif action.action_flag == ActionListActionsConstants.REMOVE:
                            self.editor.remove_dataset_config(key)
                        elif action.action_flag != ActionListActionsConstants.NO_ACTION:
                            raise Exception("No other action allowed for the {}".format(action.section))
                    elif action.section == ErddapSections.DATASET_GLOBAL:
                        if action.action_flag in (ActionListActionsConstants.EDIT, ActionListActionsConstants.ADD):
                            self.editor.set_added_global_variable(key, target_value)
                        elif action.action_flag == ActionListActionsConstants.REMOVE:
                            self.editor.remove_global_variable(key)
                        elif action.action_flag != ActionListActionsConstants.NO_ACTION:
                            raise Exception("No other action allowed for the {}".format(action.section))
