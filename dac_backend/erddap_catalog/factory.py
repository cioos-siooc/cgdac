import os
import glob
import logging
from glider_dac.app import app
from pathlib import Path
from datetime import datetime
from glider_dac.models import Deployment

from erddap_section import BasicCatalogBuilder

from .creators import CatalogGenerator, IndividualCatalogGenerator
from common import log_formatter

logger = logging.getLogger(__name__)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(log_formatter)
logger.addHandler(ch)
logger.setLevel(logging.INFO)
template_dir = Path(__file__).parent.parent / "individual_erddap_dataset_catalog_creator" / "templates"

DATASET_CHUNK_NAME = 'dataset.xml'


def get_latest_nc_file(full_path):
    '''
    Returns the lastest netCDF file found in the directory

    :param str root: Root of the directory to scan
    '''
    list_of_files = glob.glob('{}/*.nc'.format(full_path))
    if not list_of_files:  # Check for no files
        return None
    print("---------------")
    print(max(list_of_files, key=os.path.getmtime))
    print("--------------")
    return max(list_of_files, key=os.path.getmtime)


def get_latest_yml_file(full_path):
    '''
    Returns the lastest netCDF file found in the directory

    :param str root: Root of the directory to scan
    '''
    list_of_files = glob.glob('{}/*.yml'.format(full_path))
    if not list_of_files:  # Check for no files
        return None
    return max(list_of_files, key=os.path.getmtime)


class BaseCreatorFactory:
    """
    This base class is only for the documentation of this type Classes
    We use the factory class to generate the creator class instance
    we prepare any needed variables for the creator, so creator doesn't need to wrong about the database and searching
    """

    def generate(self):
        raise NotImplementedError


class IndividualCatalogCreatorFactory(BaseCreatorFactory):

    def __init__(self, data_root, config):
        self.config = config
        self.data_root = data_root

    def get_dataset_chunk_path(self, deployment_dir):
        dataset_chunk_path = os.path.join(self.data_root, deployment_dir, DATASET_CHUNK_NAME)
        if not os.path.exists(dataset_chunk_path):
            return None
        return dataset_chunk_path

    def get_deployment_abs_path(self, deployment_dir):
        if not deployment_dir.startswith(self.data_root):
            deployment_dir = os.path.join(self.data_root, deployment_dir)
        return deployment_dir

    def skip_dataset(self):
        # when the database is stable, we don't want to update or check it again
        ...

    def get_last_run(self, last_run_path):
        if os.path.exists(last_run_path):
            try:
                with open(last_run_path, 'r') as f:
                    last_run = datetime.utcfromtimestamp(int(f.read()))
            except Exception as e:
                last_run = 0
        else:
            last_run = 0
        return last_run

    def get_latest_nc_file(self, deployment_dir):
        latest_nc_file = get_latest_nc_file(self.get_deployment_abs_path(deployment_dir))
        if latest_nc_file:
            return os.path.getmtime(latest_nc_file)
        return 0

    def get_latest_yml_config_folder(self, deployment_dir):
        return os.path.join(deployment_dir, "yml_config")

    def get_latest_config_modified_time(self, config_dir):
        # if the yml config got updated. we want to recreate the dataset.xml
        latest_yml = get_latest_yml_file(config_dir)
        if latest_yml:
            return os.path.getmtime(latest_yml)
        return 0

    def get_latest_related_file_modified_time(self, deployment_dir):
        latest_yml_config_modified_time = self.get_latest_config_modified_time(
            self.get_latest_yml_config_folder(deployment_dir))
        latest_nc_modified_time = self.get_latest_nc_file(deployment_dir)
        return max(latest_nc_modified_time, latest_yml_config_modified_time)

    def get_dataset_chunk_modified_time(self, deployment_dir):
        dataset_chunk_path = self.get_dataset_chunk_path(deployment_dir)
        last_m_time = os.path.getmtime(dataset_chunk_path)
        return last_m_time

    def detect_file_changes(self, deployment_dir):
        return self.get_dataset_chunk_modified_time(deployment_dir) < self.get_latest_related_file_modified_time(
            deployment_dir)

    def get_deployments_to_update_generator(self):
        # Go through all of the deployments and decide which deployment should be updated
        deploy_queryset = Deployment.query.all()
        for deployment in deploy_queryset:
            logger.debug(deployment.username)
            should_create = False
            # if the datasets.default.xml haven't been created then generate the datasets.default.xml
            dataset_chunk_path = self.get_dataset_chunk_path(deployment.deployment_dir)
            if not dataset_chunk_path:
                if self.get_latest_nc_file(deployment.deployment_dir):
                    should_create = True
            elif self.detect_file_changes(self.get_deployment_abs_path(deployment.deployment_dir)):
                # if the datasets chunk exist but if was created before latest netCDF file
                should_create = True
            if should_create:
                last_run_path = os.path.join(self.get_deployment_abs_path(deployment.deployment_dir), 'lastrun')
                update_dict = {
                    "name": deployment.name,
                    "deployment_date": deployment.deployment_date,
                    "data_chuck_path": dataset_chunk_path,
                    "data_root": self.data_root,
                    "last_process_time_path": last_run_path,
                    "dataset_ID": deployment.name,
                    "deployment_dir": self.get_deployment_abs_path(deployment.deployment_dir),
                    "checksum": deployment.checksum,
                    "completed": deployment.completed,
                    "delayed_mode": deployment.delayed_mode,
                    "latest_file": deployment.selected_file,
                    "platform_name": deployment.glider_name,
                    "wmo_id": deployment.wmo_id
                }

                yield update_dict

    def generate(self):
        # generate builder list
        creators = []
        logger.info("Selecting deployment for update")
        for deployment_dict in self.get_deployments_to_update_generator():
            creators.append(IndividualCatalogGenerator(deployment_dict, self.config))
        logger.info("{} deployments was selected to update".format(len(creators)))
        return creators


class CatalogCreatorFactory(BaseCreatorFactory):
    def __init__(self, individual_dataset_folder=app.config["INDIVIDUAL_DATASET_FOLDER"],
                 erddap_dataset_xml=app.config["ERDDAP_DATASETS_XML"]):
        """
        Initialize the CatalogCreatorFactory.

        Args:
            data_root (str): Root path for the data directory.
            catalog_root (str): Root path for the catalog directory.
        """
        self.individual_dataset_folder = individual_dataset_folder
        self.erddap_dataset_xml = erddap_dataset_xml

    def create_catalog_builder(self):
        builder = BasicCatalogBuilder(self.individual_dataset_folder, self.erddap_dataset_xml)
        return builder

    def generate(self):
        """
        Retrieve information about deployments from the database.

        Returns:
            list: List of dictionaries containing deployment information.
        """
        builder = self.create_catalog_builder()
        output_path = builder.build()
        return output_path
