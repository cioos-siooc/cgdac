import os
import shutil
import tempfile
import unittest
from erddap_section.erddap_support.individual_erddap_dataset_catalog_creator.individual_erddap_dataset_catalog_handler import \
    IndividualErddapDatasetCatalogHandler


def clean_folder(folder_path):
    """
    Remove all content inside the specified folder.

    :param folder_path: Path to the folder to clean.
    """
    if not os.path.isdir(folder_path):
        raise ValueError(f"The path '{folder_path}' is not a valid directory.")

    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        try:
            if os.path.isfile(item_path) or os.path.islink(item_path):
                os.unlink(item_path)  # Remove file or symbolic link
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)  # Remove directory and its contents
        except Exception as e:
            print(f"Failed to delete {item_path}. Reason: {e}")

def generate_env_file(file_path, variables):
    """
    Generate a .env file with the given key-value pairs.

    :param file_path: Path to the .env file to be created.
    :param variables: Dictionary of key-value pairs to write.
    """
    with open(file_path, "w") as env_file:
        for key, value in variables.items():
            env_file.write(f"{key}={value}\n")


class TestIntegrationIndividualERDDAPDatasetCatalogHandler(unittest.TestCase):

    def setUp(self):
        self.current_folder_path = os.getcwd()
        self.erddap_xml_generation_script = os.path.join(os.path.dirname(os.path.dirname(self.current_folder_path)),'generate_datasets_xml', "GenerateDatasetsXML.sh")

        # Create temporary directories and files for testing
        self.output_dir = os.path.join(self.current_folder_path, "output")
        self.erddap_dir = os.path.join(self.current_folder_path, "erddap")
        self.test_env_file_path = os.path.join(self.current_folder_path, ".test.env")
        self.temp_nc_file = tempfile.NamedTemporaryFile(delete=False, suffix=".nc")
        self.config = {
            "generate_datasets_xml_command_path": self.erddap_xml_generation_script,
            "dataset_config_root": os.path.join(self.current_folder_path, "output"),
        }
        self.deployment_dict = {
            "user": "test_user"
        }
        self.dataset_dict = {
            "dataset_id": "test_dataset_id",
        }
        self.erddap_dict = {
            "erddap_big_parents_path": self.erddap_dir,
            "data_root": "/datasets"
        }


    def tearDown(self):
        # Clean up temporary files and directories
        self.temp_nc_file.close()
        os.unlink(self.temp_nc_file.name)
        clean_folder(self.erddap_dir)
        clean_folder(self.output_dir)
        os.remove(self.test_env_file_path)

    def test_real_workflow(self):
        handler = IndividualErddapDatasetCatalogHandler(self.config,
                                              self.deployment_dict,
                                              self.erddap_dict,
                                              self.dataset_dict)

        env_variables = {
            "ERDDAP_DATASET": "./resource/",
            "ERDDAP_ERDDAP_DATA": "{}".format(self.erddap_dir),
            "DOCKER_VERSION": "2.23-jdk17-openjdk"
        }

        generate_env_file(self.test_env_file_path, env_variables)

        # config the test env file
        os.environ["DOCKER_ENV"] = self.test_env_file_path

        # Simulate ERDDAP logs folder and output file
        logs_dir = os.path.join(self.erddap_dir, "logs")

        # Execute the workflow
        handler.generate_draft_dataset_xml()


