import unittest
import os

from erddap_section.erddap_support.datasets_catalog_crafter.dataset_crafter import DatasetsCrafter
from erddap_section.erddap_support.datasets_catalog_crafter.data_structure import ErddapData


class TestDatasetsCrafter(unittest.TestCase):

    def setUp(self):
        self.datasets_data = ErddapData()
        self.current_path = os.path.dirname(__file__)
        self.individuals_datasets = 'erddap_section/erddap_support/datasets_catalog_crafter/tests/resource'
        self.output_dir = '/tmp'
        self.crafter = DatasetsCrafter(self.individuals_datasets, self.output_dir, self.datasets_data)

    def test_build(self):
        # check if it can run successful
        # need further test with ERDDAP
        result = self.crafter.build()


if __name__ == '__main__':
    unittest.main()
