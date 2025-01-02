import unittest
from unittest.mock import MagicMock, patch
from factory import CatalogCreatorFactory


class TestCatalogCreatorFactory(unittest.TestCase):
    @patch("factory.CatalogCreatorFactory.Deployment")  # Replace with the actual import path for Deployment
    def test_the_catalog(self, mock_deployment):
        mock_deployment_instance = MagicMock()
        mock_deployment_instance.deployment_dir = "mock_dir"
        mock_deployment_instance.activate = True
        mock_deployment_instance.name = "mock_name"

        # Mock the query.all() method to return a list of mocked deployments
        mock_deployment.query.all.return_value = [mock_deployment_instance]

        # Mock the file system to simulate the presence of dataset chunk files
        with patch("os.path.isfile", return_value=True):
            # Act: Instantiate and run the factory
            factory = CatalogCreatorFactory("mock_data_root", "mock_catalog_root")
            result = factory.generate()

        # Assert: Validate the returned object and the mocked behavior
        self.assertIsInstance(result, CatalogCreatorFactory)
        self.assertEqual(len(result.deployments_dict), 1)
        self.assertEqual(result.deployments_dict[0]["dataset_chunk_path"], "mock_data_root/mock_dir/datasets.chunk.xml")
        self.assertEqual(result.deployments_dict[0]["activate"], True)
        self.assertEqual(result.deployments_dict[0]["name"], "mock_name")





