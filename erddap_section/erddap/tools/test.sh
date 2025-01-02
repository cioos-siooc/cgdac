#!/bin/bash

export DOCKER_ENV=".test.env"

test_script_name="GenerateDatasetsXML.sh"

current_dir="$(dirname "$0")"

testing_str="EDDTableFromNcFiles /datasets/dataset1 nothing nothing nothing nothing nothing nothing nothing nothing nothing nothing nothing nothing nothing nothing nothing nothing"


bash "$current_dir/$test_script_name" "$testing_str"

if head -n 1 "$current_dir/test_resource/bigParents/logs/GenerateDatasetsXml.out" | grep -q "dataset1"; then
    echo "Keyword found in the first line."
fi


testing_str="EDDTableFromNcFiles /datasets/dataset2 nothing nothing nothing nothing nothing nothing nothing nothing nothing nothing nothing nothing nothing nothing nothing nothing"


bash "$current_dir/$test_script_name" "$testing_str"

if head -n 1 "$current_dir/test_resource/bigParents/logs/GenerateDatasetsXml.out" | grep -q "dataset2"; then
    echo "Keyword found in the first line."
fi