import os
import copy
from .handlers import HANDLERS_LIST
from .ErddapMeta import ErddapMeta


def find_yml_file_name(folder_path):
    # Function to find YAML file names in a given folder
    name_list = []
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".yml"):
            name_list.append(file_name)
    return name_list


class HandlerFactory:
    def __init__(self, config_folder):
        self.config_folder = config_folder
        self.handler_class_list = HANDLERS_LIST
        self._handlers = None

    def get_handlers(self):
        return self

    def generate(self):
        return self.handlers

    def get_all_yaml_file(self):
        name_list = find_yml_file_name(self.config_folder)
        yaml_file_dict = dict()

        for name in name_list:
            yaml_file_dict[name] = os.path.join(self.config_folder, name)
        return yaml_file_dict

    @property
    def handlers(self):
        if self._handlers is None:
            self._handlers = dict()
            yaml_file_dict = self.get_all_yaml_file()
            for handler_class in self.handler_class_list:
                template_name = handler_class.TEMPLATE_NAME + '.yml'
                if template_name in yaml_file_dict:
                    self._handlers[handler_class.TEMPLATE_NAME] = handler_class(
                        yaml_file_dict[template_name])
        return self._handlers


class BaseNetCDFMetaFactory:
    def __init__(self, source_erddap_attrs, meta_mapping_path, source_erddap_variables):
        self.source_erddap_attrs = source_erddap_attrs
        self.source_erddap_variables = source_erddap_variables
        self.meta_mapping = meta_mapping_path
        self.yaml_dicts = dict()

    def generate(self):
        erddap_meta = ErddapMeta(self.source_erddap_attrs, self.source_erddap_variables)
        handler_classes_dict = self.generate_handlers()
        for handler_class_name, content in handler_classes_dict.items():
            content.process(erddap_meta)
        return erddap_meta

    def generate_handlers(self):
        dataset_meta_config_path = os.path.join(self.meta_mapping, "yml_config")
        handlers = HandlerFactory(dataset_meta_config_path).generate()
        return handlers

    def generate_meta_erddap(self):
        return self.source_erddap_attrs

    def generate_adjusted_meta(self):
        new_meta = copy.deepcopy(self.source_erddap_attrs)
        for meta_type, content in self.meta_mapping:
            if meta_type == "global":
                self.enhance_global(new_meta, content)

        return new_meta

    def enhance_global(self, source_meta, mapping_content):
        """
        Assign new values to some keys.
        """
        drop_list = []
        for key, value in mapping_content.items():
            if key in source_meta:
                drop_list.append(key)
                source_meta[value] = source_meta[key]
        for k in drop_list:
            source_meta.pop(k, None)
        return source_meta

    def find_yamls(self) -> list:
        return list()

    def read_yaml(self, yaml_file_path) -> None:
        pass

    def load_yaml(self):
        yaml_path_list = self.find_yamls()
        self.read_yaml(yaml_path_list)

    def load_yaml_handlers(self):
        ...


class NetCDFMetaFactory(BaseNetCDFMetaFactory):
    ...
