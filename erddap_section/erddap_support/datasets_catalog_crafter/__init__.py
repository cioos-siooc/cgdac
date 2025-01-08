from .dataset_crafter import DatasetsCrafter, BasicCatalogBuilder

from .data_structure import ErddapData, Config, DatabaseConnectionProperty

"""
# This module merge individual dataset xml into one gaint datasets.xml


example:

    individuals_datasets = "individuals_datasets"
    output_dir = "output"
    erddap_data = ErddapData() # Empty for the default ERDDAP
    datasets_crafter = DatasetsCrafter(individuals_datasets, output_dir, erddap_data)
    datasets_crafter.build()
"""
