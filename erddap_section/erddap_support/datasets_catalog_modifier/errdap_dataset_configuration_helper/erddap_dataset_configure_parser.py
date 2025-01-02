import re

BEFORE_DATASET_XML = 0
DATASET_XML = 1
AFTER_DATASET_XML = 3


def header_matcher(input):
    start_pattern = '<dataset\s*((type=.*)|(datasetID=.*)|(active=(\"true\"|\"false\"))\s*){3}>'
    return re.match(start_pattern, input)


def end_matcher(input):
    end_pattern = "</dataset>"
    return re.match(end_pattern, input)


def dataset_xml_parser(file_path):
    with open(file_path, 'r') as f:
        content = f.readlines()

    content_section = BEFORE_DATASET_XML
    xml_content = ""
    for c in content:
        if content_section == BEFORE_DATASET_XML:
            if header_matcher(c):
                content_section = DATASET_XML

        if content_section == DATASET_XML:
            xml_content = xml_content + "\n" + c
            if end_matcher(c):
                content_section = AFTER_DATASET_XML

    return xml_content


def dataset_xml_parser_with_comment(file_path):
    from xml.etree import ElementTree
    import xml.etree.ElementTree as ET

    class CommentedTreeBuilder(ElementTree.TreeBuilder):
        def comment(self, data):
            self.start(ElementTree.Comment, {})
            self.data(data)
            self.end(ElementTree.Comment)

    parser = ET.XMLParser(target=CommentedTreeBuilder())
    root = ET.parse(file_path, parser).getroot()
    return root
