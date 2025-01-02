from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field


@dataclass
class DatabaseConnectionProperty:
    """
    here is the example for dataset xml which contain the connectionProperty
    <dataset type="EDDTableFromDatabase" datasetID="seacycler_level2_seacycler_aquadopp_upcast" active="true">
    <sourceUrl>jdbc:postgresql://cercos.ocean.dal.ca/seacycler</sourceUrl>
    <driverName>org.postgresql.Driver</driverName>
    <connectionProperty name="host">host_name</connectionProperty>
    <connectionProperty name="database">host_database</connectionProperty>
    <connectionProperty name="user">host_user</connectionProperty>
    <connectionProperty name="password">host_password</connectionProperty>
    <catalogName>seacycler</catalogName>
    <schemaName>level2</schemaName>
    <tableName>seacycler_aquadopp_upcast</tableName>
    <orderBy>timestamp</orderBy>
    <reloadEveryNMinutes>2880</reloadEveryNMinutes>
    """
    host: str
    database: str
    user: str
    password: str


@dataclass
class UpdateMessage:
    joined: bool
    failed_reason: str


@dataclass
class UpdateMessages:
    """
    This data is for pass the information out of module
    """
    update_list = Dict[str, UpdateMessage]


@dataclass
class Config:
    """
    This is generated from the defaultERDDAP dataset header
    A ERDDAP dataset example is
    <!-- GENERAL INFORMATION
    The information in this file specifies which datasets your ERDDAP will serve.
    The initial version of this file has a few examples which should work for you.
    But after your initial experiments with ERDDAP,
    you should replace them with information for your datasets.

    You can change this document (e.g., add datasets, change metadata) while ERDDAP is running.
    The changes will be detected the next time this document is read
    (as often as loadDatasetsMinMinutes).

    Each dataset has a reloadEveryNMinutes value (default = 10080 (one week)).
    When this document is reread, datasets that haven't been been reloaded in
    their reloadEveryNMinutes will be reloaded.
    You only need to specify a reloadEveryNMinutes value if you anticipate that
    the dataset will change periodically.

    If this document has an xml error, processing will stop and an email
    will be sent to emailEverythingTo as specified in setup.xml.

    If you want to remove a dataset while ERDDAP is running, add
        active="false"
    to the dataset tag.  For example,
        <dataset type="EDDGridFromDap" datasetID="erdMHchla8day" active="false">

    For more information, see
    https://coastwatch.pfel.noaa.gov/erddap/download/setupDatasetsXml.html
    -->

    <!-- The tags below are described in setupDatasetsXml.html.
         The defaults listed below are as of ERDDAP v2.00. -->
    <cacheMinutes></cacheMinutes>                                     <!-- default=60 -->
    <decompressedCacheMaxGB></decompressedCacheMaxGB>                 <!-- default=10 -->
    <decompressedCacheMaxMinutesOld></decompressedCacheMaxMinutesOld> <!-- default=15 -->
    <drawLandMask></drawLandMask>                                     <!-- "over", "under" (default), "outline", or "off" -->
    <emailDiagnosticsToErdData></emailDiagnosticsToErdData>           <!-- "true (default) or "false" -->
    <graphBackgroundColor></graphBackgroundColor>                     <!-- 0xAARRGGBB, default is 0xffccccff -->
    <ipAddressMaxRequests></ipAddressMaxRequests>                     <!-- current default=7 -->
    <ipAddressMaxRequestsActive></ipAddressMaxRequestsActive>         <!-- current default=2 -->
    <ipAddressUnlimited></ipAddressUnlimited>                         <!-- default=(empty) -->
    <loadDatasetsMinMinutes></loadDatasetsMinMinutes>                 <!-- usually=default=15 -->
    <loadDatasetsMaxMinutes></loadDatasetsMaxMinutes>                 <!-- default=60 -->
    <logLevel></logLevel> <!-- "warning" (fewest messages), "info" (default), or "all" (most messages) -->
    <nGridThreads></nGridThreads>                                     <!-- default=1 -->
    <nTableThreads></nTableThreads>                                   <!-- default=1 -->
    <partialRequestMaxBytes></partialRequestMaxBytes>                 <!-- default=490000000 -->
    <partialRequestMaxCells></partialRequestMaxCells>                 <!-- default=10000000 -->
    <slowDownTroubleMillis></slowDownTroubleMillis>                   <!-- default=1000 -->
    <unusualActivity></unusualActivity>                               <!-- default=10000 -->
    <updateMaxEvents></updateMaxEvents>                               <!-- default=10 -->
    <!-- The defaults for the following tags are in messages.xml. -->
    <startHeadHtml5></startHeadHtml5>
    <endBodyHtml5></endBodyHtml5>
    <standardLicense></standardLicense>
    <standardContact></standardContact>
    <standardDataLicenses></standardDataLicenses>
    <standardDisclaimerOfEndorsement></standardDisclaimerOfEndorsement>
    <standardDisclaimerOfExternalLinks></standardDisclaimerOfExternalLinks>
    <standardGeneralDisclaimer></standardGeneralDisclaimer>

    <standardPrivacyPolicy><![CDATA[
    <br>&nbsp;
    <hr>
    <h2><a class="selfLink" id="privacyPolicy" href="#privacyPolicy" rel="help">Privacy Policy</a></h2>
    ERDDAP follows
    <a rel="bookmark" href="https://www.noaa.gov/protecting-your-privacy"
      >NOAA's Privacy Policy Guidelines</a>.
    ]]></standardPrivacyPolicy>

    <startBodyHtml5><![CDATA[
    <body>
    <table class="compact nowrap" style="width:100%; background-color:#128CB5;">
      <tr>
        <td style="text-align:center; width:80px;"><a rel="bookmark"
          href="https://www.noaa.gov/"><img
          title="National Oceanic and Atmospheric Administration"
          src="&erddapUrl;/images/noaab.png" alt="NOAA"
          style="vertical-align:middle;"></a></td>
        <td style="text-align:left; font-size:x-large; color:#FFFFFF; ">
          <strong>ERDDAP</strong>
          <br><small><small><small>&EasierAccessToScientificData;</small></small></small>
          </td>
        <td style="text-align:right; font-size:small;">
          &loginInfo; | &language; &nbsp; &nbsp;
          <br>&BroughtToYouBy;
          <a title="National Oceanic and Atmospheric Administration" rel="bookmark"
          href="https://www.noaa.gov">NOAA</a>
          <a title="National Marine Fisheries Service" rel="bookmark"
          href="https://www.fisheries.noaa.gov">NMFS</a>
          <a title="Southwest Fisheries Science Center" rel="bookmark"
          href="https://www.fisheries.noaa.gov/about/southwest-fisheries-science-center">SWFSC</a>
          <a title="Environmental Research Division" rel="bookmark"
          href="https://www.fisheries.noaa.gov/about/environmental-research-division-southwest-fisheries-science-center">ERD</a>
          &nbsp; &nbsp;
          </td>
      </tr>
    </table>
    ]]></startBodyHtml5>

    <theShortDescriptionHtml><![CDATA[
    <h1>ERDDAP</h1>
    &erddapIs;
    &thisParticularErddap;
    [standardShortDescriptionHtml]
    ]]></theShortDescriptionHtml>


    <!-- If you want to refuse requests from certain clients
      (e.g., to fend off a Denial of Service attack or an overly zealous web robot),
      add their numeric IP address (e.g., 123.45.67.89) to this comma-separated list.
      You can also replace the last number in an IP address with * to block 0-255 (e.g., 123.45.67.*).
      See your ERDDAP daily report for a list/tally of the most active requesters. -->
    <requestBlacklist></requestBlacklist>


    <!-- If you want to prevent specific people from using the email/URL subscription
         system, add their email addresses to this comma-separated list.
         You can use the name "*" to blacklist an entire domain, e.g., *@example.com .
    -->
    <subscriptionEmailBlacklist>your.email@yourinstitution.edu, some.name@company.com,
    another.name@company.com, *@example.com</subscriptionEmailBlacklist>

    """


    cacheMinutes: Optional[int] = field(default=60)
    decompressedCacheMaxGB: Optional[int] = field(default=10)
    decompressedCacheMaxMinutesOld: Optional[int] = field(default=15)
    drawLandMask: Optional[str] = field(default="under")  # Can be "over", "under", "outline", or "off"
    emailDiagnosticsToErdData: Optional[bool] = field(default=True)  # "true" or "false"
    graphBackgroundColor: Optional[str] = field(default="0xffccccff")  # 0xAARRGGBB
    ipAddressMaxRequests: Optional[int] = field(default=7)
    ipAddressMaxRequestsActive: Optional[int] = field(default=2)
    ipAddressUnlimited: Optional[str] = field(default="")  # Default is empty
    loadDatasetsMinMinutes: Optional[int] = field(default=15)
    loadDatasetsMaxMinutes: Optional[int] = field(default=60)
    logLevel: Optional[str] = field(default="info")  # "warning", "info", or "all"
    nGridThreads: Optional[int] = field(default=1)
    nTableThreads: Optional[int] = field(default=1)
    partialRequestMaxBytes: Optional[int] = field(default=490000000)
    partialRequestMaxCells: Optional[int] = field(default=10000000)
    slowDownTroubleMillis: Optional[int] = field(default=1000)
    unusualActivity: Optional[int] = field(default=10000)
    updateMaxEvents: Optional[int] = field(default=10)

    standardPrivacyPolicyPath: Optional[str] = field(default="")
    startBodyHtml5Path: Optional[str] = field(default="")
    theShortDescriptionHtmlPath: Optional[str] = field(default="")
    requestBlacklist: Optional[List[str]] = field(default_factory=list)  # List of blacklisted requests
    subscriptionEmailBlacklist: Optional[List[str]] = field(default_factory=list)  # List of blacklisted emails

    # Fields with default values in another configuration (e.g., messages.xml)
    startHeadHtml5: Optional[str] = field(default="")
    endBodyHtml5: Optional[str] = field(default="")
    standardLicense: Optional[str] = field(default="")
    standardContact: Optional[str] = field(default="")
    standardDataLicenses: Optional[str] = field(default="")
    standardDisclaimerOfEndorsement: Optional[str] = field(default="")
    standardDisclaimerOfExternalLinks: Optional[str] = field(default="")
    standardGeneralDisclaimer: Optional[str] = field(default="")


@dataclass
class ErddapData:
    """
        A data class used to pass dataset-related information to the module responsible for
        generating ERDDAP headers and configuring datasets.

        Attributes:
            deactivate_list (List[Dict[str, Any]]):
                A list of dataset IDs to be included in the joined datasets XML file.
                Example:
                ['seacycler_level2_seacycler_aquadopp_upcast', 'otn201_20150123_43_delayed']

            datasets_connection_properties (Dict[str, DatabaseConnectionProperty]):
                A dictionary where keys are dataset IDs, and values are
                DatabaseConnectionProperty objects that define connection
                properties for the datasets.

            dataset_config (Config):
                The configuration for variables in the dataset header, specifying
                ERDDAP behavior and appearance for the datasets.
        """
    deactivate_list: List[Dict[str, Any]] = field(default_factory=list)
    datasets_connection_properties: Dict[str, DatabaseConnectionProperty] = field(default_factory=dict)
    dataset_config: Config = field(default_factory=Config)

    def to_dict(self) -> Dict[str, Any]:
        """
        Converts the DatasetsData instance to a dictionary.
        """
        from dataclasses import asdict
        return asdict(self)