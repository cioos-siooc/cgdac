"""
scripts/build_erddap_catalog.py

This module generates dataset "chunks" for gliderDAC deployments and
concatenates them into a single datasets.default.xml file for ERDDAP. This
script is run on a schedule to help keep the gliderDAC datasets in
sync with newly registered (or deleted) deployments

Details:
Only generates a new dataset chunk if the dataset has been updated since
the last time the script ran. The chunk is saved as dataset.xml in the
deployment directory.

Use the -f CLI argument to create a dataset.xml chunk for ALL the datasets

Optionally add/update metadata to a dataset by supplying a json file named extra_atts.json
to the deployment directory.

An example of extra_atts.json file which modifies the history global
attribute and the depth variable's units attribute is below

{
    "_global_attrs": {
        "history": "updated units"
    },
    "depth": {
        "units": "m"
    }
}
"""
