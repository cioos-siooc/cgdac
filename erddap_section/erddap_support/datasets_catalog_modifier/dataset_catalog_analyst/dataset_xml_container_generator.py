import copy

from .dataset_xml_container import DatasetXmlContainer
from ..errdap_dataset_configuration_helper import ERDDAPDatasetXMLEditor, read_xml_as_string
from .dataset_modify_actions import DataTypeDatasetModifyActionFactory

class DatasetXmlContainerGenerator:
    def __init__(self, xml_path):
        xml_str = read_xml_as_string(xml_path)
        self.editor = ERDDAPDatasetXMLEditor(xml_str)
        self._dataset_xml_container = None

    def get_header(self):
        return dict(self.editor.get_header())

    def get_dataset_config(self):
        return self.editor.get_all_attr()

    def get_global_variables(self):
        return self.editor.get_all_global_attr(read_comments=True)

    def get_all_data_variables(self):
        return self.editor.get_all_data_variables(read_comments=True)

    def generate(self):
        deep_copied_editor = copy.deepcopy(self.editor)
        deep_copied_editor = self.editor
        data_container = DatasetXmlContainer(deep_copied_editor)
        return data_container