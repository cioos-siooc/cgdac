import yaml
from pathlib import Path


class BaseErddapConfigHandler:
    TEMPLATE_NAME = None
    PROCESS_PRIORITY = 0

    def __init__(self, yaml_path):
        self._yaml_path = yaml_path
        self._yaml_dict = None

    @property
    def yaml_dict(self):
        if self._yaml_dict is None:
            try:
                self._yaml_dict = yaml.safe_load(Path(self._yaml_path).read_text())
            except Exception as e:
                raise Exception(f"Error reading yaml file: {e}")
        return self._yaml_dict

    def process(self, erddao_meta):
        """To be implemented by subclasses"""
        raise NotImplementedError

    def get_template_name(self):
        """Returns the name of the template"""
        if not self.TEMPLATE_NAME:
            raise ValueError("Please set TEMPLATE NAME  in the subclass")
        return self.TEMPLATE_NAME


class DefaultGlobalRemoveConfigHandler(BaseErddapConfigHandler):
    TEMPLATE_NAME = 'global_variable_removal'

    def process(self, erddap_meta):
        for item in self.yaml_dict["global_variable_you_want_to_remove"]:
            erddap_meta.add_remove_global_variable(item)


class DefaultGlobalVariableMapping(BaseErddapConfigHandler):
    TEMPLATE_NAME = 'ocean_glider_global_variable_mapping'

    def process(self, erddap_meta):
        """
        Assign new values to some keys.
        """
        for key, value in self.yaml_dict['global'].items():
            if value:
                if value in erddap_meta.source_global_attrs:
                    erddap_meta.add_global_update_variable(key, erddap_meta.source_global_attrs[value])


class DefaultOceanGliderVariableMapping(BaseErddapConfigHandler):
    TEMPLATE_NAME = 'og_default_global_meta'

    def process(self, erddap_meta):
        for field_name, content in self.yaml_dict.items():
            if field_name not in erddap_meta.source_global_attrs:
                erddap_meta.add_global_update_variable(field_name, content)
            # elif erddap_meta.source_global_attrs[field_name] != content:
            #     internal_field_name = "internal_" + field_name
            #     erddap_meta.add_global_update_variable(internal_field_name,
            #                                            erddap_meta.source_global_attrs[field_name])
            #     erddap_meta.add_global_update_variable(field_name, content)


HANDLERS_LIST = [DefaultGlobalRemoveConfigHandler, DefaultGlobalVariableMapping, DefaultOceanGliderVariableMapping]
