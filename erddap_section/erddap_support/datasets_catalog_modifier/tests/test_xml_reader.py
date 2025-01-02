import unittest
from erddap_section.erddap_support.datasets_catalog_modifier.xml_reader import XmlReader  # Replace `your_module` with your module name

class TestXMLVariableReader(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Example XML content for tests
        cls.xml_content_with_comments = """<?xml version="1.0"?>
        <root>
            <!-- This is a comment -->
            <!-- <variable name="commented_out_var">12345</variable> -->
            <variable name="active_var">67890</variable>
        </root>
        """

        cls.xml_content_without_comments = """<?xml version="1.0"?>
        <root>
            <variable name="active_var">67890</variable>
        </root>
        """

        cls.xml_invalid_content = """<?xml version="1.0"?>
        <root>
            <variable name="active_var">67890</variable>
        """

        cls.valid_file_path = "valid.xml"
        cls.invalid_file_path = "invalid.xml"

    def setUp(self):
        # Write example XML content to temporary files
        with open(self.valid_file_path, "w") as f:
            f.write(self.xml_content_with_comments)

        with open(self.invalid_file_path, "w") as f:
            f.write(self.xml_invalid_content)

    def test_read_active_variables(self):
        """Test reading active variables from an XML file."""
        reader = XmlReader(self.valid_file_path)
        active_vars = reader.get_active_variables()
        self.assertIn("active_var", active_vars)

    def test_read_commented_variables(self):
        """Test reading commented-out variables from an XML file."""
        reader = XmlReader(self.valid_file_path)
        commented_vars = reader.get_commented_variables()
        self.assertIn("commented_out_var", commented_vars)

    def test_invalid_xml_handling(self):
        """Test handling of invalid XML."""
        with self.assertRaises(Exception):
            XmlReader(self.invalid_file_path)

    def test_file_not_found(self):
        """Test handling of non-existent XML files."""
        with self.assertRaises(FileNotFoundError):
            XmlReader("non_existent.xml")

    def tearDown(self):
        # Clean up files created during the tests
        import os
        os.remove(self.valid_file_path)
        os.remove(self.invalid_file_path)

if __name__ == "__main__":
    unittest.main()