import os
import glob
import json
import logging
import numpy as np
from collections import defaultdict
from lxml import etree
from netCDF4 import Dataset
from pathlib import Path
from .exceptions import ExtraAttsError

log_format_str = '%(asctime)s - %(process)d - %(name)s - %(module)s:%(lineno)d - %(levelname)s - %(message)s'
log_formatter = logging.Formatter(log_format_str)

logger = logging.getLogger(__name__)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(log_formatter)
logger.addHandler(ch)
logger.setLevel(logging.INFO)

template_dir = Path(__file__).parent.parent / "glider_dac" / "erddap" / "templates"
erddap_mapping_dict = defaultdict(lambda: 'String',
                                  {np.int8: 'byte',
                                   np.int16: 'short',
                                   np.float32: 'float',
                                   np.float64: 'double'})


def variable_sort_function(element):
    """
    Sorts by ERDDAP variable destinationName, or by
    sourceName if the former is not available.
    """
    elem_list = (element.xpath("destinationName/text()") or
                 element.xpath("sourceName/text()"))
    # sort case insensitive
    try:
        return elem_list[0].lower()
    # If there's no source or destination name, or type is not a string,
    # assume a blank string.
    # This is probably not valid in datasets.default.xml, but we have to do something.
    except (IndexError, AttributeError):
        return ""


def qc_var_snippets(required_vars, qc_var_types, dest_var_remaps):
    var_list = []
    for req_var in required_vars:
        # If the required non-QARTOD QC variable isn't already defined,
        # then supply a set of default attributes.
        if req_var not in qc_var_types['gen_qc']:
            flag_atts = """
                <att name="flag_values" type="byteList">0 1 2 3 4 5 6 7 8 9</att>
                <att name="flag_meanings">no_qc_performed good_data probably_good_data bad_data_that_are_potentially_correctable bad_data value_changed interpolated_value missing_value</att>
                <att name="_FillValue" type="byte">-127</att>
                <att name="valid_min" type="byte">0</att>
                <att name="valid_max" type="byte">9</att>
            """
        else:
            flag_atts = ""

        var_str = f"""
        <dataVariable>
            <sourceName>{req_var}</sourceName>
            <destinationName>{dest_var_remaps.get(req_var, req_var)}</destinationName>
            <dataType>byte</dataType>
            <addAttributes>
                <att name="ioos_category">Quality</att>
                <att name="long_name">{dest_var_remaps.get(req_var, req_var).replace('_qc', '')} Variable Quality Flag</att>
                {flag_atts}
            </addAttributes>
        </dataVariable>"""
        var_list.append(etree.fromstring(var_str))

    for qartod_var in qc_var_types["qartod"]:
        # if there are QARTOD variables defined, populate them

        if "_FillValue" not in qc_var_types['qartod'][qartod_var]:
            fill_value_snippet = '<att name="_FillValue" type="byte">-127</att>'
        else:
            fill_value_snippet = ""
        # all qartod variables should have _FillValue, missing_value,
        # flag_values, and flag_meanings defined

        qartod_snip = f"""
       <dataVariable>
           <sourceName>{qartod_var}</sourceName>
           <destinationName>{qartod_var}</destinationName>
           <dataType>byte</dataType>
           <addAttributes>
              <att name="ioos_category">Quality</att>
              <att name="flag_values" type="byteList">1 2 3 4 9</att>
              <att name="flag_meanings">GOOD NOT_EVALUATED SUSPECT BAD MISSING</att>
              <att name="valid_min" type="byte">1</att>
              <att name="valid_max" type="byte">9</att>
              {fill_value_snippet}
           </addAttributes>
       </dataVariable>
       """
        var_list.append(etree.fromstring(qartod_snip))

    for gen_qc_var in qc_var_types["gen_qc"]:
        # if we already have this variable as part of required QC variables,
        # skip it.
        if gen_qc_var in required_vars:
            continue
        # assume byte for data type as it is required
        gen_qc_snip = f"""
            <dataVariable>
               <sourceName>{gen_qc_var}</sourceName>
               <dataType>byte</dataType>
               <addAttributes>
                  <att name="ioos_category">Quality</att>
               </addAttributes>
            </dataVariable>
            """
        var_list.append(etree.fromstring(gen_qc_snip))

    return var_list


def add_erddap_var_elem(var):
    """
    Adds an unhandled standard name variable to the ERDDAP datasets.default.xml
    """
    dvar_elem = etree.Element('dataVariable')
    source_name = etree.SubElement(dvar_elem, 'sourceName')
    source_name.text = var.name
    data_type = etree.SubElement(dvar_elem, 'dataType')
    if var.dtype == str:
        data_type.text = "String"
    else:
        data_type.text = erddap_mapping_dict[var.dtype.type]
    add_atts = etree.SubElement(dvar_elem, 'addAttributes')
    ioos_category = etree.SubElement(add_atts, 'att', name='ioos_category')
    ioos_category.text = "Other"
    return dvar_elem


def add_extra_attributes(tree, identifier, mod_atts):
    """
    Adds extra user-defined attributes to the ERDDAP datasets.default.xml.
    Usually sourced from the extra_atts.json file, this function modifies an
    ERDDAP xml datasets tree.   `identifier` should either be "_global_attrs"
    to modify a global attribute, or the name of a variable in the dataset
    to modify a variable's attributes.  `mod_atts` is a dict with the attributes
    to create or modify.
    """
    if identifier == '_global_attrs':
        xpath_expr = "."
    else:
        xpath_expr = "dataVariable[sourceName='{}']".format(identifier)
    subtree = tree.find(xpath_expr)

    if subtree is None:
        logger.warning("Element specified By XPath expression {} not found, skipping".format(xpath_expr))
        return

    add_atts_found = subtree.find('addAttributes')
    if add_atts_found is not None:
        add_atts_elem = add_atts_found
    else:
        add_atts_elem = subtree.append(etree.Element('addAttributes'))
        logger.info('Added "addAttributes" to xpath for {}'.format(xpath_expr))

    for att_name, value in mod_atts.items():
        # find the attribute
        found_elem = add_atts_elem.find(att_name)
        # attribute exists, update current value
        if found_elem is not None:
            found_elem.text = value
        # attribute
        else:
            new_elem = etree.Element('att', {'name': att_name})
            new_elem.text = value
            add_atts_elem.append(new_elem)


def check_for_qc_vars(nc):
    """
    Checks for general gc variables and QARTOD variables by naming conventions.
    Returns a dict with both sets of variables as keys, and their attributes
    as values.
    """
    qc_vars = {'gen_qc': {}, 'qartod': {}}
    for var in nc.variables:
        if var.endswith('_qc'):
            qc_vars['gen_qc'][var] = nc.variables[var].ncattrs()
        elif var.startswith('qartod'):
            qc_vars['qartod'][var] = nc.variables[var].ncattrs()
    return qc_vars


def get_latest_nc_file(root):
    '''
    Returns the lastest netCDF file found in the directory

    :param str root: Root of the directory to scan
    '''
    list_of_files = glob.glob('{}/*.nc'.format(root))
    if not list_of_files:  # Check for no files
        return None
    return max(list_of_files, key=os.path.getctime)
