import unittest
from unittest.mock import patch, MagicMock

from erddap_section.erddap_support.datasets_catalog_crafter import base


class TestBaseTemplateCrafter(unittest.TestCase):

    def setUp(self):
        self.crafter = base.BaseTemplateCrafter()

    @patch('erddap_section.erddap_support.datasets_catalog_crafter.base.FileSystemLoader')
    @patch('erddap_section.erddap_support.datasets_catalog_crafter.base.Environment')
    def test_env_initialization(self, mock_environment, mock_loader):
        """
        Test that the environment is initialized correctly and only once.
        """

        # Ensure the environment is not initialized initially
        self.assertIsNone(self.crafter._env)

        # Access the env property, which should initialize it
        env = self.crafter.env

        # Ensure the Environment was created with the correct loader
        mock_loader.assert_called_once()
        mock_environment.assert_called_once_with(loader=mock_loader.return_value)

        # Access the env property again to check lazy initialization (should not re-initialize)
        env_second = self.crafter.env
        mock_environment.assert_called_once()  # Ensure environment initialization is called only once

    @patch('erddap_section.erddap_support.datasets_catalog_crafter.base.Environment')
    @patch('erddap_section.erddap_support.datasets_catalog_crafter.base.FileSystemLoader')
    def test_env_property(self, mock_file_loader, mock_environment):
        """
        Test the env property to ensure it creates a Jinja2 environment
        and finds the templates 'datasets.xml' and 'header.xml'.
        """
        # Mock environment and file loader behavior
        mock_env_instance = MagicMock()
        mock_template = MagicMock()

        # Make the environment return the mock template when get_template is called
        mock_env_instance.get_template.return_value = mock_template
        mock_environment.return_value = mock_env_instance


        # Access the env property to trigger the creation of the environment
        env = self.crafter.env

        # Ensure that FileSystemLoader is initialized with 'templates' directory
        mock_file_loader.assert_called_once()

        # Ensure that Environment is created with the correct loader
        mock_environment.assert_called_once_with(loader=mock_file_loader.return_value)

        # Ensure get_template is called with 'datasets.xml'
        env.get_template('datasets.xml')
        env.get_template('header.xml')
        mock_env_instance.get_template.assert_any_call('datasets.xml')
        mock_env_instance.get_template.assert_any_call('header.xml')


    # @patch('erddap_section.erddap_support.datasets_catalog_crafter.base.BaseTemplateCrafter.env')
    def test_template_loading(self):
        """
        Test that the correct template is loaded.
        """
        # Mock the environment's get_template method
        # mock_template = MagicMock()
        # mock_env.get_template.return_value = mock_template

        # Call the template method
        env = self.crafter.env
        e = self.crafter.env.list_templates()
        tmp1 = self.crafter.template('datasets.xml')


    @patch('erddap_section.erddap_support.datasets_catalog_crafter.base.BaseTemplateCrafter.template')
    def test_rendering_template(self, mock_template):
        """
        Test that a template is rendered with the correct content.
        """
        # Mock a template's render method
        mock_render = MagicMock()
        mock_template.return_value.render = mock_render
        mock_render.return_value = 'rendered content'

        # Define some content to render
        content = {'key': 'value'}

        # Call the render method
        result = self.crafter.render('my_template.html', content)

        # Ensure template method is called with the correct template name
        mock_template.assert_called_once_with('my_template.html')

        # Ensure render was called with the correct content
        mock_render.assert_called_once_with(content)

        # Check the result of the rendering
        self.assertEqual(result, 'rendered content')


if __name__ == '__main__':
    unittest.main()
