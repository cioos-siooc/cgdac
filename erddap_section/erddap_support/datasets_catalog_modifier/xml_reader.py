import os
from lxml import etree
from typing import List

class XmlReader:
    def __init__(self, xml_path):
        self._xml_path = xml_path
        self._tree = None


    @property
    def xml_path(self):
        if not os.path.isfile(self._xml_path):
            raise FileNotFoundError(f"The file '{self._xml_path}' does not exist.")
        return self._xml_path

    @property
    def tree(self):
        # Parse the XML file
        try:
            with open(self.xml_path, "r") as file:
                self._tree = etree.parse(file)
        except etree.XMLSyntaxError as e:
            raise ValueError(f"Invalid XML syntax in '{self.xml_path}': {e}")
        return self._tree

    def get_commented_variables(self) -> List[str]:
        """
        Get the list of commented-out variable names from the XML.

        :return: A list of commented-out variable names.
        """
        commented_vars = []
        # Find all comments in the XML
        for comment in self.tree.xpath("//comment()"):
            try:
                # Attempt to parse the comment as XML
                comment_tree = etree.XML(comment)
                if comment_tree.tag == "variable" and "name" in comment_tree.attrib:
                    commented_vars.append(comment_tree.attrib["name"])
            except etree.XMLSyntaxError:
                # Ignore invalid XML within the comment
                continue
        return commented_vars