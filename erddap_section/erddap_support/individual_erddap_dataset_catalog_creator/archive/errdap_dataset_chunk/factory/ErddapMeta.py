class ErddapMeta:

    def __init__(self, global_attrs, variables):
        self.global_attrs = global_attrs
        self.variables = variables
        self.remove_global_variable = []
        self.add_global_variable_dict = dict()

    def get_global_remove(self):
        return self.remove_global_variable

    def get_global_add_update(self):
        return self.add_global_variable_dict

    def add_remove_global_variable(self, item):
        self.remove_global_variable.append(item)

    def add_global_update_variable(self, variable_name, content):
        self.add_global_variable_dict[variable_name] = content

    @property
    def source_global_attrs(self):
        return self.global_attrs

    def set_title(self, dataset_id):
        if "title" not in self.global_attrs:
            self.add_global_update_variable("title", dataset_id)

    @property
    def source_variables(self):
        return self.global_attrs