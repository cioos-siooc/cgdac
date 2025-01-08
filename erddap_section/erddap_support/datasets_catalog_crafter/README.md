# README.md

## Overview

This project includes a Django management command to join multiple XML dataset configuration files into a single file. The command reads from a configuration file, validates and formats the XML files, and ensures uniqueness of dataset IDs. The resulting file can then be used in ERDDAP or other similar systems.

---

## User Guide



This module is designed to streamline the process of handling XML files from a specified directory structure. It works by:

	1.	Finding the paths for both individuals_datasets and output_dir.
	2.	Reading all XML files located under individuals_datasets and its subfolders.
	3.	Generating an output file named datasets.xml in the output_dir.
	4.	Creating a backup of the previous datasets.xml every time a new one is generated, storing it in the same directory.

Additionally, the module prepares an instance of the DatasetsData class, which represents the data structure for the XML content.
You can leave the relevant field empty to use the default configuration for datasets generation. For more details on DatasetsData,
refer to the datasets_structure.py file.


Usage
```plaintext
Root
│
├── DatasetsCatalogCrafter   # Module files and scripts
│
├── individuals_datasets     # XML files and subfolders containing individual datasets
│
├── output                   # Directory where datasets.xml and its backups will be generated
│
└── test_crafter.py          # Script for testing the functionality of the module
```

Assuming you are working on test_crafter.py file

```python
from DatasetsCatalogCrafter import DatasetsCrafter, ErddapData

individuals_datasets_folder_path = "individuals_datasets"
output_dir = "output"
datasets_data = ErddapData()  # Empty for the default ERDDAP
datasets_crafter = DatasetsCrafter(individuals_datasets_folder_path, output_dir, datasets_data)
datasets_crafter.build()
```

To generate a datasets which contain customize apperance, please provide

for example, give the html file. body.html

```plaintext
Root
│
├── datasetsCatalogCrafter   # Module files and scripts
│
├── individuals_datasets     # XML files and subfolders containing individual datasets
│
├── output                   # Directory where datasets.xml and its backups will be generated
│
├── resource                 # Contains additional resources for the module
│   └── body.html            # HTML template or content used by the module
│
└── test_crafter.py          # Script for testing the functionality of the module
```

```html
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
      <a title="CEOTR" rel="bookmark"
      href="https://www.ceotr.ca">NOAA</a>
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
```


```python
datasets_data.startBodyHtml5Path = 'resource/body.html' # setup customize EEDDAP body
datasets_crafter = DatasetsCrafter(individuals_datasets, output_dir, datasets_data)
datasets_crafter.build()
```

Select dataset to join

by default the crafter will join all of individuals datasets xml, but you can provide a list of dataset ids which
you don't want to be join in datasets.xml

```python
datasets_data.deactivate_list = ["otn201_20150123_43_delayed", "seacycler_level2_seacycler_aquadopp_upcast"] # The dataset ids list that you don't want to be showing on ERDDAP
datasets_crafter = DatasetsCrafter(individuals_datasets, output_dir, datasets_data)
datasets_crafter.build()
```

For datasetswe don't want credentail exist in it, so the crafter also provide function that can insert the in the credentail during the join

```python
datasets_data.datasets_connection_property = { 
    "seacycler_level2_seacycler_aquadopp_upcast": {
       "host": "the_host",
       "user": "the_user",
       "database": "database_name",
       "password": "password"
    }
}# The dataset ids list that you don't want to be showing on ERDDAP
datasets_crafter = DatasetsCrafter(individuals_datasets, output_dir, datasets_data)
datasets_crafter.build()
```

