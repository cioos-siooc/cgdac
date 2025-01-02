ERRDAP dataset configuration editor

errdap_dataset_xml can help you edit ERRDAP configuration by Python easily!

usage:

dataset_xml_parser  can help you read ERRDAP dataset xml file and return str

ERDDAPDatasetXMLEditor can help edit the ERRDAP datast xml

Errdap configuration contain 4 sections

those were header, database behaviour, dataset global attribute, variables attribute

change header:
set_header
get_header

database behaviour:
set_attr
get_all_attr
remove_attr(name)

dataset global attribute:
get_all_added_attr()
set_added_attr(name, text)
remove_added_attr(name)

variables attribute:
remove_data_variable(source_name)
edit_data_variable_destination_name(source_name, new_destination_name)
edit_data_variable_data_type(source_name, new_data_type)
set_data_variable_add_attribute(source_name, attr_name, new_attr_text)
remove_data_variable_add_attribute(source_name, attr_name)