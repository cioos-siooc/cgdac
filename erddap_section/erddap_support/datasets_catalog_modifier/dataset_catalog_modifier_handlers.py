from erddap_section.erddap_support.datasets_catalog_modifier.errdap_dataset_configuration_helper import ERDDAPDatasetXMLEditor


class ErddapGliderDatasetXmlRefiner(ERDDAPDatasetXMLEditor):
    """
    The output of the GenerateDatasetsXml is draft
    we need to edit the output to make it better

    quote from erddap docs
    DISCLAIMER:
    THE CHUNK OF datasets.xml MADE BE GenerateDatasetsXml
    ISN'T PERFECT. YOU MUST READ AND EDIT THE XML BEFORE
    USING IT IN A PUBLIC ERDDAP. GenerateDatasetsXml RELIES
    ON A LOT OF RULES-OF-THUMB WHICH AREN'T ALWAYS CORRECT.
    YOU ARE RESPONSIBLE FOR ENSURING THE CORRECTNESS OF THE
    XML THAT YOU ADD TO ERDDAP'S datasets.xml FILE.
    """

    def __init__(self, xml_str,
                 dataset_id,
                 remote_nc_folder_path,
                 erddap_dataset_title,
                 output_path):
        super().__init__(xml_str)
        self.datasets_id = dataset_id
        self.remote_nc_folder_path = remote_nc_folder_path
        self.erddap_dataset_title = erddap_dataset_title
        self.output_path = output_path

    def refine(self):
        self._alter_header(self.datasets_id)
        self._alter_attr()
        self._alter_added_attr()
        self.write(self.output_path)

    def _alter_header(self, dataset_id):
        self.set_header("datasetID", dataset_id)

    def _alter_attr(self):
        # Since pipeline would trigger the Hard Flag file, reload min was set very high.
        # 40320 mins is 28 days
        self.set_erddap_config("reloadEveryNMinutes", 40320)
        # set the updateEveryNMillis as 0, means turn off the this feature
        self.set_erddap_config("updateEveryNMillis", 0)
        # we want user can view the nc files as well
        self.set_erddap_config("accessibleViaFiles", 'True')
        target_nc = self.remote_nc_folder_path
        self.set_erddap_config("fileDir", target_nc)
        # ERDDAP doc: remove since those feature was deprecated
        # Adding try catch for now
        try:
            self.remove_dataset_config('preExtractRegex')
        except TypeError:
            pass
        try:
            self.remove_dataset_config('postExtractRegex')
        except TypeError:
            pass
        try:
            self.remove_dataset_config('extractRegex')
        except TypeError:
            pass
        try:
            self.remove_dataset_config('columnNameForExtract')
        except TypeError:
            pass

    def _alter_added_attr(self):
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
        self.set_added_global_variable('cdm_profile_variables', 'profile_id, time, latitude, longitude')
        self.set_added_global_variable('cdm_trajectory_variables', 'trajectory')
        self.set_added_global_variable('Metadata_Conventions', 'CF-1.6, COARDS, ACDD-1.3')
        self.set_added_global_variable('title', self.erddap_dataset_title)
        self.remove_global_variable('testOutOfDate')
        self.remove_global_variable('subsetVariables')
        try:
            # Hide the source file from ERRDAP meta page
            self.set_added_global_variable('source_file', "null")
        except TypeError:
            pass