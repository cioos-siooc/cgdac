import os
import sys
import argparse
from glider_dac.app import app


def get_config():
    return {
    "GENERATE_DATASETS_XML_PROGRAM_PATH": app.config["GENERATE_DATASETS_XML_PROGRAM_PATH"],
    "XML_TEMP_FOLDER": app.config["XML_TEMP_FOLDER"]
}

def auto_handle(data_dir, catalog_dir):
    with app.app_context():
        from .manager import ErddapCatalogManager
        sys.exit(ErddapCatalogManager(data_dir, catalog_dir, get_config()).run())


'''
build_erddap_catalog.py priv_erddap ./data/data/priv_erddap ./data/catalog ./glider_dac/erddap/templates/private
'''
parser = argparse.ArgumentParser()
parser.add_argument('data_dir', help='The directory where netCDF files are read from')
parser.add_argument('catalog_dir', help='The full path to where the datasets.default.xml will reside')
parser.add_argument('auto', action='store_true', help='auto handle the deployment catalogs creations')
parser.add_argument('-f', '--force', action="store_true", help="Force processing ALL deployments")

args = parser.parse_args()

catalog_dir = os.path.realpath(args.catalog_dir)
data_dir = os.path.realpath(args.data_dir)
force = args.force
auto = args.auto

if auto:
    auto_handle(data_dir, catalog_dir)
