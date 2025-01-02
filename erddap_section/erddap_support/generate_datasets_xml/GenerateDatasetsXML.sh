#!/bin/bash
set -m
# Use the value of DOCKER_ENV if it's set; otherwise, use the default ../../../.env
ENV_FILE="${DOCKER_ENV:-../../.env}"


source $ENV_FILE

str_data="$*"
echo "$str_data"


# Run the Docker command with the collected parameters
docker run --rm -it \
  -v "$ERDDAP_DATASET:/datasets" \
  -v "$ERDDAP_ERDDAP_DATA/logs:/erddapData/logs" \
  -e "ERDDAP_flagKeyKey=randon_value_just_making_erddap_happy" \
  axiom/docker-erddap:$DOCKER_VERSION \
  bash -c "cd webapps/erddap/WEB-INF/ && bash GenerateDatasetsXml.sh $str_data"