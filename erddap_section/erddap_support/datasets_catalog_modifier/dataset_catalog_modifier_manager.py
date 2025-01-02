from .dataset_catalog_analyst import (DatasetXmlContainerGenerator,
                                      DatasetXmlModifierHandler,
                                      AnalystFactory)


class DatasetCatalogModifyManager:
    def __init__(self, analysts_list, datatset_xml_container, output_path, data_update_handler):
        self.analysts = analysts_list
        self.datatset_xml_container = datatset_xml_container
        self.output_path = output_path
        self.dataset_update_handler = data_update_handler

    def modify(self):
        for analyst in self.analysts:
            for action_list in analyst.analyse_generator():
                self.datatset_xml_container.action_list.set_action(action_list)
                self.dataset_update_handler.update_dataset()
        self.dataset_update_handler.write()

    def analyse_generator(self):
        for analyst in self.analysts:
            action_list_dict = analyst.analyse()
            yield action_list_dict

    def dataset_container_update(self):
        for action_dicts in self.analyse_generator():
            self.datatset_xml_container.set_action(action_dicts)

    def generate_modified_dataset_catalog(self):
        self.dataset_update_handler.update_dataset()
        self.dataset_update_handler.write_dataset()


class DatasetCatalogModifyManagerGenerator:
    def __init__(self, dataset_draftxml_path, output_path, deployment_config, deployment_dict, dataset_dict):
        self._data_container = None
        self.dataset_draft_xml_path = dataset_draftxml_path
        self.deployment_config = deployment_config
        self.deployment_dict = deployment_dict
        self.dataset_dict = dataset_dict
        self.output_path = output_path

    @property
    def data_container(self):
        if self._data_container is None:
            container_generator = DatasetXmlContainerGenerator(self.dataset_draft_xml_path)
            self._data_container = container_generator.generate()
        return self._data_container

    def generate_catalog_analyst(self):
        catalog_analyst_factory = AnalystFactory(self.data_container, self.deployment_dict, self.dataset_dict)
        analyst_list = catalog_analyst_factory.generate()
        return analyst_list

    def generate_data_update_handler(self):
        data_update_handler = DatasetXmlModifierHandler(self.data_container, self.output_path)
        return data_update_handler

    def generate(self):
        analyst_list = self.generate_catalog_analyst()
        data_update_handler = self.generate_data_update_handler()
        catalog_modify_manager = DatasetCatalogModifyManager(analyst_list, self.data_container, self.output_path,
                                                             data_update_handler)
        return catalog_modify_manager
