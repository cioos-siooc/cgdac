from xml.etree.ElementTree import (
    fromstring,
    ElementTree,
    Element,
    tostring,

)
from lxml import etree
from lxml.doctestcompare import strip


def xml_element_to_dict(element, read_comments=False):
    """
    Recursively converts an XML element and its structure into a dictionary.

    :param element: The XML element to convert.
    :return: A dictionary representation of the XML element.
    """
    result = {}

    # Add element attributes if they exist
    if element.attrib:
        result.update(element.attrib)

    # Add element children
    for child in element:

        if isinstance(child, etree._Comment) and read_comments:
            if "addAttributes" not in result:
                result["addAttributes"] = {}
                result["addAttributes"]["att_in_comments"] = []
            comment_text = child.text.strip()

            # Reconstruct the comment as valid XML
            if not comment_text.startswith("<"):
                comment_text = f"<{comment_text}>"
            if not comment_text.endswith(">"):
                comment_text = f"{comment_text}</>"
            try:
                # Parse the reconstructed comment
                comment_root = etree.XML(comment_text)
                if comment_root.tag == "sourceAttributes":
                    for att in comment_root.xpath("./att"):
                        res = dict(att.attrib)
                        if att.text and att.text.strip():
                            res['text'] = att.text.strip()
                        result["addAttributes"]["att_in_comments"].append(res)
            except etree.XMLSyntaxError as e:
                print(f"Failed to parse comment: {comment_text}, error: {e}")
        if not isinstance(child, etree._Comment):
            child_dict = xml_element_to_dict(child)

            if child.tag not in result:
                result[child.tag] = child_dict
            else:
                # Handle multiple children with the same tag by converting to a list
                if not isinstance(result[child.tag], list):
                    result[child.tag] = [result[child.tag]]
                result[child.tag].append(child_dict)

    # Add element text if it exists and is not whitespace
    if element.text and element.text.strip():
        if result:
            result["text"] = element.text.strip()
        else:
            return element.text.strip()

    return result


