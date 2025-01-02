def read_xml_as_string(file_path):
    """
    Read an XML file into a string.

    :param file_path: Path to the XML file.
    :return: The contents of the file as a string.
    """
    with open(file_path, "r", encoding="utf-8") as file:
        xml_string = file.read()
    return xml_string

