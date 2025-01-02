# This Module revise the draft of the datasets catalog chunk
import os.path
from xml.etree.ElementTree import (
    fromstring,
    ElementTree,
    Element,
    tostring,
    SubElement
)
from datetime import datetime
from erddap_catalog_chunk_editor.dataset_xml_editor import ERDDAPDatasetXMLEditor

TRAJECTORY = "trajectory"


class ErddapGliderDatasetXmlAdjuster(ERDDAPDatasetXMLEditor):
    """
    The output of the GenerateDatasetsXml is draft
    we need to edit the output to make it better

    quote from erddap docs
    DISCLAIMER:
    THE CHUNK OF datasets.default.xml MADE BE GenerateDatasetsXml
     ISN'T PERFECT. YOU MUST READ AND EDIT THE XML BEFORE
    USING IT IN A PUBLIC ERDDAP. GenerateDatasetsXml RELIES
    ON A LOT OF RULES-OF-THUMB WHICH AREN'T ALWAYS CORRECT.
    YOU ARE RESPONSIBLE FOR ENSURING THE CORRECTNESS OF THE
    XML THAT YOU ADD TO ERDDAP'S datasets.default.xml FILE.
    """

    def __init__(self, xml_str: str, dataset_id: str,
                 erddap_server_nc_folder_path: str,
                 dataset_meta,
                 output_path: str,
                 deployment_meta = None):
        super().__init__(xml_str)
        self.dataset_meta = dataset_meta
        self.datasets_id = dataset_id
        self.erddap_server_nc_folder_path = erddap_server_nc_folder_path
        self.deployment_meta =deployment_meta
        self.output_path = output_path

    def adjust(self):
        self.update_catalog_id(self.datasets_id)
        self.dataset_meta.set_title(self.datasets_id)
        self.update_catalog_general()
        self.adjust_cdm_profile_variable(self.get_all_added_attr())
        self.apply_convention_standards()
        self.update_global_attribute()
        self.update_data_variables()
        self.write(self.output_path)

    def apply_convention_standards(self):
        # This is the function for subclass to overwrite
        ...

    def adjust_cdm_profile_variable(self, added_attr):
        if "cdm_data_type" in added_attr and added_attr["cdm_data_type"] == "TrajectoryProfile":
            self.set_added_attr('cdm_profile_variables', 'profile_id, time, latitude, longitude')
            self.set_added_attr('cdm_trajectory_variables', 'trajectory')

    def update_catalog_id(self, dataset_id):
        self.set_header("datasetID", dataset_id)

    def update_catalog_general(self):
        # Since pipeline would trigger the Hard Flag file, reload min was set very high.
        # 40320 mins is 28 days
        self.set_attr("reloadEveryNMinutes", 40320)
        # set the updateEveryNMillis as 0, means turn off the this feature
        self.set_attr("updateEveryNMillis", 0)
        # we want user can view the nc files as well
        self.set_attr("accessibleViaFiles", 'True')
        target_nc = self.erddap_server_nc_folder_path
        nc_folder = os.path.dirname(target_nc)
        self.set_attr("fileDir", nc_folder)

        # ERDDAP doc: remove since those feature was deprecated
        # Adding try catch for now
        try:
            self.remove_attr('preExtractRegex')
        except TypeError:
            pass
        try:
            self.remove_attr('postExtractRegex')
        except TypeError:
            pass
        try:
            self.remove_attr('extractRegex')
        except TypeError:
            pass
        try:
            self.remove_attr('columnNameForExtract')
        except TypeError:
            pass

    def fix_for_ceotr_dataset(self, added_attr):
        if "publisher_name" in added_attr and "CEOTR" in added_attr:
            self.set_added_attr('title', self.datasets_id)

    def add_update_global_attribute(self):
        global_meta_update = self.dataset_meta.get_global_add_update()
        for variable_name, content in global_meta_update.items():
            self.set_added_attr(variable_name, content)

        #
        # self.set_added_attr('cdm_profile_variables', 'profile_id, time, latitude, longitude')
        # self.set_added_attr('cdm_trajectory_variables', 'trajectory')
        # self.set_added_attr('Metadata_Conventions', 'CF-1.6')
        # self.set_added_attr('title', self.erddap_dataset_title)
        # try:
        #     # Hide the source file from ERRDAP meta page
        #     self.set_added_attr('source_file', "null")
        # except TypeError:
        #     pass

    def remove_global_attribute(self):
        global_meta_update = self.dataset_meta.get_global_remove()
        for variable_name in global_meta_update:
            self.remove_added_attr(variable_name)

        # self.remove_added_attr('testOutOfDate')
        # self.remove_added_attr('subsetVariables')

    def update_global_attribute(self):
        """
        quote from erddap doc
        If you don't like a sourceAttribute,
         overwrite it by adding an addAttribute
         with the same name but a different value
        (or no value, if you want to remove it).
        """
        """
        From erddap document
        The dataset MUST include the globalAttribute
        cdm_profile_variables, where the value is a comma-separated
        list of the variables which have the information about each profile.
        For a given profile, the values of these variables MUST be constant.
        For example, <att name="cdm_profile_variables">profile_number,time,latitude,longitude</att>
        The list MUST include the cf_role=profile_id variable and all other variables with information
        about the profile, and time, latitude and longitude. The list will never include altitude, depth,
        or any observation variables. 
        """
        self.add_update_global_attribute()
        self.remove_global_attribute()

    def update_data_variables(self):
        ...