class ERDDAPDatasetXMLEditor:

    def __init__(self, xml):
        self.xml = xml
        self._tree = None
        self._root = None
        self._add_attr_index = None

    @property
    def root(self):
        if self._root is None:
            self._root = self.tree
        return self._root

    @property
    def tree(self):
        if self._tree is None:
            if isinstance(self.xml, str):
                self._tree = etree.XML(self.xml)
            else:
                with open(self.xml, 'r', encoding='utf-8') as file:
                    xml_content = file.read()
                self._tree = etree.XML(xml_content)
        return self._tree

    @staticmethod
    def _get_data_variable_add_attributes(data_variable_element):
        for sub in data_variable_element:
            if sub.tag == "addAttributes":
                return sub

    @staticmethod
    def create_new_att_element(name, text):
        new_element = etree.Element("att", attrib={'name': name})
        new_element.text = text
        new_element.tail = '\n\n   '
        return new_element

    @staticmethod
    def update_att_element_text(ele, name, text):
        UPDATED = True
        attrs = ele.attrib
        if attrs["name"] == name:
            ele.text = text
            return UPDATED
        else:
            return not UPDATED

    def set_add_attribute(self, ele, name, new_attr_text):
        for sub in ele:
            if self.update_att_element_text(sub, name, new_attr_text):
                break
        else:
            new_element = self.create_new_att_element(name, new_attr_text)
            ele.append(new_element)

    @staticmethod
    def _set_header(ele, name, content):
        if type(content) is int:
            content = str(content)
        ele.set(name, content)

    @staticmethod
    def _get_header(ele):
        return ele.attrib

    @staticmethod
    def sub_element_text_change_by_tag(ele, tag, new_text):
        for sub in ele:
            if sub.tag == tag:
                sub.text = new_text

    def set_header(self, name, content):
        self._set_header(self.root, name, content)

    def get_header(self):
        return self._get_header(self.root)

    def get_all_attr(self):
        """
        here is example for the target code snippet
        <reloadEveryNMinutes>10080</reloadEveryNMinutes> # Want
        <fileDir>/datasets/</fileDir> # Want
        <!-- sourceAttributes>
            <att name="_NCProperties">version=2,netcdf=4.9.3-development,hdf5=1.12.2</att>
            <att name="acknowledgment">Funding provided by Ocean Frontier Institute Module O &quot;Transforming Ocean Observations&quot;.</att>
            <att name="cdm_dataType">profile</att>
            <att name="wmo_id">6801509</att>
        </sourceAttributes -->
        <!-- Please specify the actual cdm_data_type (TimeSeries?) and related info below, for example...
            <att name="cdm_timeseries_variables">station_id, longitude, latitude</att>
            <att name="subsetVariables">station_id, longitude, latitude</att>
        -->
        """
        _attr = {}
        for child in self.root:
            t = child.tag
            te = child.text
            if t != "addAttributes" and t != "dataVariable" and type(t) is str:
                _attr[t] = te
        return _attr

    def get_unit(self, read_comments=False):
        res = {}

        for index, child in self._get_element_by_tag_generator("dataVariable"):
            unit = None
            for sub in child:
                if read_comments and isinstance(sub, etree._Comment):
                    comment_text = sub.text.strip()
                    if not comment_text.startswith("<"):
                        comment_text = f"<{comment_text}>"
                    if not comment_text.endswith(">"):
                        comment_text = f"{comment_text}</>"
                    comment_root = etree.XML(comment_text)
                    if comment_root.tag == "sourceAttributes":
                        for att in comment_root.xpath("./att"):
                            name = att.attrib.get("name")
                            if name == "units":
                                res[source_name] = att.text
                # if a value exist in the actully content and in comment. Always use the value not in the comment.
                if sub.tag == "sourceName":
                    source_name = sub.text
                if sub.tag == "addAttributes":
                    for ssub in sub:
                        attrib = ssub.attrib
                        if attrib['name'] == "units":
                            unit = ssub.text
                if unit and source_name:
                    res[source_name] = unit
        return res

    def add_unit(self, attr_name, unit_value):
        self.set_data_variable_add_attribute(attr_name, 'units', unit_value)

    def set_erddap_config(self, tag, text):
        # Add or Change the value of erddap config
        if type(text) is int:
            text = str(text)
        for child in self.root:
            if child.tag == tag:
                child.text = text
                break
        else:
            new_element = etree.Element(tag)
            new_element.text = text
            new_element.tail = '\n\n   '
            self.root.insert(0, new_element)

    def remove_dataset_config(self, name):
        attr = self.root.find(name)
        self.root.remove(attr)


    def _data_variable_merge(self, res, read_comments):
        addAttributes = res["addAttributes"]
        if read_comments and isinstance(addAttributes, list):
            new_add_attributes = {}
            att_in_comment = addAttributes[0]["att_in_comments"]
            for value in att_in_comment:
                new_add_attributes[value["name"]] = value
            att = addAttributes[1]["att"]
            if isinstance(att, list):
                for value in att:
                    new_add_attributes[value["name"]] = value
            else:
                new_add_attributes[att["name"]] = att
        else:
            att = addAttributes["att"]
            new_add_attributes = {}
            if isinstance(att, list):
                for value in att:
                    new_add_attributes[value["name"]] = value
            else:
                new_add_attributes[att["name"]] = att

        res["addAttributes"] = new_add_attributes
        return res


    def get_all_data_variables(self, read_comments=False):
        data_variables_list = []
        for index, child in enumerate(self.root.xpath("dataVariable")):
            res = xml_element_to_dict(child, read_comments=read_comments)

            res = self._data_variable_merge(res, read_comments)
            data_variables_list.append(res)
        return data_variables_list


    def get_all_global_attr(self, read_comments=False):
        """
        Use this function to retrieve all global added attributes.

        For example, it returns the names of the attributes as a list:
        <!-- sourceAttributes>
        <att name="acknowledgment">acknowledgment</att> #  want if read_comments is true
        <att name="cdm_dataType">profile</att> #  want if read_comments is true
        <att name="wmo_id">6801509</att> #  want if read_comments is true
        </sourceAttributes -->
        <!-- Please specify the actual cdm_data_type (TimeSeries?) and related info below, for example... # no want
        <att name="cdm_timeseries_variables">station_id, longitude, latitude</att> # no want
        <att name="subsetVariables">station_id, longitude, latitude</att> # no want
        -->
        <addAttributes>
        <att name="cdm_data_type">Point</att> # want
        <att name="Conventions">CF-1.10, COARDS, ACDD-1.3</att> # want
        </addAttributes>
        """
        _add_attr = {}
        added_attr_element = self._get_added_attr_section()

        for child in added_attr_element:
            attrib = child.attrib
            te = child.text
            _add_attr[attrib["name"]] = te

        if read_comments:
            # Process commented attributes
            for data_variable in self.root.xpath("//dataset"):
                for child in data_variable:
                    if isinstance(child, etree._Comment):  # Check if the child is a comment
                        comment_text = child.text.strip()

                        # Reconstruct the comment as valid XML
                        if not comment_text.startswith("<"):
                            comment_text = f"<{comment_text}>"
                        if not comment_text.endswith(">"):
                            comment_text = f"{comment_text}</>"

                        try:
                            # Parse the reconstructed comment
                            comment_root = etree.XML(comment_text)
                            if comment_root.tag == "sourceAttributes":
                                for att in comment_root.xpath("./att"):
                                    name = att.attrib.get("name")
                                    value = att.text
                                    _add_attr[name] = value
                        except etree.XMLSyntaxError as e:
                            print(f"Failed to parse comment: {comment_text}, error: {e}")

        return _add_attr

    def _get_element_by_tag_generator(self, tag):
        for index, child in enumerate(self.root):
            if child.tag == tag:
                yield index, child

    def get_element_by_tag_generator_with_comment(self, tag):
        for index, child in enumerate(self.root.xpath("dataVariable")):
            if child.tag == tag:
                yield index, child

    def _get_added_attr_section(self):
        added_attr_element = None
        if self._add_attr_index is None:
            for index, child in enumerate(self.root):
                t = child.tag
                if t == "addAttributes":
                    self._add_attr_index = index
                    self._add_attr_index = index
                    added_attr_element = child
        else:
            added_attr_element = self.root[self._add_attr_index]
        return added_attr_element

    def _added_new_element_to_attr_section(self, name, text, added_attr_element):
        new_element = etree.Element("att", attrib={'name': name})
        new_element.text = text
        new_element.tail = '\n\n   '
        added_attr_element.append(new_element)

    def _text_update_for_added_attr(self, name, text, child):
        UPDATED = True
        attrs = child.attrib
        if attrs["name"] == name:
            child.text = text
            return UPDATED
        else:
            return not UPDATED

    def set_added_global_variable(self, name, text):
        added_attr_element = self._get_added_attr_section()
        if added_attr_element:
            for child in added_attr_element:
                if self._text_update_for_added_attr(name, text, child):
                    break
            else:
                self._added_new_element_to_attr_section(name, text, added_attr_element)

    def remove_global_variable(self, name):
        added_attr_element = self._get_added_attr_section()
        for child in added_attr_element:
            attrs = child.attrib
            if attrs["name"] == name:
                added_attr_element.remove(child)
                break


    def write(self, file_path):
        if not self._tree:
            self.tree
        tree = etree.ElementTree(self._tree)
        # Write to the file
        with open(file_path, "wb") as file:
            tree.write(file, pretty_print=True, xml_declaration=False, encoding="UTF-8")

    def to_string(self):
        return tostring(self.root, encoding='unicode', method='xml')

    def _find_data_variable_by_source_name(self, source_name):
        for index, child in self._get_element_by_tag_generator("dataVariable"):
            for sub in child:
                if sub.tag == "sourceName":
                    if sub.text == source_name:
                        return index, child
                    else:
                        break
        else:
            return None, None
    #########################################
    # functions below is for the data variables
    def remove_data_variable(self, source_name):
        index, child = self._find_data_variable_by_source_name(source_name)
        if child:
            self._root.remove(child)

    def edit_data_variable_destination_name(self, source_name, new_destination_name):
        index, child = self._find_data_variable_by_source_name(source_name)
        self.sub_element_text_change_by_tag(child, "destinationName", new_destination_name)

    def edit_data_variable_data_type(self, source_name, new_data_type):
        index, child = self._find_data_variable_by_source_name(source_name)
        self.sub_element_text_change_by_tag(child, "dataType", new_data_type)

    def set_data_variable_add_attribute(self, source_name, attr_name, new_attr_text):
        index, child = self._find_data_variable_by_source_name(source_name)
        if child:
            add_attribute_element = self._get_data_variable_add_attributes(child)
            self.set_add_attribute(add_attribute_element, attr_name, new_attr_text)
        else:
            raise Exception("Unable to find the data variable")

    def remove_data_variable_add_attribute(self, source_name, attr_name):
        index, child = self._find_data_variable_by_source_name(source_name)
        add_attribute_element = self._get_data_variable_add_attributes(child)
        for sub in add_attribute_element:
            attrib_name = sub.attrib["name"]
            if attrib_name == attr_name:
                add_attribute_element.remove(sub)
                break


    def add_data_variable(self, source_name, destination_name, data_type, add_attributes_dict):
        """
        Add a new 'dataVariable' element to the end of the root with nested elements.

        :param source_name: Value for 'sourceName' element
        :param destination_name: Value for 'destinationName' element
        :param data_type: Value for 'dataType' element
        :param attributes: Dictionary of attributes for 'addAttributes'
        """
        data_variable = etree.Element("dataVariable")
        data_variable.tail = '\n'
        data_variable.text = '\n\t\t'
        # Add child elements

        sourceName = etree.SubElement(data_variable, "sourceName")
        sourceName.text = source_name
        sourceName.tail = '\n\t\t'
        destinationName = etree.SubElement(data_variable, "destinationName")
        destinationName.text = destination_name
        destinationName.tail = '\n\t\t'
        dataType = etree.SubElement(data_variable, "dataType")
        dataType.text = data_type
        dataType.tail = '\n\t\t'

        # Add addAttributes element with nested att elements
        add_attributes = etree.SubElement(data_variable, "addAttributes")
        add_attributes.text = '\n\t\t\t'
        add_attributes.tail = '\n\t\t'
        for index, value in enumerate(add_attributes_dict):
            name = value["name"]
            attr_type = value.get("type")
            attr_value = value.get("value")
            if attr_type:
                att = etree.SubElement(add_attributes, "att", name=name, type=attr_type)
            else:
                att = etree.SubElement(add_attributes, "att", name=name)
            att.text = attr_value
            if len(add_attributes_dict)-1 == index:
                att.tail = '\n\t\t'
            else:
                att.tail = '\n\t\t\t'
        if len(self.root):
            self.root[-1].tail = '\n\t'
        self.root.append(data_variable)




#########################################
