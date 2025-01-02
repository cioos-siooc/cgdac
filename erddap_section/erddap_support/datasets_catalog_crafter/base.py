import os
from jinja2 import Environment, FileSystemLoader


class BaseTemplateCrafter:
    """
    This class is responsible for crafting the final datasets XML by joining datasets,
    generating headers, and writing the output to the desired directory. It also
    handles the backup of existing datasets files.
    """

    def __init__(self):
        self._env = None

    @property
    def env(self):
        # Create an environment for Jinja2
        if self._env is None:
            current_directory =os.path.dirname(os.path.abspath(__file__))
            file_loader = FileSystemLoader(os.path.join(current_directory, 'templates'))
            self._env = Environment(loader=file_loader)
        return self._env

    def template(self, template_name):
        return self.env.get_template(template_name)

    def render(self, template_name, content):
        return self.template(template_name).render(content)