class DataVariable:
    def __init__(self, parent_root, source_name, destination_name, data_type):
        self.parent_root = parent_root
        self._root = None
        self.sourceName = source_name
        self.destinationName = destination_name
        self.dataType = data_type
        self._attribute = None
        self.add_attributes_dict = dict()

    def _build_default_attribute(self):
        return SubElement(self.root, "addAttributes")

    @property
    def attribute(self):
        if self._attribute is None:
            self._attribute = self._build_default_attribute()
        return self._attribute

    @property
    def root(self):
        if self._root is None:
            self._root = SubElement(self.parent_root, 'dataVariable')
            self._root.tail = '\n\n   '
        return self._root

    def build_add_attribute(self):
        for key, content in self.add_attributes_dict.items():
            element = SubElement(self.attribute, "att", {
                "name": key
            })
            element.text = content
            element.tail = '\n\n   '

    def add_attributes(self, name, content):
        self.add_attributes_dict[name] = content

    def build_source_name(self):
        self._build_sub_element("sourceName")

    def build_destination_name(self):
        self._build_sub_element("destinationName")

    def build_data_type(self):
        self._build_sub_element("dataType")

    def _build_sub_element(self, element_name):
        element = SubElement(self.root, element_name)
        element.text = getattr(self, element_name)
        element.tail = '\n\n   '

    def build(self):
        self.build_source_name()
        self.build_destination_name()
        self.build_data_type()
        self.build_add_attribute()


