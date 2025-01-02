import os
import glob
import logging
import fileinput
from common import log_formatter
from datetime import datetime, timezone
from shutil import copy

from .errdap_dataset_chunk import ErddapCatalogChunkCreator

logger = logging.getLogger(__name__)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(log_formatter)
logger.addHandler(ch)
logger.setLevel(logging.INFO)


class BaseCreator:
    """
    Base generator Class
    note: try to note bring database object into creator class.
    it will be benefit to the unit test and potential database swap
    """

    def create(self):
        raise NotImplementedError


def get_latest_nc_file(full_path):
    '''
    Returns the lastest netCDF file found in the directory

    :param str root: Root of the directory to scan
    '''
    list_of_files = glob.glob('{}/*.nc'.format(full_path))
    if not list_of_files:  # Check for no files
        return None
    return max(list_of_files, key=os.path.getmtime)

class IndividualCatalogGenerator(BaseCreator):


    def __init__(self, deployment_dict, config):
        """
            Initializes the IndividualCatalogGenerator.

            :param deployment_dict: Dictionary containing deployment-specific information.
            :param config: Configuration dictionary for catalog generation.
            :param data_root: The root path of the data folder
        """
        self.deployment_dict = deployment_dict
        self.data_chuck_path = deployment_dict["data_chuck_path"]
        self.data_root = deployment_dict["data_root"]
        self.last_process_time_path = deployment_dict["last_process_time_path"]
        self.dataset_id = self.deployment_dict["dataset_ID"]
        self.selected_file = self.deployment_dict["latest_file"]
        self.deployment_dir = self.deployment_dict["deployment_dir"]
        self.config = config

    def create(self):
        latest_file = get_latest_nc_file(os.path.join(self.data_root, self.deployment_dir))
        self.selected_file = latest_file
        if self.selected_file:
            try:
                logger.info("Building ERDDAP catalog chunk for {}".format(self.deployment_dir))

                chunk_creator = ErddapCatalogChunkCreator(self.deployment_dict, self.selected_file, self.dataset_id,
                                                          self.config)
                chunk_creator.create()

            except Exception as e:
                logger.exception("Error: creating dataset chunk for {}".format(self.deployment_dir))
            else:
                try:
                    # with open(self.data_chuck_path, 'w') as f:
                    #     f.write(chunk_contents)

                    with open(self.last_process_time_path, 'w') as f:
                        f.write(str(datetime.now(tz=timezone.utc)))
                    return True
                except:
                    logger.exception("Could not write ERDDAP dataset snippet XML file {}".format(self.data_chuck_path))

    def file_selection(self):
        return get_latest_nc_file(os.path.join(self.data_root, self.deployment_dir))

class CatalogGenerator(BaseCreator):
    def __init__(self, data_root, deployment_dicts, head_path, tail_path, catalog_root):
        self.deployment_dicts = deployment_dicts

        self.data_root = data_root
        self.catalog_root = catalog_root
        self.head_path = head_path
        self.tail_path = tail_path
        self.ds_tmp_path = os.path.join(self.catalog_root, 'datasets.default.xml.tmp')
        self.ds_bak_path = os.path.join(self.catalog_root, 'datasets.default.xml.bak')
        self.ds_path = os.path.join(self.catalog_root, 'datasets.default.xml')

    def catalog_chunk_validation(self, chunk_path):
        # todo: implement a way valid the chunk before add it to tmp xml
        return True

    def create(self):
        logger.info("Start generate new datasets.default.xml: {}".format(self.ds_path))
        try:
            with open(self.ds_tmp_path, 'w') as f:
                for line in fileinput.input([self.head_path]):
                    f.write(line)
                # for each deployment, get the dataset chunk
                for deployment_dict in self.deployment_dicts:
                    # First check that a chunk exists
                    dataset_chunk_path = deployment_dict["dataset_chunk_path"]
                    activate = deployment_dict["activate"]
                    name = deployment_dict["name"]
                    if os.path.isfile(dataset_chunk_path) and activate and self.catalog_chunk_validation(
                            dataset_chunk_path):
                        for line in fileinput.input([dataset_chunk_path]):
                            f.write(line)
                    else:
                        f.write('\n<dataset type="EDDTableFromNcFiles" datasetID="{}" active="false"></dataset>'.format(
                            name))

                for line in fileinput.input([self.tail_path]):
                    f.write(line)
            # now try moving the file to update datasets.default.xml
            if os.path.exists(self.ds_path):
                copy(self.ds_path, self.ds_bak_path)
            os.rename(self.ds_tmp_path, self.ds_path)
        except OSError as e:
            logger.exception("Could not write to datasets.default.xml {}".format(e))
        logger.info("Wrote {} from {} deployments".format(self.ds_path, len(self.deployment_dicts)))