class OceanGliderStandardDatasetXmlAdjuster(ErddapGliderDatasetXmlAdjuster):
    """
    This class review the dataset xml chunk and add some global variables and attributes that is required by Ocean Glider

    """

    def add_new_variable(self, source_name, destination_name, data_type, attrs):
        if not any(destination_name.lower() == val.lower() for val in self.dataset_meta.variables):
            new_data_variable = DataVariable(self._root, source_name, destination_name, data_type)
            if attrs:
                for key, content in attrs.items():
                    new_data_variable.add_attributes(key, content)
            new_data_variable.build()

    def add_feature_type(self):
        """
        reference: https://oceangliderscommunity.github.io/OG-format-user-manual/
        featureType
        Description of a single feature with this discrete sampling geometry
        mandatory
        trajectory

        """

        self.set_added_attr('featureType', TRAJECTORY)

    def add_cdm_data_type(self):
        self.set_added_attr('cdm_data_type', TRAJECTORY)

    def add_cdm_trajectory_variables(self):
        """
        reference: https://coastwatch.pfeg.noaa.gov/erddap/download/setupDatasetsXml.html#cdmTrajectory
        """
        self.set_added_attr('cdm_trajectory_variables', TRAJECTORY)

    def remove_other_cdm_variable(self):
        # remove cdm_profile_variables
        # from ERDDAP: For cdm_data_type=Trajectory, the global attribute cdm_profile_variables must *not* be set.

        self.remove_added_attr('cdm_profile_variables')


    def remove_other_cf_role(self):
        #  from ERDDAP: For cdm_data_type=Trajectory, no variable should have cf_role=profile_id
        for val, content in self.dataset_meta.variables.items():
            if 'cf_role' in content and content['cf_role'] == "profile_id":
                self.set_data_variable_add_attribute(val, 'cf_role', 'null')


    def apply_global_variables(self):
        self.add_feature_type()
        self.add_cdm_data_type()
        self.add_cdm_trajectory_variables()
        self.remove_other_cdm_variable()
        self.remove_other_cf_role()

    def add_deployment_time(self):
        """
        <dataVariable>

        <sourceName>={the deployment timestamp}</sourceName>

        <destinationName>DEPLOYMENT_TIME</destinationName>

        <dataType>double</dataType>


        <addAttributes>
            <att name="long_name">date of deployment</att>

            <att name="calendar">gregorian</att>
            <att name="units">seconds since 1970-01-01T00:00:00Z</att>
        </addAttributes>

        </dataVariable>

        """
        start_date =self.deployment_meta["deployment_date"]
        if start_date:
            self.add_new_variable("={}".format(datetime.timestamp(start_date)), "DEPLOYMENT_TIME", "double", {
                "long_name": "date of deployment",
                "calendar": "gregorian",
                "units": "seconds since 1970-01-01T00:00:00Z"
            })

    def add_deployment_variable(self):
        """
        reference: https://oceangliderscommunity.github.io/OG-format-user-manual/
        deployment time
        <dataVariable>

        <sourceName>={the deployment timestamp}</sourceName>

        <destinationName>DEPLOYMENT_TIME</destinationName>

        <dataType>double</dataType>


        <addAttributes>
            <att name="long_name">date of deployment</att>

            <att name="calendar">gregorian</att>
            <att name="units">seconds since 1970-01-01T00:00:00Z</att>
        </addAttributes>

    </dataVariable>



        """
        self.add_deployment_time()

    def add_vmo_identifier(self):
        """
        reference: https://oceangliderscommunity.github.io/OG-format-user-manual/
            <dataVariable>

        <sourceName>="123"</sourceName>

        <destinationName>WMO_IDENTIFIER</destinationName>

        <dataType>String</dataType>


        <addAttributes>
            <att name="long_name">wmo id</att>
        </addAttributes>

    </dataVariable>
        """
        if "wmo_id" in self.deployment_meta and self.deployment_meta["wmo_id"]:
            self.add_new_variable("={}".format(self.deployment_meta["wmo_id"]), "WMO_IDENTIFIER", "String", {
                "long_name": "wmo id"
            })

    def add_trajectory(self):
        """
        reference: https://oceangliderscommunity.github.io/OG-format-user-manual/
        Erddap trajectory Example
        <dataVariable>

        <sourceName>="<platform_name>_<start_date>"</sourceName>

        <destinationName>trajectory</destinationName>

        <dataType>String</dataType>


        <addAttributes>
            <att name="long_name">trajectory name</att>
            <att name="cf_role">trajectory_id</att>
            <att name="data_mode_vocabulary ">""</att>
            <att name="_ChunkSizes">null</att>

        </addAttributes>
        """
        platform_name, start_date = self.deployment_meta["platform_name"], self.deployment_meta["deployment_date"]
        if platform_name and start_date:
            trajectory = "{}_{}".format(platform_name, start_date.strftime("%Y-%m-%d"))
        else:
            trajectory = self.datasets_id
        self.add_new_variable("=\"{}\"".format(trajectory), "trajectory", "String", {
            "long_name": "trajectory name",
            "cf_role": "trajectory_id"
        })

    def add_platform_variable(self):
        """
        <dataVariable>

        <sourceName>="example model"</sourceName>

        <destinationName>PLATFORM_MODEL</destinationName>

        <dataType>String</dataType>


        <addAttributes>
            <att name="long_name">model of the glider</att>
            <att name="platform_model_vocabulary">""</att>
        </addAttributes>

        </dataVariable>
        """
        ...

    def apply_attributes(self):
        self.add_trajectory()
        self.add_platform_variable()
        self.add_deployment_variable()
        self.add_vmo_identifier()

    def apply_og_standards(self):
        self.apply_global_variables()
        self.apply_attributes()
        self.add_data_url()

    def apply_convention_standards(self):
        self.apply_og_standards()

    # def add_deployment_latitude(self):
    #     """
    #     reference: https://oceangliderscommunity.github.io/OG-format-user-manual/
    #     """
    #     ...
    #
    # def add_deployment_longitude(self):
    #     """
    #     reference: https://oceangliderscommunity.github.io/OG-format-user-manual/
    #     """
    #     ...

    def add_data_url(self):
        """
         reference: https://oceangliderscommunity.github.io/OG-format-user-manual/
         data_url
        url link to OG1.0 data file
        mandatory
         """
        ...

    def review_latitude(self):
        ...

    def review_longitude(self):
        ...
